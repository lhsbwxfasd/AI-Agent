from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Attachment(BaseModel):
    id: str = Field(..., description="附件ID")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小")
    parsed_content: Optional[str] = Field(default=None, description="解析后的内容")


class Message(BaseModel):
    role: str = Field(..., description="消息角色：user/assistant/system")
    content: str = Field(..., description="消息内容")
    attachments: Optional[List[Attachment]] = Field(default=None, description="附件列表")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="对话历史")
    stream: bool = Field(default=True, description="是否使用流式响应")
    use_knowledge: bool = Field(default=True, description="是否使用知识库")
    use_mcp: bool = Field(default=True, description="是否使用 MCP 工具")
    model: Optional[str] = Field(default=None, description="使用的模型（不指定则使用用户偏好模型）")
    conversation_id: Optional[str] = Field(default=None, description="会话ID（用于保存对话历史）")
    temperature: Optional[float] = Field(default=None, description="温度参数")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")


class ChatResponse(BaseModel):
    content: str = Field(..., description="回复内容")
    model: str = Field(..., description="使用的模型")
    conversation_id: Optional[str] = Field(default=None, description="会话ID")
    usage: Optional[Dict] = Field(default=None, description="token 使用情况")
