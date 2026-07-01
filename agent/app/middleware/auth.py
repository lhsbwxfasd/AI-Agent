from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from jose import jwt, JWTError

from app.services.auth_service import auth_service
from config import settings


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
        "/api/v1/auth/register",
        "/api/v1/users/register",
        "/api/v1/users/login"
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
            request.state.user_id = token_data.user_id if hasattr(token_data, 'user_id') else token_data.username
            logger.info(f"User {token_data.username} authenticated for {request.url.path}")
            
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"}
            )
        
        return await call_next(request)


# 用于依赖注入的函数
async def get_current_user_id(request: Request) -> str:
    """获取当前用户ID"""
    authorization = request.headers.get("Authorization")
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        # 解码 token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_id
        
    except (ValueError, JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def get_current_user_role(request: Request) -> tuple:
    """获取当前用户ID和角色"""
    authorization = request.headers.get("Authorization")
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        # 解码 token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
        # 查询用户是否是管理员
        from app.db.database import db_manager, UserModel
        from sqlalchemy import select
        
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            is_admin = bool(user.is_admin)
        
        return user_id, is_admin
        
    except (ValueError, JWTError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def require_admin(request: Request) -> str:
    """要求管理员权限"""
    user_id, is_admin = await get_current_user_role(request)
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_id
