from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MessageAttachment(BaseModel):
    """消息附件"""
    id: str = Field(..., description="附件ID")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小")


class Message(BaseModel):
    role: str = Field(..., description="消息角色：user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="消息时间戳")
    attachments: Optional[List[MessageAttachment]] = Field(default=None, description="附件列表")


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, description="会话标题")
    model: str = Field(default="gpt-4", description="使用的模型")


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, description="会话标题")
    model: Optional[str] = Field(None, description="使用的模型")


class Conversation(BaseModel):
    id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    title: str = Field(..., description="会话标题")
    model: str = Field(..., description="使用的模型")
    messages: List[Message] = Field(default_factory=list, description="消息列表")
    summary: Optional[str] = Field(None, description="会话摘要")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    conversations: List[Conversation] = Field(..., description="会话列表")
    total: int = Field(..., description="总数")
