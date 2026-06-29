import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from loguru import logger
import os
import asyncio
from functools import lru_cache
from datetime import datetime, timedelta

from config import settings

# 设置 HuggingFace 镜像（解决国内网络问题）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 禁用 ChromaDB 遥测
os.environ['ANONYMIZED_TELEMETRY'] = 'False'


class KnowledgeService:
    def __init__(self):
        self.client = None
        self.embedder = None
        self.collection = None
        self._initialized = False
        # 查询缓存
        self._query_cache = {}
        self._cache_ttl = 300  # 缓存5分钟
        logger.info("Knowledge service created (will initialize asynchronously)")
    
    async def initialize(self):
        """异步初始化（避免阻塞事件循环）"""
        if self._initialized:
            return
        
        try:
            # 在线程池中执行同步初始化
            loop = asyncio.get_event_loop()
            
            # 初始化 ChromaDB
            self.client = await loop.run_in_executor(
                None,
                lambda: chromadb.PersistentClient(
                    path=settings.chroma_persist_dir,
                    settings=Settings(anonymized_telemetry=False)
                )
            )
            
            # 初始化嵌入模型（使用镜像或本地缓存）
            logger.info("Loading sentence-transformers model...")
            logger.info("Using HuggingFace mirror: https://hf-mirror.com")
            
            try:
                self.embedder = await loop.run_in_executor(
                    None,
                    lambda: SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                )
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {str(e)}")
                logger.error("Possible solutions:")
                logger.error("  1. Check network connection")
                logger.error("  2. Use VPN or proxy")
                logger.error("  3. Download model manually:")
                logger.error("     Visit: https://hf-mirror.com/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
                logger.error("     Download to: ~/.cache/huggingface/hub/")
                raise
            
            # 获取或创建集合
            self.collection = await loop.run_in_executor(
                None,
                lambda: self.client.get_or_create_collection(
                    name=settings.chroma_collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            )
            
            self._initialized = True
            logger.info(f"Knowledge service initialized with collection: {settings.chroma_collection_name}")
        except Exception as e:
            logger.error(f"Error initializing knowledge service: {str(e)}")
            raise
    
    async def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            await self.initialize()
    
    async def _embed_text(self, text: str) -> List[float]:
        """将文本转换为向量（异步）"""
        await self._ensure_initialized()
        
        # 检查缓存
        cache_key = f"embed:{text}"
        if cache_key in self._query_cache:
            cached_data, timestamp = self._query_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                return cached_data
        
        # 在线程池中执行同步嵌入计算
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.embedder.encode(text).tolist()
        )
        
        # 缓存结果
        self._query_cache[cache_key] = (embedding, datetime.now())
        return embedding
    
    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> dict:
        """添加文档到知识库"""
        await self._ensure_initialized()
        
        try:
            # 批量生成嵌入（异步）
            embeddings = []
            for doc in documents:
                embedding = await self._embed_text(doc)
                embeddings.append(embedding)
            
            # 生成 ID（如果未提供）
            if ids is None:
                ids = [f"doc_{i}_{hash(doc) % 1000000}" for i, doc in enumerate(documents)]
            
            # 在线程池中执行添加操作
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            )
            
            logger.info(f"Added {len(documents)} documents to knowledge base")
            return {"status": "success", "added_count": len(documents)}
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[dict] = None
    ) -> str:
        """搜索相关文档"""
        await self._ensure_initialized()
        
        # 检查缓存
        cache_key = f"search:{query}:{top_k}:{where}"
        if cache_key in self._query_cache:
            cached_data, timestamp = self._query_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                return cached_data
        
        try:
            # 生成查询向量（异步）
            query_embedding = await self._embed_text(query)
            
            # 在线程池中执行搜索
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where
                )
            )
            
            # 格式化结果
            result_text = ""
            if results['documents'] and results['documents'][0]:
                context_parts = []
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    source = metadata.get('source', 'unknown')
                    context_parts.append(f"[来源: {source}]\n{doc}")
                
                result_text = "\n\n---\n\n".join(context_parts)
            
            # 缓存结果
            self._query_cache[cache_key] = (result_text, datetime.now())
            return result_text
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return ""
    
    async def delete_documents(self, ids: List[str]) -> dict:
        """删除文档"""
        await self._ensure_initialized()
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.collection.delete(ids=ids)
            )
            
            # 清除缓存
            self._query_cache.clear()
            
            logger.info(f"Deleted {len(ids)} documents from knowledge base")
            return {"status": "success", "deleted_count": len(ids)}
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    async def get_collection_info(self) -> dict:
        """获取集合信息"""
        await self._ensure_initialized()
        
        try:
            loop = asyncio.get_event_loop()
            count = await loop.run_in_executor(
                None,
                lambda: self.collection.count()
            )
            return {
                "name": settings.chroma_collection_name,
                "count": count,
                "persist_dir": settings.chroma_persist_dir
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            raise


knowledge_service = KnowledgeService()
