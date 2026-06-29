from pydantic_settings import BaseSettings
from typing import Optional, List, Dict
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
    openai_base_url: str = "https://api.deepseek.com"
    default_model: str = "deepseek-chat"
    default_temperature: float = 0.7
    max_tokens: int = 2000
    
    # DeepSeek 配置（兼容字段）
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # 多模型配置
    available_models: Dict[str, Dict] = {
        "deepseek-chat": {"name": "DeepSeek Chat", "provider": "deepseek", "max_tokens": 4096},
        "deepseek-coder": {"name": "DeepSeek Coder", "provider": "deepseek", "max_tokens": 4096},
        "gpt-4": {"name": "GPT-4", "provider": "openai", "max_tokens": 8192},
        "gpt-3.5-turbo": {"name": "GPT-3.5 Turbo", "provider": "openai", "max_tokens": 4096},
        "claude-3-opus": {"name": "Claude 3 Opus", "provider": "anthropic", "max_tokens": 4096},
        "claude-3-sonnet": {"name": "Claude 3 Sonnet", "provider": "anthropic", "max_tokens": 4096},
    }
    
    # 长对话配置
    max_conversation_history: int = 20  # 最大对话历史轮数
    enable_conversation_summary: bool = True  # 启用对话摘要
    summary_threshold: int = 10  # 超过多少轮对话后进行摘要
    
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
    
    # CORS 配置
    cors_allow_origins: List[str] = ["*"]  # 生产环境应限制来源
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
