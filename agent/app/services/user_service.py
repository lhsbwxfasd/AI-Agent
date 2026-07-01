import uuid
from datetime import datetime
from typing import Optional, List
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy import select, and_
from loguru import logger

from app.db.database import db_manager, UserModel
from config import settings


class UserService:
    """用户服务"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        """创建访问令牌"""
        from datetime import timedelta
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    async def register(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> dict:
        """用户注册"""
        async with db_manager.get_session() as session:
            # 检查用户名是否已存在
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            if result.scalar_one_or_none():
                raise ValueError("用户名已存在")
            
            # 检查邮箱是否已存在
            if email:
                result = await session.execute(
                    select(UserModel).where(UserModel.email == email)
                )
                if result.scalar_one_or_none():
                    raise ValueError("邮箱已被注册")
            
            # 创建用户
            user_id = str(uuid.uuid4())
            password_hash = self.get_password_hash(password)
            
            user = UserModel(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                is_active=1,
                is_admin=0
            )
            
            session.add(user)
            await session.commit()
            
            logger.info(f"User registered: {username}")
            
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "is_active": True,
                "is_admin": False
            }
    
    async def login(self, username: str, password: str) -> dict:
        """用户登录"""
        async with db_manager.get_session() as session:
            # 查找用户
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("用户名或密码错误")
            
            # 验证密码
            if not self.verify_password(password, user.password_hash):
                raise ValueError("用户名或密码错误")
            
            # 检查用户是否激活
            if not user.is_active:
                raise ValueError("用户已被禁用")
            
            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            await session.commit()
            
            # 创建访问令牌
            access_token = self.create_access_token(
                data={"sub": user.id, "username": user.username}
            )
            
            logger.info(f"User logged in: {username}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_admin": bool(user.is_admin)
                }
            }
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """获取用户信息"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": bool(user.is_active),
                "is_admin": bool(user.is_admin),
                "created_at": user.created_at,
                "last_login": user.last_login,
                "preferred_model": user.preferred_model
            }
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": bool(user.is_active),
                "is_admin": bool(user.is_admin)
            }
    
    async def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
        preferred_model: Optional[str] = None
    ) -> Optional[dict]:
        """更新用户信息"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if email is not None:
                # 检查邮箱是否被其他用户使用
                result = await session.execute(
                    select(UserModel).where(
                        and_(UserModel.email == email, UserModel.id != user_id)
                    )
                )
                if result.scalar_one_or_none():
                    raise ValueError("邮箱已被其他用户使用")
                user.email = email
            
            if full_name is not None:
                user.full_name = full_name
            
            if password is not None:
                user.password_hash = self.get_password_hash(password)
            
            if preferred_model is not None:
                user.preferred_model = preferred_model
            
            user.updated_at = datetime.utcnow()
            await session.commit()
            
            return await self.get_user(user_id)
    
    async def list_users(self, limit: int = 20, offset: int = 0) -> List[dict]:
        """获取用户列表（管理员功能）"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel)
                .order_by(UserModel.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            users = result.scalars().all()
            
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": bool(user.is_active),
                    "is_admin": bool(user.is_admin),
                    "created_at": user.created_at,
                    "last_login": user.last_login
                }
                for user in users
            ]
    
    async def deactivate_user(self, user_id: str) -> bool:
        """禁用用户（管理员功能）"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.is_active = 0
            user.updated_at = datetime.utcnow()
            await session.commit()
            
            logger.info(f"User deactivated: {user.username}")
            return True
    
    async def activate_user(self, user_id: str) -> bool:
        """激活用户（管理员功能）"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.is_active = 1
            user.updated_at = datetime.utcnow()
            await session.commit()
            
            logger.info(f"User activated: {user.username}")
            return True
    
    def get_user_preferred_model(self, user_id: str) -> str:
        """获取用户偏好模型"""
        # 这个方法保持同步以兼容现有代码
        # 实际应该改为异步，但需要修改调用处
        return settings.default_model


user_service = UserService()
