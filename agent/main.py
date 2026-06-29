from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

# 设置 HuggingFace 镜像（必须在导入相关库之前）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.expanduser('~/.cache/huggingface/hub')

# 修复 sqlite3 版本问题（必须在导入 chromadb 之前）
from app.utils.sqlite3_patch import *

from app.api import chat, knowledge, auth, conversation
from app.middleware.logging import LoggingMiddleware
from app.middleware.auth import AuthMiddleware
from app.utils.logger import setup_logger
from app.services.mcp_service import mcp_service
from app.services.knowledge_service import knowledge_service
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # 异步初始化知识库服务
    try:
        await knowledge_service.initialize()
        logger.info("Knowledge service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize knowledge service: {str(e)}")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down application")
    
    # 清理资源
    try:
        await mcp_service.close()
        logger.info("MCP service closed")
    except Exception as e:
        logger.error(f"Error closing MCP service: {str(e)}")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # 自定义中间件
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # 注册路由
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天"])
    app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
    app.include_router(conversation.router, prefix="/api/v1/conversations", tags=["会话管理"])
    
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
