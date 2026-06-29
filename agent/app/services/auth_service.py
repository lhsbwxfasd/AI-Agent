from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from loguru import logger

from config import settings
from app.models.user import User, TokenData

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        
        # 模拟用户数据库（生产环境应使用真实数据库）
        self.users_db = {
            "admin": {
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": self.get_password_hash("admin123"),
                "id": 1,
                "is_active": True,
                "preferred_model": "deepseek-chat"
            }
        }
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    def get_user(self, username: str) -> Optional[User]:
        """获取用户"""
        user_dict = self.users_db.get(username)
        if user_dict:
            return User(**user_dict)
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """认证用户"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            return TokenData(username=username)
        except JWTError:
            return None
    
    async def login(self, username: str, password: str) -> dict:
        """用户登录"""
        user = self.authenticate_user(username, password)
        if not user:
            logger.warning(f"Failed login attempt for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = self.create_access_token(data={"sub": user.username})
        logger.info(f"User {username} logged in successfully")
        
        # 返回用户信息（不包含密码）
        user_info = {
            "username": user.username,
            "email": user.email,
            "id": user.id,
            "is_active": user.is_active,
            "preferred_model": user.preferred_model
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_info
        }
    
    def update_user_preferred_model(self, username: str, preferred_model: str) -> Optional[User]:
        """更新用户偏好模型"""
        if username not in self.users_db:
            return None
        
        self.users_db[username]["preferred_model"] = preferred_model
        return User(**self.users_db[username])
    
    def get_user_preferred_model(self, username: str) -> str:
        """获取用户偏好模型"""
        user = self.get_user(username)
        if user:
            return user.preferred_model
        return "deepseek-chat"


auth_service = AuthService()
