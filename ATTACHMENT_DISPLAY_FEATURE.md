# 会话附件显示功能 - 实现说明

## 功能概述

实现了在会话聊天中显示用户上传的附件，包括：
1. 当前会话中实时显示附件
2. 历史会话加载时显示附件

## 实现细节

### 一、后端修改

#### 1. 消息模型扩展 (`agent/app/models/conversation.py`)

**新增 `MessageAttachment` 模型**：
```python
class MessageAttachment(BaseModel):
    """消息附件"""
    id: str = Field(..., description="附件ID")
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小")
```

**扩展 `Message` 模型**：
```python
class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime
    attachments: Optional[List[MessageAttachment]] = None  # 新增
```

#### 2. 会话服务修改 (`agent/app/services/conversation_service.py`)

**修改 `add_message` 方法**：
- 新增 `attachments` 参数
- 保存消息时同时保存附件信息

```python
async def add_message(
    self,
    conversation_id: str,
    role: str,
    content: str,
    attachments: Optional[List[Dict]] = None  # 新增
) -> Optional[Conversation]:
    # 处理附件
    message_attachments = None
    if attachments:
        message_attachments = [
            MessageAttachment(...)
            for att in attachments
        ]
    
    message = Message(
        role=role, 
        content=content,
        attachments=message_attachments  # 保存附件
    )
```

**修改 `get_conversation_messages` 方法**：
- 返回消息时包含附件信息

```python
async def get_conversation_messages(...):
    messages = []
    for msg in conversation.messages:
        msg_dict = {"role": msg.role, "content": msg.content}
        
        # 如果有附件，也包含附件信息
        if msg.attachments:
            msg_dict["attachments"] = [...]
        
        messages.append(msg_dict)
```

#### 3. 聊天 API 修改 (`agent/app/api/chat.py`)

**修改消息保存逻辑**：
```python
# 保存用户消息（包含附件）
await conversation_service.add_message(
    conversation_id=conversation_id,
    role="user",
    content=last_message["content"],
    attachments=last_message.get("attachments")  # 传递附件
)
```

### 二、前端修改

#### 1. 创建附件显示组件 (`web/src/components/MessageAttachments.vue`)

**功能**：
- 显示附件图标（图片/PDF/文档）
- 显示文件名和大小
- 支持多种附件类型

**特点**：
- 根据文件类型显示不同图标
- 自动格式化文件大小
- 响应式设计，支持多个附件

#### 2. 修改聊天界面 (`web/src/views/Chat.vue`)

**导入附件组件**：
```javascript
import MessageAttachments from '@/components/MessageAttachments.vue'
```

**在用户消息中显示附件**：
```vue
<div v-if="message.role === 'user'" class="user-message">
  <MessageAttachments 
    v-if="message.attachments && message.attachments.length > 0"
    :attachments="message.attachments"
  />
  <div class="message-content">
    {{ message.content }}
  </div>
</div>
```

**修改会话加载逻辑**：
```javascript
async function handleSelectConversation(id) {
  const response = await conversationApi.getMessages(id)
  chatStore.messages = response.messages.map(msg => ({
    role: msg.role,
    content: msg.content,
    attachments: msg.attachments || undefined  // 加载附件
  }))
}
```

## 数据流程

### 1. 发送带附件的消息

```
用户上传附件
  ↓
前端保存附件信息
  ↓
用户发送消息
  ↓
前端将消息+附件发送到后端
  ↓
后端保存消息（包含附件信息）
  ↓
后端处理消息（OCR等）
  ↓
后端返回AI回复
  ↓
前端显示用户消息（含附件）+ AI回复
```

### 2. 加载历史会话

```
用户点击历史会话
  ↓
前端请求会话消息
  ↓
后端返回消息列表（含附件信息）
  ↓
前端显示消息（含附件）
```

## 存储结构

### 会话文件格式 (`data/conversations/{id}.json`)

```json
{
  "id": "conversation-id",
  "user_id": "user-id",
  "title": "会话标题",
  "model": "deepseek-r1:7b",
  "messages": [
    {
      "role": "user",
      "content": "请分析这张图片",
      "timestamp": "2026-07-01T10:00:00",
      "attachments": [
        {
          "id": "attachment-id",
          "filename": "image.png",
          "content_type": "image/png",
          "size": 123456
        }
      ]
    },
    {
      "role": "assistant",
      "content": "根据图片内容...",
      "timestamp": "2026-07-01T10:00:05",
      "attachments": null
    }
  ]
}
```

## UI 效果

### 用户消息显示

```
┌─────────────────────────────────┐
│ 📎 image.png (120.5 KB)         │  ← 附件显示
│ 📎 document.pdf (2.3 MB)        │
├─────────────────────────────────┤
│ 请分析这些文件的内容            │  ← 消息内容
└─────────────────────────────────┘
```

### 附件图标

- **图片**：🖼️ Picture 图标
- **PDF**：📄 Document 图标
- **其他**：📁 Folder 图标

## 支持的附件类型

- **图片**：PNG, JPG, GIF, WebP, BMP
- **文档**：PDF, DOCX, TXT
- **其他**：任何类型（显示通用图标）

## 性能优化

### 1. 附件信息轻量化

只保存必要的附件信息：
- ✅ ID（用于引用）
- ✅ 文件名（用于显示）
- ✅ 文件类型（用于图标）
- ✅ 文件大小（用于显示）
- ❌ 不保存文件内容（节省空间）
- ❌ 不保存解析内容（已处理）

### 2. 按需加载

- 附件信息随消息一起加载
- 不需要额外的 API 请求
- 历史会话加载速度快

## 测试步骤

### 1. 测试当前会话附件显示

1. 启动应用
2. 上传附件（图片/PDF）
3. 发送消息
4. ✅ 验证：用户消息上方显示附件

### 2. 测试历史会话附件显示

1. 发送带附件的消息
2. 创建新会话
3. 点击历史会话
4. ✅ 验证：历史消息显示附件

### 3. 测试多附件

1. 上传多个附件
2. 发送消息
3. ✅ 验证：所有附件都显示

## 注意事项

### 1. 附件文件不保存

- 附件文件存储在 `data/attachments/`
- 会话中只保存附件元信息
- 清理会话不会删除附件文件

### 2. 附件 ID 唯一性

- 每个附件有唯一 ID
- 用于关联和引用
- 由系统自动生成

### 3. 向后兼容

- 旧会话没有 attachments 字段
- 前端使用 `attachments || undefined` 处理
- 不会影响旧会话的加载

## 未来改进

### 1. 附件预览

- 图片缩略图预览
- PDF 第一页预览
- 点击查看大图

### 2. 附件管理

- 下载附件
- 删除附件
- 替换附件

### 3. 附件统计

- 显示会话中附件数量
- 附件总大小统计
- 存储空间管理

## 相关文件

### 后端
- `agent/app/models/conversation.py` - 消息模型
- `agent/app/services/conversation_service.py` - 会话服务
- `agent/app/api/chat.py` - 聊天 API

### 前端
- `web/src/components/MessageAttachments.vue` - 附件组件
- `web/src/views/Chat.vue` - 聊天界面

## 总结

✅ 实现了完整的附件显示功能
✅ 当前会话实时显示附件
✅ 历史会话正确加载附件
✅ UI 美观，用户体验好
✅ 性能优化，存储高效
✅ 向后兼容，不影响旧数据

用户现在可以在会话中看到自己上传的所有附件！
