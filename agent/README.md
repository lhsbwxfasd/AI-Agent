# Enterprise Agent Backend

企业级 Agent 后端服务，支持知识库检索、MCP 工具调用和流式响应。

## 📖 完整安装指南

**新用户请先阅读**：[SETUP.md](SETUP.md) - 包含完整的安装步骤、配置说明和常见问题解决方案

**Python 版本要求**：Python 3.10.x 或 3.11.x（推荐 3.10.11）

## 功能特性

### 核心功能
- **多模型支持**：支持 GPT-4、GPT-3.5-Turbo、Claude-3 等多种模型，用户可自由切换
- **模型偏好记忆**：自动记住用户的模型选择，下次使用时自动应用
- **长对话支持**：支持对话摘要和滑动窗口，处理长对话历史
- **会话管理**：完整的会话历史记录，支持创建、编辑、删除会话
- **知识库支持**：基于 ChromaDB 的向量数据库，支持企业私有知识库
- **MCP 工具集成**：内置常用工具（天气、搜索、计算、翻译等），支持外部 MCP 服务器
- **流式响应**：支持 SSE 流式输出，提升用户体验
- **预置知识库**：内置企业常用知识库内容，一键初始化

### 企业级特性
- **JWT 认证**：完善的用户认证和授权机制
- **日志记录**：结构化日志，支持日志轮转和压缩
- **监控支持**：可集成 Prometheus 进行监控
- **错误处理**：完善的异常处理和降级机制

## 技术栈

- **后端框架**：FastAPI
- **异步运行时**：asyncio + uvicorn
- **向量数据库**：ChromaDB
- **LLM 集成**：LangChain
- **认证**：JWT + OAuth2
- **日志**：loguru

## 项目结构

```
agent/
├── app/
│   ├── api/              # API 路由
│   │   ├── auth.py          # 认证相关
│   │   ├── chat.py          # 聊天接口
│   │   ├── knowledge.py     # 知识库管理
│   │   └── conversation.py  # 会话管理
│   ├── core/            # 核心业务逻辑
│   │   ├── agent.py         # Agent 核心逻辑
│   │   ├── llm.py           # LLM 封装（支持多模型）
│   │   └── streaming.py     # 流式响应处理
│   ├── services/        # 服务层
│   │   ├── knowledge_service.py  # 知识库服务
│   │   ├── mcp_service.py        # MCP 服务
│   │   ├── mcp_tools.py          # 内置 MCP 工具
│   │   ├── conversation_service.py  # 会话管理服务
│   │   └── auth_service.py       # 认证服务
│   ├── models/          # 数据模型
│   │   ├── chat.py          # 聊天相关模型
│   │   ├── user.py          # 用户相关模型
│   │   └── conversation.py  # 会话相关模型
│   ├── middleware/      # 中间件
│   │   ├── auth.py      # 认证中间件
│   │   └── logging.py   # 日志中间件
│   └── utils/           # 工具函数
│       ├── logger.py    # 日志工具
│       └── helpers.py   # 辅助函数
├── scripts/             # 脚本目录
│   └── init_knowledge.py  # 知识库初始化脚本
├── data/                # 数据目录
│   ├── chroma/          # 向量数据库数据
│   └── conversations/   # 会话历史数据
├── logs/                # 日志目录
├── config.py            # 配置管理
├── main.py              # 应用入口
├── requirements.txt     # Python 依赖
├── .env                 # 环境变量
├── Dockerfile           # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
└── nginx.conf           # Nginx 配置
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，填入你的配置：

```env
# LLM 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4

# 认证配置
SECRET_KEY=your_secret_key_change_this_in_production
```

### 3. 初始化知识库（可选）

```bash
# 运行知识库初始化脚本
python scripts/init_knowledge.py
```

### 4. 启动服务

```bash
# 开发环境
python main.py

# 生产环境
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API 文档

启动服务后，访问 `http://localhost:8000/docs` 查看完整的 API 文档。

### 主要 API 端点

#### 认证

- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

#### 聊天

