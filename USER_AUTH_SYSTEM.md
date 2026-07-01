# 用户认证系统实现说明

## 功能概述

实现了完整的用户认证系统，包括：
- 用户注册
- 用户登录
- 用户信息管理
- 密码加密存储
- JWT Token 认证

## 实现的功能

### 1. 用户数据库模型

#### users 表
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active INTEGER DEFAULT 1,
    is_admin INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    last_login DATETIME,
    preferred_model VARCHAR(100),
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

### 2. 用户服务 (user_service.py)

**功能**：
- ✅ 用户注册
- ✅ 用户登录
- ✅ 密码加密（bcrypt）
- ✅ JWT Token 生成
- ✅ 用户信息查询
- ✅ 用户信息更新
- ✅ 用户列表（管理员）
- ✅ 禁用/激活用户（管理员）

### 3. 用户 API (users.py)

**接口**：
- `POST /api/v1/users/register` - 用户注册
- `POST /api/v1/users/login` - 用户登录
- `GET /api/v1/users/me` - 获取当前用户
- `PUT /api/v1/users/me` - 更新当前用户
- `GET /api/v1/users/list` - 用户列表（管理员）
- `POST /api/v1/users/{id}/deactivate` - 禁用用户（管理员）
- `POST /api/v1/users/{id}/activate` - 激活用户（管理员）

### 4. 前端页面

#### 注册页面 (Register.vue)
- 用户名（必填，3-100字符）
- 密码（必填，至少6字符）
- 确认密码
- 邮箱（可选）
- 姓名（可选）

#### 登录页面 (Login.vue)
- 用户名
- 密码
- 注册链接

## 使用步骤

### 1. 初始化数据库

```bash
cd agent
python test_database.py
```

这会创建所有表，包括 users 表。

### 2. 创建管理员用户

```bash
python init_admin.py
```

按提示输入：
- 管理员密码（默认：admin123）
- 管理员邮箱（可选）

**输出示例**：
```
============================================================
Initialize Admin User
============================================================

1. Initializing database...
   ✅ Database initialized

2. Checking if admin exists...
   ℹ️  Admin user does not exist

3. Creating admin user...
Enter admin password (default: admin123): 
Enter admin email (optional): admin@example.com
   ✅ Admin user created successfully
      Username: admin
      Password: admin123
      Email: admin@example.com

============================================================
Initialization completed!
============================================================

You can now login with:
  Username: admin
  Password: admin123
```

### 3. 启动应用

```bash
# 后端
python main.py

# 前端
cd ../web
npm run dev
```

### 4. 使用应用

#### 方式1：使用管理员账号

访问 http://localhost:3000/login
- 用户名：admin
- 密码：admin123（或你设置的密码）

#### 方式2：注册新用户

访问 http://localhost:3000/register
- 填写注册信息
- 提交注册
- 跳转到登录页面

## API 使用示例

### 注册

```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com",
    "full_name": "Test User"
  }'
```

### 登录

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "abc-123-def",
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_admin": false
  }
}
```

### 获取当前用户

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 更新用户信息

```bash
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "New Name",
    "preferred_model": "deepseek-r1:7b"
  }'
```

## 数据流程

### 注册流程

```
用户填写注册信息
  ↓
前端验证
  ↓
POST /api/v1/users/register
  ↓
后端检查用户名/邮箱是否存在
  ↓
密码加密（bcrypt）
  ↓
保存到数据库
  ↓
返回成功
  ↓
跳转到登录页面
```

### 登录流程

```
用户输入用户名和密码
  ↓
POST /api/v1/users/login
  ↓
后端查询用户
  ↓
验证密码（bcrypt）
  ↓
生成 JWT Token
  ↓
更新最后登录时间
  ↓
返回 Token 和用户信息
  ↓
前端保存 Token
  ↓
跳转到主页
```

## 安全特性

### 1. 密码加密

使用 bcrypt 算法：
- 自动加盐
- 单向加密
- 防止彩虹表攻击

```python
# 加密
password_hash = pwd_context.hash(password)

# 验证
is_valid = pwd_context.verify(plain_password, hashed_password)
```

### 2. JWT Token

- 有效期：30分钟（可配置）
- 包含：用户ID、用户名
- 签名：使用 SECRET_KEY

### 3. 权限控制

- 普通用户：只能访问自己的数据
- 管理员：可以管理所有用户
- Token 验证：每个请求都验证

## 文件结构

```
agent/
├── app/
│   ├── db/
│   │   └── database.py          # 用户模型
│   ├── services/
│   │   └── user_service.py      # 用户服务
│   ├── api/
│   │   └── users.py             # 用户API
│   └── middleware/
│       └── auth.py              # 认证中间件
├── init_admin.py                # 初始化管理员
└── test_database.py             # 数据库测试

web/
├── src/
│   ├── views/
│   │   ├── Login.vue            # 登录页面
│   │   └── Register.vue         # 注册页面
│   ├── api/
│   │   └── auth.js              # 认证API
│   └── router/
│       └── index.js             # 路由配置
```

## 配置说明

### 密钥配置

`.env` 文件：
```bash
SECRET_KEY=your_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**重要**：生产环境必须修改 SECRET_KEY！

### 生成安全的密钥

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 常见问题

### Q1: 忘记管理员密码？

运行初始化脚本：
```bash
python init_admin.py
```

选择更新密码。

### Q2: 如何添加管理员？

方法1：注册后手动修改数据库：
```sql
UPDATE users SET is_admin = 1 WHERE username = 'username';
```

方法2：使用 init_admin.py 脚本。

### Q3: Token 过期怎么办？

重新登录获取新 Token。

### Q4: 如何修改密码？

调用更新用户API：
```bash
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer TOKEN" \
  -d '{"password": "new_password"}'
```

## 测试

### 1. 测试数据库

```bash
python test_database.py
```

### 2. 测试注册

```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

### 3. 测试登录

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

## 生产环境建议

### 1. 安全配置

- ✅ 修改 SECRET_KEY
- ✅ 使用 HTTPS
- ✅ 启用 CORS 白名单
- ✅ 密码复杂度要求

### 2. 性能优化

- ✅ Token 缓存
- ✅ 数据库索引
- ✅ 连接池配置

### 3. 监控

- 登录日志
- 失败尝试限制
- 异常登录告警

## 总结

✅ **已完成**：
- 用户数据库模型
- 用户服务（注册、登录、管理）
- 用户 API 接口
- 前端注册页面
- 前端登录页面
- 初始化管理员脚本
- JWT Token 认证
- 密码加密存储

✅ **特性**：
- 完整的用户认证流程
- 安全的密码存储
- Token 过期机制
- 用户信息管理
- 管理员功能

✅ **下一步**：
1. 运行 `python init_admin.py` 创建管理员
2. 启动应用
3. 注册或登录使用

现在用户认证系统已完全实现！🎉
