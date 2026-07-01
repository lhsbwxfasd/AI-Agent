import json
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message, ConversationCreate, ConversationUpdate, MessageAttachment
from app.db.database import db_manager, ConversationModel, MessageModel
from config import settings


class ConversationService:
    """会话服务（数据库版本）"""
    
    async def create_conversation(
        self,
        user_id: str,
        conversation_data: ConversationCreate
    ) -> Conversation:
        """创建新会话"""
        conversation_id = str(uuid.uuid4())
        title = conversation_data.title or "新对话"
        
        async with db_manager.get_session() as session:
            # 创建会话记录
            conv_model = ConversationModel(
                id=conversation_id,
                user_id=user_id,
                title=title,
                model=conversation_data.model
            )
            session.add(conv_model)
            await session.commit()
            
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            
            return Conversation(
                id=conversation_id,
                user_id=user_id,
                title=title,
                model=conversation_data.model,
                messages=[],
                summary=None,
                created_at=conv_model.created_at,
                updated_at=conv_model.updated_at
            )
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        async with db_manager.get_session() as session:
            # 查询会话
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            conv_model = result.scalar_one_or_none()
            
            if not conv_model:
                return None
            
            # 查询消息
            msg_result = await session.execute(
                select(MessageModel)
                .where(MessageModel.conversation_id == conversation_id)
                .order_by(MessageModel.timestamp)
            )
            msg_models = msg_result.scalars().all()
            
            # 转换为领域模型
            messages = []
            for msg_model in msg_models:
                attachments = None
                if msg_model.attachments:
                    attachments = [
                        MessageAttachment(**att) 
                        for att in msg_model.attachments
                    ]
                
                messages.append(Message(
                    role=msg_model.role,
                    content=msg_model.content,
                    timestamp=msg_model.timestamp,
                    attachments=attachments
                ))
            
            return Conversation(
                id=conv_model.id,
                user_id=conv_model.user_id,
                title=conv_model.title,
                model=conv_model.model,
                messages=messages,
                summary=conv_model.summary,
                created_at=conv_model.created_at,
                updated_at=conv_model.updated_at
            )
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """获取用户的所有会话"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel)
                .where(ConversationModel.user_id == user_id)
                .order_by(desc(ConversationModel.updated_at))
                .offset(offset)
                .limit(limit)
            )
            conv_models = result.scalars().all()
            
            conversations = []
            for conv_model in conv_models:
                conversations.append(Conversation(
                    id=conv_model.id,
                    user_id=conv_model.user_id,
                    title=conv_model.title,
                    model=conv_model.model,
                    messages=[],
                    summary=conv_model.summary,
                    created_at=conv_model.created_at,
                    updated_at=conv_model.updated_at
                ))
            
            return conversations
    
    async def update_conversation(
        self,
        conversation_id: str,
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """更新会话"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            conv_model = result.scalar_one_or_none()
            
            if not conv_model:
                return None
            
            if update_data.title is not None:
                conv_model.title = update_data.title
            if update_data.model is not None:
                conv_model.model = update_data.model
            
            conv_model.updated_at = datetime.utcnow()
            await session.commit()
            
            return await self.get_conversation(conversation_id)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """删除会话"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            conv_model = result.scalar_one_or_none()
            
            if not conv_model:
                return False
            
            await session.delete(conv_model)
            await session.commit()
            
            logger.info(f"Deleted conversation {conversation_id}")
            return True
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        attachments: Optional[List[Dict]] = None
    ) -> Optional[Conversation]:
        """添加消息到会话"""
        async with db_manager.get_session() as session:
            # 检查会话是否存在
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            conv_model = result.scalar_one_or_none()
            
            if not conv_model:
                return None
            
            # 准备附件数据
            attachments_json = None
            if attachments:
                attachments_json = [
                    {
                        "id": att.get("id", ""),
                        "filename": att.get("filename", ""),
                        "content_type": att.get("content_type", ""),
                        "size": att.get("size", 0)
                    }
                    for att in attachments
                ]
            
            # 创建消息记录
            msg_model = MessageModel(
                conversation_id=conversation_id,
                role=role,
                content=content,
                attachments=attachments_json
            )
            session.add(msg_model)
            
            # 更新会话
            conv_model.updated_at = datetime.utcnow()
            
            # 如果是第一条用户消息，更新标题
            if role == "user":
                msg_count_result = await session.execute(
                    select(MessageModel).where(MessageModel.conversation_id == conversation_id)
                )
                msg_count = len(msg_count_result.scalars().all())
                if msg_count == 0:  # 这是第一条消息（还没commit）
                    conv_model.title = content[:50] + "..." if len(content) > 50 else content
            
            await session.commit()
            
            return await self.get_conversation(conversation_id)
    
    async def update_summary(
        self,
        conversation_id: str,
        summary: str
    ) -> Optional[Conversation]:
        """更新会话摘要"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.id == conversation_id)
            )
            conv_model = result.scalar_one_or_none()
            
            if not conv_model:
                return None
            
            conv_model.summary = summary
            conv_model.updated_at = datetime.utcnow()
            await session.commit()
            
            return await self.get_conversation(conversation_id)
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        max_history: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """获取会话消息（用于发送给LLM）"""
        async with db_manager.get_session() as session:
            query = (
                select(MessageModel)
                .where(MessageModel.conversation_id == conversation_id)
                .order_by(MessageModel.timestamp)
            )
            
            result = await session.execute(query)
            msg_models = result.scalars().all()
            
            messages = []
            for msg_model in msg_models:
                msg_dict = {
                    "role": msg_model.role,
                    "content": msg_model.content
                }
                
                if msg_model.attachments:
                    msg_dict["attachments"] = msg_model.attachments
                
                messages.append(msg_dict)
            
            # 如果设置了最大历史数，进行截断
            if max_history and len(messages) > max_history:
                system_messages = [m for m in messages if m["role"] == "system"]
                recent_messages = messages[-max_history:]
                messages = system_messages + recent_messages
            
            return messages
    
    async def get_conversation_count(self, user_id: str) -> int:
        """获取用户会话数量"""
        async with db_manager.get_session() as session:
            result = await session.execute(
                select(ConversationModel).where(ConversationModel.user_id == user_id)
            )
            return len(result.scalars().all())


conversation_service = ConversationService()