- `GET /api/v1/chat/models` - 获取可用模型列表
- `POST /api/v1/chat/completions` - 聊天完成（非流式）
- `POST /api/v1/chat/completions/stream` - 聊天完成（流式）

#### 会话管理

- `POST /api/v1/conversations/` - 创建新会话
- `GET /api/v1/conversations/` - 获取用户的所有会话
- `GET /api/v1/conversations/{conversation_id}` - 获取指定会话
- `PUT /api/v1/conversations/{conversation_id}` - 更新会话
- `DELETE /api/v1/conversations/{conversation_id}` - 删除会话
- `GET /api/v1/conversations/{conversation_id}/messages` - 获取会话的消息历史

#### 知识库

- `POST /api/v1/knowledge/documents` - 添加文本文档
- `POST /api/v1/knowledge/documents/batch` - 批量添加文档
- `POST /api/v1/knowledge/documents/upload` - 上传文件（PDF/DOCX/TXT）
- `DELETE /api/v1/knowledge/documents` - 删除文档
- `GET /api/v1/knowledge/info` - 获取知识库信息

#### 健康检查

- `GET /health` - 健康检查

## 使用示例

### 1. 用户登录

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. 添加知识库文档

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/documents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"content": "企业知识库示例文档内容", "metadata": {"source": "internal"}}'
```

### 3. 获取可用模型

```bash
curl -X GET http://localhost:8000/api/v1/chat/models
```

### 4. 流式聊天（指定模型和会话）

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "stream": true,
    "model": "gpt-4",
    "conversation_id": "existing-conversation-id"
  }'
```

### 5. 创建会话

```bash
curl -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"model": "gpt-4"}'
```

### 6. 获取会话历史

```bash
curl -X GET http://localhost:8000/api/v1/conversations/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. 前端集成示例

```javascript
async function streamChat(messages, token) {
    const response = await fetch('http://localhost:8000/api/v1/chat/completions/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            messages: messages,
            stream: true,
            model: "gpt-4",  // 指定模型
            conversation_id: conversationId,  // 指定会话ID
            use_knowledge: true,
            use_mcp: true
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'start') {
                    console.log('Stream started:', data.request_id);
                    console.log('Model:', data.model);
                    console.log('Conversation ID:', data.conversation_id);
                } else if (data.type === 'content') {
                    console.log('Content:', data.content);
                    // 更新 UI 显示内容
                } else if (data.type === 'end') {
                    console.log('Stream ended:', data.usage);
                }
            }
        }
    }
}
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | OpenAI API 密钥 | 必填 |
| OPENAI_BASE_URL | OpenAI API 基础 URL | https://api.openai.com/v1 |
| DEFAULT_MODEL | 默认模型 | gpt-4 |
| DEFAULT_TEMPERATURE | 默认温度 | 0.7 |
| MAX_TOKENS | 最大 token 数 | 2000 |
| CHROMA_PERSIST_DIR | ChromaDB 数据目录 | ./data/chroma |
| CHROMA_COLLECTION_NAME | ChromaDB 集合名称 | enterprise_knowledge |
| SECRET_KEY | JWT 密钥 | 必填 |
| MCP_SERVER_URL | MCP 服务器 URL（可选，不配置则使用内置工具） | http://localhost:3000 |
| LOG_LEVEL | 日志级别 | INFO |

### 多模型配置

在 `config.py` 中配置可用模型：

```python
available_models: Dict[str, Dict] = {
    "deepseek-chat": {"name": "DeepSeek Chat", "provider": "deepseek", "max_tokens": 4096},
    "deepseek-coder": {"name": "DeepSeek Coder", "provider": "deepseek", "max_tokens": 4096},
    "gpt-4": {"name": "GPT-4", "provider": "openai", "max_tokens": 8192},
    "gpt-3.5-turbo": {"name": "GPT-3.5 Turbo", "provider": "openai", "max_tokens": 4096},
    "claude-3-opus": {"name": "Claude 3 Opus", "provider": "anthropic", "max_tokens": 4096},
    "claude-3-sonnet": {"name": "Claude 3 Sonnet", "provider": "anthropic", "max_tokens": 4096},
}
```

