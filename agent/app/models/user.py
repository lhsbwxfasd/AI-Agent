from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserCreate(UserBase):
    password: str = Field(..., description="密码")


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class User(UserBase):
    id: int = Field(..., description="用户 ID")
    is_active: bool = Field(default=True, description="是否激活")
    preferred_model: str = Field(default="gpt-4", description="偏好模型")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
