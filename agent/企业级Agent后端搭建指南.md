# 企业级 Agent 后端搭建指南

从零开始搭建支持知识库、MCP 和流式响应的企业级 Python Agent 服务

## 目录

1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [环境准备](#环境准备)
4. [项目结构](#项目结构)
5. [核心实现](#核心实现)
6. [知识库集成](#知识库集成)
7. [MCP 集成](#mcp-集成)
8. [流式响应](#流式响应)
9. [部署指南](#部署指南)
10. [最佳实践](#最佳实践)

---

## 项目概述

本指南将帮助你搭建一个企业级 Agent 后端服务，具备以下特性：

- **第三方模型集成**：支持 OpenAI、Anthropic、Azure OpenAI 等多种模型
- **知识库支持**：集成向量数据库，支持企业私有知识库
- **MCP 协议支持**：兼容 Model Context Protocol，扩展 Agent 能力
- **流式响应**：支持 SSE 流式输出，提升用户体验
- **企业级特性**：认证、日志、监控、错误处理

---

## 技术架构

### 技术栈

```
后端框架: FastAPI
异步运行时: asyncio + uvicorn
向量数据库: ChromaDB / Qdrant / PGVector
LLM 集成: LangChain / LlamaIndex
MCP 客户端: MCP SDK
认证: JWT + OAuth2
日志: loguru
监控: Prometheus + Grafana
```

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    前端应用 (Web/Mobile)                 │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/SSE
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  API Gateway (Nginx/Kong)               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI 后端服务                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  认证中间件   │  │  路由处理    │  │  流式响应    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Agent 核心   │  │  知识库检索  │  │  MCP 客户端   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 向量数据库    │ │ 第三方 LLM   │ │ MCP 服务     │
│ (ChromaDB)   │ │ (OpenAI等)   │ │ (外部工具)   │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 环境准备

### 1. Python 环境安装

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 2. 安装依赖

创建 `requirements.txt`：

```txt
# Web 框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# 异步支持
httpx==0.25.2
aiohttp==3.9.1

# LLM 集成
langchain==0.1.0
langchain-openai==0.0.2
langchain-community==0.0.10
openai==1.6.1

# 向量数据库
chromadb==0.4.22
sentence-transformers==2.2.2

# MCP 支持
mcp==0.1.0

# 认证
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# 工具库
loguru==0.7.2
python-dotenv==1.0.0
tenacity==8.2.3

# 监控
prometheus-client==0.19.0
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 3. 环境变量配置

创建 `.env` 文件：

```env
# 应用配置
APP_NAME=Enterprise Agent Backend
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# LLM 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2000

# 向量数据库配置
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=enterprise_knowledge

# 认证配置
SECRET_KEY=your_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MCP 配置
MCP_SERVER_URL=http://localhost:3000
MCP_TIMEOUT=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## 项目结构

```
enterprise-agent-backend/
├── .env                          # 环境变量
├── requirements.txt              # Python 依赖
├── README.md                     # 项目说明
├── main.py                       # 应用入口
├── config.py                     # 配置管理
├── app/
│   ├── __init__.py
│   ├── api/                      # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py               # 认证相关
│   │   ├── chat.py               # 聊天接口
│   │   └── knowledge.py          # 知识库管理
│   ├── core/                     # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── agent.py              # Agent 核心逻辑
│   │   ├── llm.py                # LLM 封装
│   │   └── streaming.py          # 流式响应处理
│   ├── services/                 # 服务层
│   │   ├── __init__.py
│   │   ├── knowledge_service.py  # 知识库服务
│   │   ├── mcp_service.py        # MCP 服务
│   │   └── auth_service.py       # 认证服务
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── chat.py               # 聊天相关模型
│   │   └── user.py               # 用户相关模型
│   ├── middleware/               # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py               # 认证中间件
│   │   └── logging.py            # 日志中间件
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── logger.py             # 日志工具
│       └── helpers.py            # 辅助函数
├── data/                         # 数据目录
│   └── chroma/                   # 向量数据库数据
├── logs/                         # 日志目录
└── tests/                        # 测试目录
    ├── __init__.py
    └── test_api.py
```

---

## 核心实现

### 1. 配置管理 (config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "Enterprise Agent Backend"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM 配置
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    default_model: str = "gpt-4"
    default_temperature: float = 0.7
    max_tokens: int = 2000
    
    # 向量数据库配置
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "enterprise_knowledge"
    
    # 认证配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # MCP 配置
    mcp_server_url: Optional[str] = None
    mcp_timeout: int = 30
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

### 2. 应用入口 (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.api import chat, knowledge, auth
from app.middleware.logging import LoggingMiddleware
from app.middleware.auth import AuthMiddleware
from app.utils.logger import setup_logger
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # 关闭时执行
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境需要限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 自定义中间件
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # 注册路由
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天"])
    app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app_version}
    
    return app


if __name__ == "__main__":
    setup_logger()
    app = create_app()
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
```

### 3. 日志工具 (app/utils/logger.py)

```python
from loguru import logger
import sys
from config import settings


def setup_logger():
    """配置日志系统"""
    logger.remove()  # 移除默认处理器
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="500 MB",
        retention="10 days",
        compression="zip"
    )
```

### 4. LLM 封装 (app/core/llm.py)

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, AsyncIterator, Optional
from config import settings
import json


class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.default_model,
            temperature=settings.default_temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url,
            streaming=True
        )
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """同步聊天"""
        langchain_messages = []
        
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        response = await self.llm.ainvoke(langchain_messages)
        return response.content
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天"""
        langchain_messages = []
        
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        async for chunk in self.llm.astream(langchain_messages):
            if chunk.content:
                yield chunk.content


llm_service = LLMService()
```

### 5. Agent 核心逻辑 (app/core/agent.py)

```python
from typing import List, Dict, AsyncIterator, Optional
from app.core.llm import llm_service
from app.services.knowledge_service import knowledge_service
from app.services.mcp_service import mcp_service
from loguru import logger


class Agent:
    def __init__(self):
        self.system_prompt = """你是一个企业级智能助手，具有以下能力：
1. 可以回答用户的各种问题
2. 可以检索企业知识库获取相关信息
3. 可以调用外部工具（通过 MCP）执行任务

请以专业、准确、友好的方式回答用户问题。如果不确定答案，请诚实地说明。"""
    
    async def process(
        self,
        messages: List[Dict[str, str]],
        use_knowledge: bool = True,
        use_mcp: bool = True,
        user_id: Optional[str] = None
    ) -> str:
        """处理用户消息（非流式）"""
        # 获取最新用户消息
        user_message = messages[-1]["content"] if messages else ""
        
        # 知识库检索
        context = ""
        if use_knowledge and user_message:
            context = await knowledge_service.search(user_message, top_k=3)
            if context:
                logger.info(f"Retrieved knowledge context for user {user_id}")
        
        # 构建增强的系统提示
        enhanced_system = self.system_prompt
        if context:
            enhanced_system += f"\n\n相关知识库内容：\n{context}"
        
        # 调用 LLM
        response = await llm_service.chat(
            messages=messages,
            system_prompt=enhanced_system
        )
        
        return response
    
    async def process_stream(
        self,
        messages: List[Dict[str, str]],
        use_knowledge: bool = True,
        use_mcp: bool = True,
        user_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """处理用户消息（流式）"""
        # 获取最新用户消息
        user_message = messages[-1]["content"] if messages else ""
        
        # 知识库检索
        context = ""
        if use_knowledge and user_message:
            context = await knowledge_service.search(user_message, top_k=3)
            if context:
                logger.info(f"Retrieved knowledge context for user {user_id}")
        
        # 构建增强的系统提示
        enhanced_system = self.system_prompt
        if context:
            enhanced_system += f"\n\n相关知识库内容：\n{context}"
        
        # 流式调用 LLM
        async for chunk in llm_service.chat_stream(
            messages=messages,
            system_prompt=enhanced_system
        ):
            yield chunk


agent = Agent()
```

### 6. 数据模型 (app/models/chat.py)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Message(BaseModel):
    role: str = Field(..., description="消息角色：user/assistant/system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="对话历史")
    stream: bool = Field(default=True, description="是否使用流式响应")
    use_knowledge: bool = Field(default=True, description="是否使用知识库")
    use_mcp: bool = Field(default=True, description="是否使用 MCP 工具")
    temperature: Optional[float] = Field(default=None, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")


class ChatResponse(BaseModel):
    content: str = Field(..., description="回复内容")
    model: str = Field(..., description="使用的模型")
    usage: Optional[Dict] = Field(default=None, description="token 使用情况")
```

### 7. 聊天 API (app/api/chat.py)

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import uuid

from app.models.chat import ChatRequest, ChatResponse
from app.core.agent import agent
from app.core.streaming import stream_formatter
from loguru import logger

router = APIRouter()


@router.post("/completions")
async def chat_completion(request: ChatRequest):
    """聊天完成接口（非流式）"""
    try:
        messages_dict = [msg.dict() for msg in request.messages]
        
        response = await agent.process(
            messages=messages_dict,
            use_knowledge=request.use_knowledge,
            use_mcp=request.use_mcp
        )
        
        return ChatResponse(
            content=response,
            model="gpt-4"
        )
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completions/stream")
async def chat_completion_stream(request: ChatRequest):
    """聊天完成接口（流式）"""
    try:
        messages_dict = [msg.dict() for msg in request.messages]
        
        async def generate() -> AsyncGenerator[str, None]:
            request_id = str(uuid.uuid4())
            
            # 发送开始事件
            yield stream_formatter({
                "type": "start",
                "request_id": request_id,
                "model": "gpt-4"
            })
            
            # 流式生成内容
            full_content = ""
            async for chunk in agent.process_stream(
                messages=messages_dict,
                use_knowledge=request.use_knowledge,
                use_mcp=request.use_mcp
            ):
                full_content += chunk
                yield stream_formatter({
                    "type": "content",
                    "content": chunk,
                    "request_id": request_id
                })
            
            # 发送结束事件
            yield stream_formatter({
                "type": "end",
                "request_id": request_id,
                "usage": {
                    "total_tokens": len(full_content)
                }
            })
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"Chat stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 8. 流式响应处理 (app/core/streaming.py)

```python
import json


def stream_formatter(data: dict) -> str:
    """格式化 SSE 流式响应"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
```

---

## 知识库集成

### 1. 知识库服务 (app/services/knowledge_service.py)

```python
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from loguru import logger
import os

from config import settings


class KnowledgeService:
    def __init__(self):
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 初始化嵌入模型
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Knowledge service initialized with collection: {settings.chroma_collection_name}")
    
    def _embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        return self.embedder.encode(text).tolist()
    
    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> dict:
        """添加文档到知识库"""
        try:
            # 批量生成嵌入
            embeddings = [self._embed_text(doc) for doc in documents]
            
            # 生成 ID（如果未提供）
            if ids is None:
                ids = [f"doc_{i}_{hash(doc) % 1000000}" for i, doc in enumerate(documents)]
            
            # 添加到集合
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
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
        try:
            # 生成查询向量
            query_embedding = self._embed_text(query)
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where
            )
            
            # 格式化结果
            if results['documents'] and results['documents'][0]:
                context_parts = []
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    source = metadata.get('source', 'unknown')
                    context_parts.append(f"[来源: {source}]\n{doc}")
                
                return "\n\n---\n\n".join(context_parts)
            
            return ""
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return ""
    
    async def delete_documents(self, ids: List[str]) -> dict:
        """删除文档"""
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from knowledge base")
            return {"status": "success", "deleted_count": len(ids)}
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    async def get_collection_info(self) -> dict:
        """获取集合信息"""
        try:
            count = self.collection.count()
            return {
                "name": settings.chroma_collection_name,
                "count": count,
                "persist_dir": settings.chroma_persist_dir
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            raise


knowledge_service = KnowledgeService()
```

### 2. 知识库 API (app/api/knowledge.py)

```python
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
import PyPDF2
import docx
from io import BytesIO

from app.services.knowledge_service import knowledge_service
from loguru import logger

router = APIRouter()


@router.post("/documents")
async def add_document(
    content: str,
    metadata: Optional[dict] = None,
    doc_id: Optional[str] = None
):
    """添加文本文档"""
    try:
        result = await knowledge_service.add_documents(
            documents=[content],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id] if doc_id else None
        )
        return result
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/batch")
async def add_documents_batch(documents: List[dict]):
    """批量添加文档"""
    try:
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata") for doc in documents]
        ids = [doc.get("id") for doc in documents]
        
        result = await knowledge_service.add_documents(
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        return result
    except Exception as e:
        logger.error(f"Error adding documents batch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    source: Optional[str] = None
):
    """上传文件并添加到知识库"""
    try:
        content = await file.read()
        
        # 根据文件类型解析
        if file.filename.endswith('.pdf'):
            text = await extract_text_from_pdf(content)
        elif file.filename.endswith('.docx'):
            text = await extract_text_from_docx(content)
        elif file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        result = await knowledge_service.add_documents(
            documents=[text],
            metadatas=[{"source": source or file.filename}],
            ids=None
        )
        
        return result
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents")
async def delete_documents(ids: List[str]):
    """删除文档"""
    try:
        result = await knowledge_service.delete_documents(ids)
        return result
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_knowledge_info():
    """获取知识库信息"""
    try:
        result = await knowledge_service.get_collection_info()
        return result
    except Exception as e:
        logger.error(f"Error getting knowledge info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def extract_text_from_pdf(content: bytes) -> str:
    """从 PDF 提取文本"""
    pdf_file = BytesIO(content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    
    return text


async def extract_text_from_docx(content: bytes) -> str:
    """从 DOCX 提取文本"""
    doc_file = BytesIO(content)
    doc = docx.Document(doc_file)
    
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    return text
```

### 3. 添加文档解析依赖

在 `requirements.txt` 中添加：

```txt
PyPDF2==3.0.1
python-docx==1.1.0
```

---

## MCP 集成

### 1. MCP 服务 (app/services/mcp_service.py)

```python
import httpx
from typing import Dict, List, Optional, Any
from loguru import logger
import json

from config import settings


class MCPService:
    def __init__(self):
        self.server_url = settings.mcp_server_url
        self.timeout = settings.mcp_timeout
        self.client = None
    
    async def _get_client(self):
        """获取 HTTP 客户端"""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=self.timeout)
        return self.client
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 MCP 工具"""
        if not self.server_url:
            logger.warning("MCP server URL not configured")
            return {"error": "MCP not configured"}
        
        try:
            client = await self._get_client()
            
            response = await client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=parameters
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"MCP tool {tool_name} called successfully")
            return result
        except httpx.HTTPError as e:
            logger.error(f"MCP tool call error: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected MCP error: {str(e)}")
            return {"error": str(e)}
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        if not self.server_url:
            return []
        
        try:
            client = await self._get_client()
            
            response = await client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            
            tools = response.json()
            logger.info(f"Retrieved {len(tools)} MCP tools")
            return tools
        except Exception as e:
            logger.error(f"Error listing MCP tools: {str(e)}")
            return []
    
    async def close(self):
        """关闭客户端连接"""
        if self.client:
            await self.client.aclose()
            self.client = None


mcp_service = MCPService()
```

### 2. 在 Agent 中集成 MCP

修改 `app/core/agent.py`：

```python
from typing import List, Dict, AsyncIterator, Optional
from app.core.llm import llm_service
from app.services.knowledge_service import knowledge_service
from app.services.mcp_service import mcp_service
from loguru import logger
import re


class Agent:
    def __init__(self):
        self.system_prompt = """你是一个企业级智能助手，具有以下能力：
1. 可以回答用户的各种问题
2. 可以检索企业知识库获取相关信息
3. 可以调用外部工具（通过 MCP）执行任务

当需要调用工具时，请使用以下格式：
TOOL_CALL: tool_name|param1=value1|param2=value2

请以专业、准确、友好的方式回答用户问题。如果不确定答案，请诚实地说明。"""
    
    def _parse_tool_calls(self, text: str) -> List[Dict]:
        """解析工具调用"""
        pattern = r'TOOL_CALL:\s*(\w+)\|(.*)'
        matches = re.findall(pattern, text)
        
        tool_calls = []
        for match in matches:
            tool_name = match[0]
            params_str = match[1]
            
            params = {}
            if params_str:
                for param in params_str.split('|'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip()
            
            tool_calls.append({
                "tool_name": tool_name,
                "parameters": params
            })
        
        return tool_calls
    
    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> str:
        """执行工具调用"""
        results = []
        for call in tool_calls:
            result = await mcp_service.call_tool(
                tool_name=call["tool_name"],
                parameters=call["parameters"]
            )
            results.append(f"工具 {call['tool_name']} 的结果: {json.dumps(result, ensure_ascii=False)}")
        
        return "\n\n".join(results)
    
    async def process(
        self,
        messages: List[Dict[str, str]],
        use_knowledge: bool = True,
        use_mcp: bool = True,
        user_id: Optional[str] = None
    ) -> str:
        """处理用户消息（非流式）"""
        user_message = messages[-1]["content"] if messages else ""
        
        # 知识库检索
        context = ""
        if use_knowledge and user_message:
            context = await knowledge_service.search(user_message, top_k=3)
        
        # 构建增强的系统提示
        enhanced_system = self.system_prompt
        if context:
            enhanced_system += f"\n\n相关知识库内容：\n{context}"
        
        # 第一轮：调用 LLM
        response = await llm_service.chat(
            messages=messages,
            system_prompt=enhanced_system
        )
        
        # 检查是否有工具调用
        if use_mcp:
            tool_calls = self._parse_tool_calls(response)
            if tool_calls:
                # 执行工具调用
                tool_results = await self._execute_tool_calls(tool_calls)
                
                # 将工具结果加入对话历史
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"工具执行结果：\n{tool_results}\n\n请基于工具结果回答用户问题。"})
                
                # 第二轮：基于工具结果生成最终回答
                response = await llm_service.chat(
                    messages=messages,
                    system_prompt=enhanced_system
                )
        
        return response
    
    async def process_stream(
        self,
        messages: List[Dict[str, str]],
        use_knowledge: bool = True,
        use_mcp: bool = True,
        user_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """处理用户消息（流式）"""
        user_message = messages[-1]["content"] if messages else ""
        
        # 知识库检索
        context = ""
        if use_knowledge and user_message:
            context = await knowledge_service.search(user_message, top_k=3)
        
        # 构建增强的系统提示
        enhanced_system = self.system_prompt
        if context:
            enhanced_system += f"\n\n相关知识库内容：\n{context}"
        
        # 流式调用 LLM
        async for chunk in llm_service.chat_stream(
            messages=messages,
            system_prompt=enhanced_system
        ):
            yield chunk


agent = Agent()
```

---

## 流式响应

### 1. 前端集成示例

```javascript
// 前端调用流式 API 的示例代码
async function streamChat(messages) {
    const response = await fetch('http://localhost:8000/api/v1/chat/completions/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            messages: messages,
            stream: true,
            use_knowledge: true,
            use_mcp: true
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'start') {
                    console.log('Stream started:', data.request_id);
                } else if (data.type === 'content') {
                    console.log('Content:', data.content);
                    // 更新 UI 显示内容
                } else if (data.type === 'end') {
                    console.log('Stream ended:', data.usage);
                }
            }
        }
    }
}
```

### 2. 流式响应优化

在 `app/core/streaming.py` 中添加更多功能：

```python
import json
from typing import Dict, Any
import time


def stream_formatter(data: Dict[str, Any]) -> str:
    """格式化 SSE 流式响应"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


class StreamBuffer:
    """流式响应缓冲区"""
    
    def __init__(self, buffer_size: int = 100):
        self.buffer = []
        self.buffer_size = buffer_size
    
    def add(self, chunk: str) -> bool:
        """添加内容到缓冲区"""
        self.buffer.append(chunk)
        return len(self.buffer) >= self.buffer_size
    
    def get_content(self) -> str:
        """获取缓冲区内容并清空"""
        content = ''.join(self.buffer)
        self.buffer = []
        return content
    
    def flush(self) -> str:
        """刷新缓冲区"""
        return self.get_content()
```

---

## 部署指南

### 1. Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/chroma logs

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "main.py"]
```

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  agent-backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      – ./data:/app/data
      – ./logs:/app/logs
      – ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - agent-backend
    restart: unless-stopped
```

### 2. Nginx 配置

创建 `nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream agent_backend {
        server agent-backend:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # 重定向到 HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # SSE 支持
        proxy_buffering off;
        proxy_cache off;

        location / {
            proxy_pass http://agent_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # SSE 特定配置
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_read_timeout 3600s;
        }

        location /health {
            proxy_pass http://agent_backend/health;
            access_log off;
        }
    }
}
```

### 3. 生产环境部署

使用 Gunicorn + Uvicorn：

```bash
pip install gunicorn

# 启动命令
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### 4. 监控配置

添加 Prometheus 监控到 `main.py`：

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# 指标定义
request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration')

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

---

## 最佳实践

### 1. 安全性

- **API 密钥管理**：使用环境变量或密钥管理服务（如 AWS Secrets Manager）
- **认证授权**：实现 JWT 认证和基于角色的访问控制
- **输入验证**：对所有用户输入进行严格验证
- **速率限制**：防止 API 滥用

### 2. 性能优化

- **连接池**：使用连接池管理数据库和 HTTP 连接
- **缓存**：对频繁访问的知识库查询结果进行缓存
- **异步处理**：使用异步 I/O 提高并发性能
- **负载均衡**：使用 Nginx 或云负载均衡器分发请求

### 3. 可观测性

- **结构化日志**：使用 JSON 格式日志，便于分析
- **分布式追踪**：集成 OpenTelemetry 进行请求追踪
- **指标监控**：监控关键指标（请求量、延迟、错误率）
- **告警机制**：设置合理的告警阈值

### 4. 错误处理

- **优雅降级**：当知识库或 MCP 不可用时，提供基本功能
- **重试机制**：对临时性错误实现指数退避重试
- **错误日志**：记录详细的错误信息用于排查
- **用户友好**：向用户返回清晰的错误信息

### 5. 扩展性

- **插件架构**：支持动态加载新的工具和知识源
- **多模型支持**：支持切换不同的 LLM 提供商
- **多租户**：支持多企业隔离部署
- **水平扩展**：设计无状态服务，支持水平扩容

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-org/enterprise-agent-backend.git
cd enterprise-agent-backend
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 特别是 OPENAI_API_KEY 和 SECRET_KEY
```

### 3. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 启动服务

```bash
python main.py
```

### 5. 测试 API

```bash
# 健康检查
curl http://localhost:8000/health

# 添加知识库文档
curl -X POST http://localhost:8000/api/v1/knowledge/documents \
  -H "Content-Type: application/json" \
  -d '{"content": "企业知识库示例文档内容", "metadata": {"source": "internal"}}'

# 流式聊天
curl -X POST http://localhost:8000/api/v1/chat/completions/stream \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好"}], "stream": true}'
```

---

## 常见问题

### Q1: 如何更换 LLM 提供商？

修改 `config.py` 中的配置，然后在 `app/core/llm.py` 中使用相应的 LangChain 集成。

### Q2: 如何支持更多文件格式？

在 `app/api/knowledge.py` 中添加新的解析函数，支持更多文件格式。

### Q3: 如何实现多用户隔离？

在知识库和对话历史中添加 user_id 字段，实现数据隔离。

### Q4: 如何提高知识库检索准确度？

- 优化文档切分策略
- 使用更强大的嵌入模型
- 调整检索参数（top_k、相似度阈值）
- 实现混合检索（关键词 + 向量）

### Q5: 如何处理长对话？

- 实现对话摘要，压缩历史消息
- 使用滑动窗口保留最近 N 轮对话
- 实现对话状态管理

---

## 总结

本指南提供了从零开始搭建企业级 Agent 后端服务的完整方案，包括：

✅ **第三方 LLM 集成**：支持 OpenAI 等多种模型  
✅ **知识库支持**：基于 ChromaDB 的向量检索  
✅ **MCP 集成**：支持外部工具调用  
✅ **流式响应**：SSE 实时输出  
✅ **企业级特性**：认证、日志、监控、部署

按照本指南，你可以搭建一个生产就绪的 Agent 后端服务，为前端应用提供强大的 AI 能力支持。

---

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [ChromaDB 文档](https://docs.trychroma.com/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [OpenAI API 文档](https://platform.openai.com/docs)

---

**版本**: 1.0.0  
**更新日期**: 2026-06-28  
**维护者**: Enterprise Agent Team