**默认使用 DeepSeek**：
- 性价比高，中文支持优秀
- API Key: `sk-8c997adb962c4ba08df3728db6fdbdfd`
- Base URL: `https://api.deepseek.com`

### 长对话配置

在 `config.py` 中配置长对话处理：

```python
max_conversation_history: int = 20  # 最大对话历史轮数
enable_conversation_summary: bool = True  # 启用对话摘要
summary_threshold: int = 10  # 超过多少轮对话后进行摘要
```

## 默认账号

- 用户名：`admin`
- 密码：`admin123`

**注意**：生产环境请修改默认密码和密钥。

## 生产环境部署

### 1. 修改配置

- 修改 `.env` 中的 `SECRET_KEY` 为强随机密钥
- 修改默认用户密码
- 配置正确的 CORS 源
- 配置 HTTPS 证书

### 2. 使用 Gunicorn

```bash
pip install gunicorn

gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### 3. 使用 Nginx

参考 `nginx.conf` 配置文件，配置反向代理和负载均衡。

## 监控和日志

- 日志文件位于 `logs/app.log`
- 支持日志轮转和压缩
- 可集成 Prometheus 进行监控

## 新功能说明

### 1. 多模型切换

系统支持多种大语言模型，用户可以在请求中指定使用的模型：

```bash
# 获取可用模型列表
curl http://localhost:8000/api/v1/chat/models

# 在聊天请求中指定模型
curl -X POST http://localhost:8000/api/v1/chat/completions/stream \
  -H "Content-Type: application/json" \
  -d '{"messages": [...], "model": "gpt-3.5-turbo"}'
```

系统会记住用户的模型偏好，下次请求时自动使用该模型。

### 2. 长对话支持

系统通过两种方式处理长对话：

- **对话摘要**：当对话超过阈值时，自动生成对话摘要，保留关键信息
- **滑动窗口**：限制发送给 LLM 的消息数量，保留最近的对话历史

配置参数：
- `max_conversation_history`：最大对话历史轮数
- `enable_conversation_summary`：是否启用对话摘要
- `summary_threshold`：摘要生成阈值

### 3. 会话管理

完整的会话生命周期管理：

- 创建新会话时自动指定模型
- 会话历史持久化存储
- 支持会话的增删改查
- 可根据会话 ID 获取完整对话历史

### 4. 内置 MCP 工具

系统内置了常用的 MCP 工具，无需配置外部服务器即可使用：

- **天气查询**：查询指定城市的天气信息
- **网络搜索**：在网络上搜索信息（模拟）
- **计算器**：执行数学计算
- **日期时间**：获取当前日期时间或转换时区
- **文本格式化**：格式化文本（大小写、去除空格等）
- **字数统计**：统计文本的字数、字符数等
- **文本翻译**：翻译文本（模拟）

Agent 可以通过 `TOOL_CALL` 格式调用这些工具：

```
TOOL_CALL: weather|city=北京|unit=celsius
TOOL_CALL: calculate|expression=2+3*4
TOOL_CALL: datetime|format=iso
```

### 5. 预置知识库

运行初始化脚本可快速添加企业常用知识库内容：

```bash
python scripts/init_knowledge.py
```

预置内容包括：
- 公司简介
- 产品服务
- 技术架构
- 开发规范
- 常见问题FAQ
- 使用指南
- 安全与隐私
- 技术支持

## 故障排查

### 1. 导入错误

确保在 `agent` 目录下运行，或设置 `PYTHONPATH`：

```bash
export PYTHONPATH=/path/to/agent:$PYTHONPATH
```

### 2. ChromaDB 初始化失败

确保 `data/chroma` 目录有写入权限。

### 3. LLM 调用失败

检查 `.env` 中的 `OPENAI_API_KEY` 是否正确配置。

## 许可证

MIT License

## 联系方式

如有问题，请联系开发团队。
