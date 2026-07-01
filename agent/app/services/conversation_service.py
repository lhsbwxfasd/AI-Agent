import json
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from loguru import logger

from app.models.conversation import Conversation, Message, ConversationCreate, ConversationUpdate
from config import settings


class ConversationService:
    def __init__(self):
        # 使用文件存储会话数据（生产环境应使用数据库）
        self.conversations_dir = Path("./data/conversations")
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.conversations: Dict[str, Conversation] = {}
        self._load_conversations()
    
    def _load_conversations(self):
        """从文件加载会话"""
        try:
            for file_path in self.conversations_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversation = Conversation(**data)
                    self.conversations[conversation.id] = conversation
            logger.info(f"Loaded {len(self.conversations)} conversations")
        except Exception as e:
            logger.error(f"Error loading conversations: {str(e)}")
    
    def _save_conversation(self, conversation: Conversation):
        """保存会话到文件"""
        try:
            file_path = self.conversations_dir / f"{conversation.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation.dict(), f, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
    
    async def create_conversation(
        self,
        user_id: str,
        conversation_data: ConversationCreate
    ) -> Conversation:
        """创建新会话"""
        conversation_id = str(uuid.uuid4())
        
        # 如果没有标题，使用第一条消息作为标题
        title = conversation_data.title or "新对话"
        
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title=title,
            model=conversation_data.model,
            messages=[],
            summary=None
        )
        
        self.conversations[conversation_id] = conversation
        self._save_conversation(conversation)
        
        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话"""
        return self.conversations.get(conversation_id)
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """获取用户的所有会话"""
        user_conversations = [
            conv for conv in self.conversations.values()
            if conv.user_id == user_id
        ]
        
        # 按更新时间倒序排序
        user_conversations.sort(key=lambda x: x.updated_at, reverse=True)
        
        return user_conversations[offset:offset + limit]
    
    async def update_conversation(
        self,
        conversation_id: str,
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """更新会话"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        if update_data.title is not None:
            conversation.title = update_data.title
        if update_data.model is not None:
            conversation.model = update_data.model
        
        conversation.updated_at = datetime.utcnow()
        self._save_conversation(conversation)
        
        return conversation
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """删除会话"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
            # 删除文件
            file_path = self.conversations_dir / f"{conversation_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        return False
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        attachments: Optional[List[Dict]] = None
    ) -> Optional[Conversation]:
        """添加消息到会话"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        # 处理附件
        message_attachments = None
        if attachments:
            from app.models.conversation import MessageAttachment
            message_attachments = [
                MessageAttachment(
                    id=att.get('id', ''),
                    filename=att.get('filename', ''),
                    content_type=att.get('content_type', ''),
                    size=att.get('size', 0)
                )
                for att in attachments
            ]
        
        message = Message(
            role=role, 
            content=content,
            attachments=message_attachments
        )
        conversation.messages.append(message)
        conversation.updated_at = datetime.utcnow()
        
        # 如果是第一条用户消息，更新标题
        if role == "user" and len(conversation.messages) == 1:
            conversation.title = content[:50] + "..." if len(content) > 50 else content
        
        self._save_conversation(conversation)
        return conversation
    
    async def update_summary(
        self,
        conversation_id: str,
        summary: str
    ) -> Optional[Conversation]:
        """更新会话摘要"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        conversation.summary = summary
        conversation.updated_at = datetime.utcnow()
        self._save_conversation(conversation)
        
        return conversation
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        max_history: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """获取会话消息（用于发送给LLM）"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []
        
        messages = []
        for msg in conversation.messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            
            # 如果有附件，也包含附件信息
            if msg.attachments:
                msg_dict["attachments"] = [
                    {
                        "id": att.id,
                        "filename": att.filename,
                        "content_type": att.content_type,
                        "size": att.size
                    }
                    for att in msg.attachments
                ]
            
            messages.append(msg_dict)
        
        # 如果设置了最大历史数，进行截断
        if max_history and len(messages) > max_history:
            # 保留系统消息和最近的消息
            system_messages = [m for m in messages if m["role"] == "system"]
            recent_messages = messages[-max_history:]
            messages = system_messages + recent_messages
        
        return messages
    
    async def get_conversation_count(self, user_id: str) -> int:
        """获取用户会话数量"""
        return len([
            conv for conv in self.conversations.values()
            if conv.user_id == user_id
        ])


conversation_service = ConversationService()
