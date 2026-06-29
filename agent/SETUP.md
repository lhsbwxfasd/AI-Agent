# 企业级 Agent 后端 - 完整安装指南

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细安装步骤](#详细安装步骤)
- [配置说明](#配置说明)
- [启动应用](#启动应用)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 环境要求

### 必需环境

| 项目 | 版本要求 | 说明 |
|------|---------|------|
| **Python** | 3.10.x 或 3.11.x | 推荐 3.10.11 |
| **操作系统** | Windows 10/11 | 或 Linux/macOS |
| **内存** | ≥ 4GB | 模型加载需要 |
| **磁盘** | ≥ 2GB | 依赖和模型缓存 |

### Python 版本说明

**推荐版本**：Python 3.10.11

**为什么选择 3.10？**
- ✅ 支持 `list[str]` 类型注解（chromadb 需要）
- ✅ 自带 sqlite3 3.37+（chromadb 0.4.x 需要）
- ✅ 完全兼容 pydantic v2
- ✅ pip 可以直接安装所有依赖
- ✅ 长期支持到 2026-10

**不推荐的版本**：
- ❌ Python 3.6/3.7：已停止维护
- ❌ Python 3.8：sqlite3 版本过低
- ⚠️ Python 3.12：部分库可能不兼容

---

## 快速开始

### 一键安装（推荐）

```powershell
# 1. 确保已安装 Python 3.10.11
python --version
# 应该显示：Python 3.10.11

# 2. 进入项目目录
cd D:\测试项目\AI2\agent

# 3. 创建虚拟环境
python -m venv venv

# 4. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 5. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 6. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入必要配置

# 7. 启动应用
python main.py
```

### 首次启动

首次启动会自动下载模型（约 470MB），需要等待 2-5 分钟。

启动成功后访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 详细安装步骤

### 步骤1：安装 Python 3.10.11

#### 方法A：从官网下载（推荐）

1. **下载 Python**
   ```
   https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
   ```

2. **安装**
   - 运行下载的安装程序
   - ✅ **勾选 "Add Python 3.10 to PATH"**（非常重要！）
   - ✅ 勾选 "Install pip"
   - 点击 "Install Now"

3. **验证**
   ```powershell
   # 打开新的 PowerShell 窗口
   python --version
   # 应该显示：Python 3.10.11
   
   pip --version
   # 应该显示 pip 版本
   ```

#### 方法B：使用 pyenv-win（多版本管理）

如果需要管理多个 Python 版本：

1. **安装 pyenv-win**
   ```powershell
   # 使用 pip 安装
   pip install pyenv-win --target "$env:USERPROFILE\.pyenv"
   
   # 添加环境变量
   [Environment]::SetEnvironmentVariable("PYENV_ROOT", "$env:USERPROFILE\.pyenv\pyenv-win", "User")
   [Environment]::SetEnvironmentVariable("PATH", "$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims;$env:PATH", "User")
   
   # 重启 PowerShell
   ```

2. **安装 Python 3.10.11**
   ```powershell
   pyenv install 3.10.11
   pyenv global 3.10.11
   python --version
   ```

---

### 步骤2：创建虚拟环境

```powershell
# 进入项目目录
cd D:\测试项目\AI2\agent

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows PowerShell）
.\venv\Scripts\Activate.ps1

# 激活虚拟环境（Windows CMD）
venv\Scripts\activate.bat

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate
```

---

### 步骤3：安装依赖

```powershell
# 升级 pip
python -m pip install --upgrade pip setuptools wheel

# 安装项目依赖（使用清华镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用默认源
pip install -r requirements.txt
```

**安装时间**：约 3-5 分钟

**依赖列表**：
- fastapi：Web 框架
- chromadb：向量数据库
- sentence-transformers：文本嵌入
- langchain：LLM 集成
- 其他工具库

---

### 步骤4：配置环境变量

```powershell
# 复制配置模板
copy .env.example .env

# 编辑配置文件
notepad .env
```

**必需配置**：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 认证密钥（用于 JWT）
SECRET_KEY=your_secret_key_here_minimum_32_characters

# 其他配置（已有默认值）
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2000
```

**生成 SECRET_KEY**：
```powershell
# 使用 Python 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 步骤5：初始化知识库（可选）

如果需要预置知识库数据：

```powershell
python scripts\init_knowledge.py
```

这会添加 8 个预置知识库：
- 公司介绍
- 产品服务
- 技术架构
- 开发规范
- 常见问题 FAQ
- 使用指南
- 安全隐私
- 技术支持

---

## 配置说明

### 环境变量配置

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| OPENAI_API_KEY | ✅ | - | OpenAI API 密钥 |
| SECRET_KEY | ✅ | - | JWT 密钥 |
| OPENAI_BASE_URL | ❌ | https://api.openai.com/v1 | API 地址 |
| DEFAULT_MODEL | ❌ | gpt-4 | 默认模型 |
| DEFAULT_TEMPERATURE | ❌ | 0.7 | 温度参数 |
| MAX_TOKENS | ❌ | 2000 | 最大 token |
| PORT | ❌ | 8000 | 服务端口 |
| LOG_LEVEL | ❌ | INFO | 日志级别 |

### 可用模型

系统支持以下模型：

- **deepseek-chat**：DeepSeek Chat（默认推荐）
- **deepseek-coder**：DeepSeek Coder（代码专用）
- **gpt-4**：GPT-4
- **gpt-3.5-turbo**：GPT-3.5 Turbo
- **claude-3-opus**：Claude 3 Opus
- **claude-3-sonnet**：Claude 3 Sonnet

### DeepSeek 配置

默认使用 DeepSeek 模型，配置如下：

```env
OPENAI_API_KEY=sk-8c997adb962c4ba08df3728db6fdbdfd
OPENAI_BASE_URL=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
```

**DeepSeek 模型优势**：
- ✅ 性价比高（比 GPT-4 便宜很多）
- ✅ 中文支持优秀
- ✅ 性能接近 GPT-3.5
- ✅ 支持长上下文

---

## 启动应用

### 开发模式启动

```powershell
# 确保虚拟环境已激活
.\venv\Scripts\Activate.ps1

# 启动应用
python main.py
```

### 启动日志

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Loading sentence-transformers model...
INFO:     Model loaded successfully
INFO:     Knowledge service initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 生产模式启动

```powershell
# 使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用 gunicorn（Linux）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 验证安装

### 1. 健康检查

```powershell
# 使用 curl
curl http://localhost:8000/health

# 或在浏览器访问
# http://localhost:8000/health
```

**预期响应**：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. API 文档

访问：http://localhost:8000/docs

可以看到所有 API 端点和交互式文档。

### 3. 登录测试

**使用 curl**：
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username": "admin", "password": "admin123"}'
```

**使用 Swagger UI**：
1. 访问 http://localhost:8000/docs
2. 找到 `/api/v1/auth/login`
3. 点击 "Try it out"
4. 输入：`{"username": "admin", "password": "admin123"}`
5. 点击 "Execute"

**预期响应**：
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@example.com",
    "preferred_model": "gpt-4"
  }
}
```

### 4. 聊天测试

1. 使用上面的 token
2. 点击页面顶部的 "Authorize"
3. 输入：`Bearer YOUR_TOKEN`
4. 测试 `/api/v1/chat/completions`

---

## 常见问题

### Q1: Python 版本不对

**问题**：`python --version` 显示的不是 3.10.x

**解决**：
```powershell
# 方法1：检查 PATH
where.exe python

# 方法2：使用完整路径
& "C:\Python310\python.exe" -m venv venv

# 方法3：使用 pyenv
pyenv global 3.10.11
```

### Q2: 依赖安装失败

**问题**：pip install 报错

**解决**：
```powershell
# 1. 升级 pip
python -m pip install --upgrade pip setuptools wheel

# 2. 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 清除缓存重试
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### Q3: 模型下载超时

**问题**：启动时卡在 "Retrying..."

**解决**：
```powershell
# 方法1：使用代理
$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
python main.py

# 方法2：等待自动下载（已配置镜像）
# 首次下载约 2-5 分钟

# 方法3：手动下载模型
# 访问：https://hf-mirror.com/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# 下载所有文件到：~/.cache/huggingface/hub/
```

### Q4: 端口被占用

**问题**：`Address already in use`

**解决**：
```powershell
# 1. 查看端口占用
netstat -ano | findstr :8000

# 2. 结束占用进程
taskkill /PID <进程ID> /F

# 3. 或修改端口
# 编辑 .env 文件
PORT=8001
```

### Q5: 认证失败

**问题**：`401 Unauthorized`

**解决**：
```powershell
# 1. 确认 token 格式
Authorization: Bearer YOUR_TOKEN

# 2. 检查 token 是否过期
# 默认有效期 30 分钟

# 3. 重新登录获取新 token
```

### Q6: 内存不足

**问题**：启动时内存错误

**解决**：
```powershell
# 1. 关闭其他应用

# 2. 使用更小的模型
# 编辑 app/services/knowledge_service.py
# 将模型改为：'paraphrase-MiniLM-L3-v2'（22MB）
```

---

## 项目结构

```
enterprise-agent-backend/
├── .env                          # 环境变量配置
├── .env.example                  # 配置模板
├── requirements.txt              # Python 依赖
├── README.md                     # 项目说明
├── SETUP.md                      # 本文档
├── main.py                       # 应用入口
├── config.py                     # 配置管理
├── app/
│   ├── api/                      # API 路由
│   │   ├── auth.py               # 认证接口
│   │   ├── chat.py               # 聊天接口
│   │   ├── conversation.py       # 会话管理
│   │   └── knowledge.py          # 知识库管理
│   ├── core/                     # 核心业务
│   │   ├── agent.py              # Agent 核心
│   │   ├── llm.py                # LLM 封装
│   │   └── streaming.py          # 流式响应
│   ├── services/                 # 服务层
│   │   ├── auth_service.py       # 认证服务
│   │   ├── conversation_service.py # 会话服务
│   │   ├── knowledge_service.py  # 知识库服务
│   │   ├── mcp_service.py        # MCP 服务
│   │   └── mcp_tools.py          # MCP 工具
│   ├── models/                   # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── chat.py               # 聊天模型
│   │   └── conversation.py       # 会话模型
│   ├── middleware/               # 中间件
│   │   ├── auth.py               # 认证中间件
│   │   └── logging.py            # 日志中间件
│   └── utils/                    # 工具函数
│       ├── logger.py             # 日志工具
│       ├── helpers.py            # 辅助函数
│       └── sqlite3_patch.py      # SQLite 补丁
├── scripts/                      # 脚本
│   └── init_knowledge.py         # 初始化知识库
├── data/                         # 数据目录
│   ├── chroma/                   # 向量数据库
│   └── conversations/            # 会话数据
├── logs/                         # 日志目录
└── venv/                         # 虚拟环境
```

---

## 功能特性

### 已实现功能

- ✅ **多模型支持**：GPT-4、GPT-3.5、Claude 等
- ✅ **模型切换**：用户可自由选择模型
- ✅ **偏好持久化**：记住用户上次选择的模型
- ✅ **长对话支持**：自动摘要和历史截断
- ✅ **会话管理**：创建、查询、删除会话
- ✅ **历史记录**：完整的对话历史
- ✅ **知识库**：ChromaDB 向量检索
- ✅ **文档上传**：支持 PDF、DOCX、TXT
- ✅ **MCP 工具**：7 个常用工具
- ✅ **流式响应**：SSE 实时输出
- ✅ **认证授权**：JWT Token
- ✅ **API 文档**：Swagger UI

### MCP 工具列表

1. **weather**：天气查询
2. **search**：网络搜索
3. **calculate**：数学计算
4. **datetime**：日期时间
5. **format**：文本格式化
6. **count**：字数统计
7. **translate**：文本翻译

---

## API 端点

### 认证
- `POST /api/v1/auth/login` - 登录
- `GET /api/v1/auth/me` - 获取当前用户
- `PUT /api/v1/auth/me/preferred-model` - 更新偏好模型

### 聊天
- `GET /api/v1/chat/models` - 获取模型列表
- `POST /api/v1/chat/completions` - 聊天（非流式）
- `POST /api/v1/chat/completions/stream` - 聊天（流式）

### 会话
- `POST /api/v1/conversations/` - 创建会话
- `GET /api/v1/conversations/` - 获取会话列表
- `GET /api/v1/conversations/{id}` - 获取会话详情
- `PUT /api/v1/conversations/{id}` - 更新会话
- `DELETE /api/v1/conversations/{id}` - 删除会话
- `GET /api/v1/conversations/{id}/messages` - 获取消息历史

### 知识库
- `POST /api/v1/knowledge/documents` - 添加文档
- `POST /api/v1/knowledge/documents/batch` - 批量添加
- `POST /api/v1/knowledge/documents/upload` - 上传文件
- `DELETE /api/v1/knowledge/documents` - 删除文档
- `GET /api/v1/knowledge/info` - 获取知识库信息

---

## 下一步

### 开发

1. 查看 API 文档：http://localhost:8000/docs
2. 测试各个接口
3. 根据需求修改代码

### 部署

1. 使用 Docker 部署（参考 Dockerfile）
2. 使用 Docker Compose（参考 docker-compose.yml）
3. 配置 Nginx 反向代理

### 监控

1. 访问健康检查端点
2. 查看日志：`logs/app.log`
3. 配置 Prometheus 监控

---

## 技术支持

如遇问题，请查看：
1. 本文档的常见问题部分
2. 项目 README.md
3. 日志文件：`logs/app.log`

---

## 更新日志

### v1.0.0 (2024-06-29)

**新增功能**：
- 多模型支持和切换
- 用户偏好持久化
- 长对话摘要
- 会话管理
- 知识库集成
- MCP 工具
- 流式响应

**技术栈**：
- Python 3.10.11
- FastAPI 0.104.1
- ChromaDB 0.4.22
- LangChain 0.1.0
- Pydantic 2.5.0
