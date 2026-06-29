from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.services.auth_service import auth_service


class AuthMiddleware(BaseHTTPMiddleware):
    # 不需要认证的路径
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/api/v1/auth/login",
        "/api/v1/auth/register"
    }
    
    async def dispatch(self, request: Request, call_next):
        # 检查是否在排除列表中
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # 获取 Authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            logger.warning(f"Missing authorization header for {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authorization header"}
            )
        
        # 验证 token
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication scheme"}
                )
            
            token_data = auth_service.verify_token(token)
            if not token_data:
                logger.warning(f"Invalid token for {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired token"}
                )
            
            # 将用户信息添加到 request state
            request.state.user = token_data.username
            logger.info(f"User {token_data.username} authenticated for {request.url.path}")
            
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"}
            )
        
        return await call_next(request)
