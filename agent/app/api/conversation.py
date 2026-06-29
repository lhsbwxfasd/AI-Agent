from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from loguru import logger

from app.models.conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationList
from app.services.conversation_service import conversation_service

router = APIRouter()


async def get_current_user() -> str:
    """获取当前用户（简化版，实际应从JWT token中获取）"""
    # 这里应该从 request.state.user 获取，简化处理返回默认用户
    return "admin"


@router.post("/", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: str = Depends(get_current_user)
):
    """创建新会话"""
    try:
        conversation = await conversation_service.create_conversation(
            user_id=current_user,
            conversation_data=conversation_data
        )
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ConversationList)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    """获取用户的所有会话"""
    try:
        conversations = await conversation_service.get_user_conversations(
            user_id=current_user,
            limit=limit,
            offset=offset
        )
        total = await conversation_service.get_conversation_count(current_user)
        
        return ConversationList(
            conversations=conversations,
            total=total
        )
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user)
):
    """获取指定会话"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 验证权限
        if conversation.user_id != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    current_user: str = Depends(get_current_user)
):
    """更新会话"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 验证权限
        if conversation.user_id != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        updated = await conversation_service.update_conversation(
            conversation_id=conversation_id,
            update_data=update_data
        )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user)
):
    """删除会话"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 验证权限
        if conversation.user_id != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await conversation_service.delete_conversation(conversation_id)
        if success:
            return {"message": "Conversation deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    max_history: int = None,
    current_user: str = Depends(get_current_user)
):
    """获取会话的消息历史"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # 验证权限
        if conversation.user_id != current_user:
            raise HTTPException(status_code=403, detail="Access denied")
        
        messages = await conversation_service.get_conversation_messages(
            conversation_id=conversation_id,
            max_history=max_history
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "summary": conversation.summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
