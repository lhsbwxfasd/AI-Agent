from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录响应信息
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )
        
        return response
