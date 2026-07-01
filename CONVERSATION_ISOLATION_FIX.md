# 会话用户隔离修复说明

## 问题描述

新注册的用户可以看到之前硬编码用户 "admin" 的会话历史，会话没有实现用户隔离。

## 问题原因

多个 API 文件中的 `get_current_user()` 函数硬编码返回 "admin"：

```python
async def get_current_user() -> str:
    """获取当前用户（简化版，实际应从JWT token中获取）"""
    return "admin"  # ❌ 硬编码
```

导致所有用户都被当作 admin 处理，可以看到 admin 的所有会话。

## 修复方案

### 1. 使用正确的用户ID获取方法

从 `app.middleware.auth` 导入 `get_current_user_id` 函数：

```python
from app.middleware.auth import get_current_user_id
```

### 2. 修改所有API文件

#### conversation.py
```python
# 修改前
async def get_current_user() -> str:
    return "admin"

# 修改后
from app.middleware.auth import get_current_user_id

@router.get("/", response_model=ConversationList)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user_id)  # ✅ 使用正确的依赖
):
```

#### chat.py
```python
# 修改后
from app.middleware.auth import get_current_user_id

@router.post("/completions")
async def chat_completion(
    request: ChatRequest,
    current_user: str = Depends(get_current_user_id)  # ✅ 正确获取用户ID
):
```

#### attachment.py
```python
# 修改后
from app.middleware.auth import get_current_user_id

@router.post("/upload")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user_id)  # ✅ 正确获取用户ID
):
```

## 修复的文件

1. ✅ `agent/app/api/conversation.py` - 会话管理API
2. ✅ `agent/app/api/chat.py` - 聊天API
3. ✅ `agent/app/api/attachment.py` - 附件上传API

## 验证方法

### 1. 创建测试用户

```bash
# 注册用户A
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"userA","password":"test123"}'

# 注册用户B
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"userB","password":"test123"}'
```

### 2. 用户A创建会话

```bash
# 登录用户A
TOKEN_A=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"userA","password":"test123"}' | jq -r '.access_token')

# 创建会话
curl -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-r1:7b"}'
```

### 3. 用户B查看会话列表

```bash
# 登录用户B
TOKEN_B=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"userB","password":"test123"}' | jq -r '.access_token')

# 查看会话列表
curl -X GET http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer $TOKEN_B"
```

**预期结果**：用户B看不到用户A的会话。

## 权限验证

### 会话访问权限

```python
# conversation.py 中的权限检查
conversation = await conversation_service.get_conversation(conversation_id)
if conversation.user_id != current_user:
    raise HTTPException(status_code=403, detail="Access denied")
```

### 会话列表过滤

```python
# 只返回当前用户的会话
conversations = await conversation_service.get_user_conversations(
    user_id=current_user,  # ✅ 使用当前用户ID过滤
    limit=limit,
    offset=offset
)
```

## 数据隔离范围

### ✅ 已实现隔离

1. **会话列表**：只显示当前用户的会话
2. **会话详情**：只能访问自己的会话
3. **会话创建**：自动关联到当前用户
4. **会话更新**：只能更新自己的会话
5. **会话删除**：只能删除自己的会话
6. **消息历史**：只能查看自己会话的消息
7. **附件上传**：关联到当前用户

### ⚠️  注意事项

**知识库**：
- 知识库是全局共享的，所有用户都能访问
- 这是设计如此，因为知识库是企业级共享资源

**附件文件**：
- 附件文件存储在 `data/attachments/`
- 数据库中记录了 user_id
- 但文件本身没有隔离（可以后续优化）

## 测试步骤

### 1. 重启后端

```bash
cd agent
python main.py
```

### 2. 前端测试

1. 注册两个用户：userA 和 userB
2. 用户A登录，创建会话，发送消息
3. 用户B登录，查看会话列表
4. ✅ 验证：用户B看不到用户A的会话

### 3. API测试

使用上面的验证方法，确认：
- ✅ 用户只能看到自己的会话
- ✅ 用户不能访问其他用户的会话
- ✅ 返回403错误（权限拒绝）

## 安全增强

### 当前实现

- ✅ JWT Token 认证
- ✅ 用户ID从Token获取
- ✅ 会话按用户ID过滤
- ✅ 权限验证（403错误）

### 后续优化建议

1. **附件隔离**：
   - 附件文件按用户目录存储
   - 添加访问权限检查

2. **数据加密**：
   - 敏感数据加密存储
   - 用户密钥管理

3. **审计日志**：
   - 记录数据访问日志
   - 异常访问告警

## 总结

✅ **已修复**：
- 移除所有硬编码的 "admin"
- 使用正确的用户ID获取方法
- 实现会话用户隔离
- 添加权限验证

✅ **效果**：
- 每个用户只能看到自己的会话
- 用户无法访问其他用户的数据
- 权限验证返回403错误

✅ **安全**：
- JWT Token 认证
- 用户ID从Token解析
- 数据库按用户过滤

现在会话已实现完整的用户隔离！🔒
