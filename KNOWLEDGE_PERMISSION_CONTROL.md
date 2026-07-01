# 知识库权限控制实现说明

## 功能概述

实现了基于角色的权限控制，知识库只有管理员才能访问。

## 实现的功能

### 1. 后端权限验证

#### 添加权限验证函数 (auth.py)

**`get_current_user_role()`**：
- 获取当前用户ID和角色
- 返回：`(user_id, is_admin)`

**`require_admin()`**：
- 要求管理员权限
- 非管理员返回 403 错误

```python
async def require_admin(request: Request) -> str:
    """要求管理员权限"""
    user_id, is_admin = await get_current_user_role(request)
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_id
```

#### 修改知识库API (knowledge.py)

所有知识库接口添加权限验证：

```python
from app.middleware.auth import require_admin

@router.post("/documents")
async def add_document(
    content: str,
    metadata: Optional[dict] = None,
    doc_id: Optional[str] = None,
    user_id: str = Depends(require_admin)  # ✅ 管理员权限
):
    # 只有管理员能访问
```

**修改的接口**：
- ✅ `POST /documents` - 添加文档
- ✅ `POST /documents/batch` - 批量添加
- ✅ `POST /documents/upload` - 上传文件
- ✅ `DELETE /documents` - 删除文档
- ✅ `GET /info` - 获取知识库信息

### 2. 前端权限控制

#### 修改 auth store (auth.js)

添加角色相关计算属性：

```javascript
const isAdmin = computed(() => {
  return user.value?.is_admin === true
})

const username = computed(() => {
  return user.value?.username || ''
})
```

#### 修改菜单显示 (Chat.vue)

根据角色显示/隐藏菜单：

```vue
<el-dropdown-menu>
  <el-dropdown-item command="conversations">会话管理</el-dropdown-item>
  <el-dropdown-item v-if="authStore.isAdmin" command="knowledge">知识库</el-dropdown-item>
  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
</el-dropdown-menu>
```

## 权限验证流程

### 后端验证

```
用户请求知识库API
  ↓
检查 Authorization header
  ↓
解析 JWT Token
  ↓
获取用户ID
  ↓
查询数据库用户角色
  ↓
判断 is_admin
  ├─ True → 允许访问
  └─ False → 返回 403 Forbidden
```

### 前端控制

```
用户登录
  ↓
获取用户信息（包含 is_admin）
  ↓
保存到 authStore
  ↓
渲染菜单时检查 authStore.isAdmin
  ├─ True → 显示知识库菜单
  └─ False → 隐藏知识库菜单
```

## 使用示例

### 1. 管理员访问知识库

```bash
# 管理员登录
TOKEN=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 访问知识库（✅ 成功）
curl -X GET http://localhost:8000/api/v1/knowledge/info \
  -H "Authorization: Bearer $TOKEN"
```

### 2. 普通用户访问知识库

```bash
# 普通用户登录
TOKEN=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"test123"}' | jq -r '.access_token')

# 访问知识库（❌ 失败）
curl -X GET http://localhost:8000/api/v1/knowledge/info \
  -H "Authorization: Bearer $TOKEN"

# 返回：
# {
#   "detail": "Admin access required"
# }
```

## 错误响应

### 401 Unauthorized

未登录或Token无效：

```json
{
  "detail": "Missing authorization header"
}
```

### 403 Forbidden

非管理员访问：

```json
{
  "detail": "Admin access required"
}
```

## 前端效果

### 管理员用户

```
┌─────────────────┐
│ 👤 admin        │
│ ├─ 会话管理     │
│ ├─ 知识库       │ ← ✅ 显示
│ └─ 退出登录     │
└─────────────────┘
```

### 普通用户

```
┌─────────────────┐
│ 👤 user         │
│ ├─ 会话管理     │
│ └─ 退出登录     │
└─────────────────┘
```
知识库菜单不显示

## 数据库字段

### users 表

```sql
is_admin INTEGER DEFAULT 0
```

- `0` - 普通用户
- `1` - 管理员

## 设置管理员

### 方式1：使用初始化脚本

```bash
python init_admin.py
```

自动设置 is_admin = 1

### 方式2：手动修改数据库

```sql
-- SQLite
sqlite3 data/db.sqlite3
UPDATE users SET is_admin = 1 WHERE username = 'username';

-- MySQL
UPDATE users SET is_admin = 1 WHERE username = 'username';
```

### 方式3：创建用户时设置

修改 `user_service.py` 的 `register` 方法：

```python
# 创建用户时设置管理员
user = UserModel(
    id=user_id,
    username=username,
    password_hash=password_hash,
    is_admin=1  # 设置为管理员
)
```

## 测试步骤

### 1. 创建测试用户

```bash
# 创建普通用户
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"normaluser","password":"test123"}'

# 管理员已通过 init_admin.py 创建
```

### 2. 测试后端权限

```bash
# 普通用户访问知识库
TOKEN=$(curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"normaluser","password":"test123"}' | jq -r '.access_token')

curl -X GET http://localhost:8000/api/v1/knowledge/info \
  -H "Authorization: Bearer $TOKEN"

# 预期：403 Forbidden
```

### 3. 测试前端显示

1. 普通用户登录
2. 查看用户菜单
3. ✅ 验证：看不到"知识库"菜单项

4. 管理员登录
5. 查看用户菜单
6. ✅ 验证：能看到"知识库"菜单项

## 扩展建议

### 1. 角色系统

可以扩展为多角色系统：

```python
class UserRole:
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
```

### 2. 权限装饰器

```python
def require_role(roles: List[str]):
    """要求特定角色"""
    async def decorator(request: Request):
        user_role = await get_user_role(request)
        if user_role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user_role
    return decorator

@router.get("/resource")
async def get_resource(
    user_id: str = Depends(require_role(["admin", "editor"]))
):
    # admin 和 editor 都能访问
```

### 3. 资源级权限

```python
# 每个资源有所有者
class Resource:
    id: str
    owner_id: str
    # ...

# 访问时验证所有权
if resource.owner_id != current_user and not is_admin:
    raise HTTPException(status_code=403, detail="Access denied")
```

## 修改的文件

### 后端
1. ✅ `app/middleware/auth.py` - 添加权限验证函数
2. ✅ `app/api/knowledge.py` - 添加权限验证

### 前端
3. ✅ `web/src/stores/auth.js` - 添加角色计算属性
4. ✅ `web/src/views/Chat.vue` - 根据角色显示菜单

## 总结

✅ **已实现**：
- 后端权限验证
- 前端菜单控制
- 管理员角色判断
- 403 错误返回

✅ **效果**：
- 管理员可以访问知识库
- 普通用户无法访问知识库
- 前端菜单根据角色显示

✅ **安全**：
- JWT Token 验证
- 数据库角色查询
- 权限装饰器
- 前后端双重验证

现在知识库已实现管理员专属访问！🔒
