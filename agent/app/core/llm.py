from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, AsyncIterator, Optional
from config import settings
from loguru import logger


class LLMService:
    def __init__(self):
        self.llm_cache = {}  # 缓存不同模型的 LLM 实例
        logger.info(f"LLM service initialized with available models: {list(settings.available_models.keys())}")
    
    def _get_llm(self, model: Optional[str] = None) -> ChatOpenAI:
        """获取指定模型的 LLM 实例"""
        model_name = model or settings.default_model
        
        # 检查模型是否可用
        if model_name not in settings.available_models:
            logger.warning(f"Model {model_name} not available, using default model")
            model_name = settings.default_model
        
        # 从缓存获取或创建新实例
        if model_name not in self.llm_cache:
            model_config = settings.available_models[model_name]
            
            self.llm_cache[model_name] = ChatOpenAI(
                model=model_name,
                temperature=settings.default_temperature,
                max_tokens=model_config.get("max_tokens", settings.max_tokens),
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_base_url,
                streaming=True
            )
            logger.info(f"Created LLM instance for model: {model_name}")
        
        return self.llm_cache[model_name]
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """同步聊天"""
        llm = self._get_llm(model)
        langchain_messages = []
        
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        response = await llm.ainvoke(langchain_messages)
        return response.content
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天"""
        llm = self._get_llm(model)
        langchain_messages = []
        
        if system_prompt:
            langchain_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        async for chunk in llm.astream(langchain_messages):
            if chunk.content:
                yield chunk.content
    
    def get_available_models(self) -> Dict[str, Dict]:
        """获取可用模型列表"""
        return settings.available_models


llm_service = LLMService()
