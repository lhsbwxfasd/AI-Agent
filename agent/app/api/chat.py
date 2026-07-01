from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import uuid

from app.models.chat import ChatRequest, ChatResponse
from app.core.agent import agent
from app.core.llm import llm_service
from app.core.streaming import stream_formatter
from app.services.conversation_service import conversation_service
from app.services.auth_service import auth_service
from loguru import logger

router = APIRouter()


async def get_current_user() -> str:
    """获取当前用户（简化版，实际应从JWT token中获取）"""
    return "admin"


async def get_user_preferred_model(user_id: str) -> str:
    """获取用户偏好模型"""
    return auth_service.get_user_preferred_model(user_id)


@router.get("/models")
async def list_models():
    """获取可用模型列表"""
    try:
        models = llm_service.get_available_models()
        return {
            "models": models,
            "default": "deepseek-r1:7b"
        }
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completions")
async def chat_completion(
    request: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    """聊天完成接口（非流式）"""
    try:
        messages_dict = [msg.dict() for msg in request.messages]
        
        # 确定使用的模型
        model = request.model or await get_user_preferred_model(current_user)
        
        # 处理会话
        conversation_id = request.conversation_id
        if conversation_id:
            # 获取会话历史
            conversation = await conversation_service.get_conversation(conversation_id)
            if conversation:
                # 使用会话中的模型
                model = conversation.model
                # 获取历史消息并添加新消息
                messages_dict = await conversation_service.get_conversation_messages(
                    conversation_id=conversation_id,
                    max_history=None
                )
                # 添加当前用户消息到历史（包含附件）
                last_message = request.messages[-1].dict()
                messages_dict.append({
                    "role": "user", 
                    "content": last_message["content"],
                    "attachments": last_message.get("attachments")
                })
                
                # 保存用户消息
                await conversation_service.add_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=last_message["content"]
                )
        else:
            # 创建新会话
            from app.models.conversation import ConversationCreate
            new_conversation = await conversation_service.create_conversation(
                user_id=current_user,
                conversation_data=ConversationCreate(model=model)
            )
            conversation_id = new_conversation.id
        
        response = await agent.process(
            messages=messages_dict,
            use_knowledge=request.use_knowledge,
            use_mcp=request.use_mcp,
            user_id=current_user,
            conversation_id=conversation_id,
            model=model
        )
        
        # 保存助手回复
        await conversation_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response
        )
        
        return ChatResponse(
            content=response,
            model=model,
            conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completions/stream")
async def chat_completion_stream(
    request: ChatRequest,
    current_user: str = Depends(get_current_user)
):
    """聊天完成接口（流式）"""
    try:
        messages_dict = [msg.dict() for msg in request.messages]
        
        # 确定使用的模型
        model = request.model or await get_user_preferred_model(current_user)
        
        # 处理会话
        conversation_id = request.conversation_id
        if conversation_id:
            # 获取会话历史
            conversation = await conversation_service.get_conversation(conversation_id)
            if conversation:
                model = conversation.model
                # 获取历史消息并添加新消息
                messages_dict = await conversation_service.get_conversation_messages(
                    conversation_id=conversation_id,
                    max_history=None
                )
                # 添加当前用户消息到历史（包含附件）
                last_message = request.messages[-1].dict()
                messages_dict.append({
                    "role": "user", 
                    "content": last_message["content"],
                    "attachments": last_message.get("attachments")
                })
                
                # 保存用户消息（包含附件）
                await conversation_service.add_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=last_message["content"],
                    attachments=last_message.get("attachments")
                )
        else:
            # 创建新会话
            from app.models.conversation import ConversationCreate
            new_conversation = await conversation_service.create_conversation(
                user_id=current_user,
                conversation_data=ConversationCreate(model=model)
            )
            conversation_id = new_conversation.id
        
        async def generate() -> AsyncGenerator[str, None]:
            request_id = str(uuid.uuid4())
            
            # 发送开始事件
            yield stream_formatter({
                "type": "start",
                "request_id": request_id,
                "model": model,
                "conversation_id": conversation_id
            })
            
            # 流式生成内容
            full_content = ""
            async for chunk in agent.process_stream(
                messages=messages_dict,
                use_knowledge=request.use_knowledge,
                use_mcp=request.use_mcp,
                user_id=current_user,
                conversation_id=conversation_id,
                model=model
            ):
                full_content += chunk
                yield stream_formatter({
                    "type": "content",
                    "content": chunk,
                    "request_id": request_id
                })
            
            # 保存助手回复
            await conversation_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_content
            )
            
            # 发送结束事件
            yield stream_formatter({
                "type": "end",
                "request_id": request_id,
                "conversation_id": conversation_id,
                "usage": {
                    "total_tokens": len(full_content)
                }
            })
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"Chat stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
