# Enterprise Agent Frontend

企业级 Agent 前端应用，基于 Vue3 + Vite + Element Plus 构建。

## 功能特性

- **用户认证**：登录/登出功能，JWT Token 管理
- **智能聊天**：支持流式响应的聊天界面
- **模型切换**：支持多种 LLM 模型选择
- **会话管理**：创建、查看、删除会话，查看对话历史
- **知识库管理**：添加文本文档、上传文件（PDF/DOCX/TXT）
- **响应式设计**：适配不同屏幕尺寸
- **Markdown 支持**：消息内容支持 Markdown 渲染和代码高亮

## 技术栈

- **框架**：Vue 3 (Composition API)
- **构建工具**：Vite
- **UI 组件库**：Element Plus
- **路由**：Vue Router
- **状态管理**：Pinia
- **HTTP 客户端**：Axios
- **Markdown 渲染**：marked
- **代码高亮**：highlight.js

## 项目结构

```
web/
├── src/
│   ├── api/              # API 接口
│   │   ├── index.js     # Axios 配置
│   │   ├── auth.js      # 认证接口
│   │   ├── chat.js      # 聊天接口
│   │   ├── conversation.js  # 会话接口
│   │   └── knowledge.js # 知识库接口
│   ├── router/          # 路由配置
│   │   └── index.js
│   ├── stores/          # 状态管理
│   │   ├── auth.js      # 认证状态
│   │   └── chat.js      # 聊天状态
│   ├── views/           # 页面组件
│   │   ├── Login.vue    # 登录页
│   │   ├── Chat.vue     # 聊天页
│   │   ├── Conversations.vue  # 会话管理页
│   │   └── Knowledge.vue     # 知识库管理页
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
├── package.json         # 依赖配置
└── README.md            # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
cd web
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

构建产物位于 `dist/` 目录。

### 4. 预览生产构建

```bash
npm run preview
```

## 配置说明

### API 代理

开发环境下，Vite 配置了 API 代理，将 `/api` 请求转发到后端服务器：

```javascript
// vite.config.js
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 后端地址

生产环境部署时，需要修改 API 基础地址：

```javascript
// src/api/index.js
const api = axios.create({
  baseURL: '/api/v1',  // 修改为实际的后端地址
  timeout: 30000
})
```

## 使用说明

### 1. 登录

使用默认账号登录：
- 用户名：`admin`
- 密码：`admin123`

### 2. 聊天

- 点击"新对话"创建新会话
- 在输入框中输入消息，按 Ctrl+Enter 或点击"发送"按钮
- 支持选择不同的模型
- 支持查看历史会话

### 3. 会话管理

- 查看所有会话列表
- 查看会话详情和消息历史
- 删除不需要的会话

### 4. 知识库管理

- 添加文本文档到知识库
- 上传 PDF、DOCX、TXT 文件
- 查看知识库统计信息

## API 接口

### 认证接口

```javascript
import { authApi } from '@/api/auth'

// 登录
await authApi.login({ username, password })

// 获取当前用户
await authApi.getCurrentUser()
```

### 聊天接口

```javascript
import { chatApi } from '@/api/chat'

// 获取可用模型
await chatApi.getModels()

// 流式聊天
await chatApi.chatStream(
  { messages, model, conversation_id },
  onMessage,
  onError,
  onComplete
)
```

### 会话接口

```javascript
import { conversationApi } from '@/api/conversation'

// 创建会话
await conversationApi.create({ model })

// 获取会话列表
await conversationApi.list({ limit, offset })

// 获取会话消息
await conversationApi.getMessages(id)

// 删除会话
await conversationApi.delete(id)
```

### 知识库接口

```javascript
import { knowledgeApi } from '@/api/knowledge'

// 添加文档
await knowledgeApi.addDocument({ content, metadata })

// 上传文件
await knowledgeApi.uploadFile(file, metadata)

// 获取知识库信息
await knowledgeApi.getInfo()
```

## 状态管理

### 认证状态

```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 登录
await authStore.login(username, password)

// 登出
authStore.logout()

// 检查认证状态
console.log(authStore.isAuthenticated)
```

### 聊天状态

```javascript
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

// 加载模型
await chatStore.loadModels()

// 添加消息
chatStore.addMessage('user', 'Hello')

// 清空消息
chatStore.clearMessages()
```

## 开发建议

### 1. 代码风格

- 使用 Vue 3 Composition API
- 使用 `<script setup>` 语法
- 遵循 ESLint 规则

### 2. 组件开发

- 组件文件使用 PascalCase 命名
- 组件内部使用 kebab-case 命名
- Props 和 Emits 明确定义类型

### 3. 样式

- 使用 scoped CSS 避免样式污染
- 优先使用 Element Plus 组件样式
- 自定义样式使用 BEM 命名规范

## 部署

### Docker 部署

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 常见问题

### 1. 跨域问题

开发环境使用 Vite 代理解决，生产环境需要配置 Nginx 反向代理。

### 2. Token 过期

Token 过期后会自动跳转到登录页面，需要重新登录。

### 3. 流式响应中断

检查网络连接和后端服务状态，确保 SSE 连接正常。

## 许可证

MIT License
