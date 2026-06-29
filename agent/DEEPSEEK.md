# DeepSeek 模型配置说明

## 配置信息

### API 配置

```env
OPENAI_API_KEY=sk-8c997adb962c4ba08df3728db6fdbdfd
OPENAI_BASE_URL=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
```

### 可用模型

1. **deepseek-chat**（默认）
   - 通用对话模型
   - 中文支持优秀
   - 性价比高
   - 适合大多数场景

2. **deepseek-coder**
   - 代码专用模型
   - 编程能力强
   - 适合代码生成、调试

---

## 使用方式

### 1. 默认使用

无需指定模型，系统自动使用 `deepseek-chat`：

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好"}]}'
```

### 2. 指定模型

在请求中指定模型：

```bash
# 使用 deepseek-coder
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "写一个 Python 函数"}],
    "model": "deepseek-coder"
  }'

# 使用 gpt-4（如果有 API Key）
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "model": "gpt-4"
  }'
```

### 3. 查看可用模型

```bash
curl http://localhost:8000/api/v1/chat/models
```

返回：
```json
{
  "models": {
    "deepseek-chat": {"name": "DeepSeek Chat", "provider": "deepseek", "max_tokens": 4096},
    "deepseek-coder": {"name": "DeepSeek Coder", "provider": "deepseek", "max_tokens": 4096},
    "gpt-4": {...},
    "gpt-3.5-turbo": {...},
    ...
  },
  "default": "deepseek-chat"
}
```

---

## DeepSeek 优势

### 1. 性价比高

| 模型 | 价格（每 1M tokens） | 性能 |
|------|---------------------|------|
| DeepSeek Chat | ¥1（输入）/ ¥2（输出） | 接近 GPT-3.5 |
| GPT-3.5 Turbo | $0.5（输入）/ $1.5（输出） | 基准 |
| GPT-4 | $10（输入）/ $30（输出） | 最强 |

**DeepSeek 比 GPT-4 便宜约 50 倍！**

### 2. 中文支持优秀

- 原生中文训练
- 中文理解能力强
- 中文生成流畅
- 适合中文场景

### 3. 性能良好

- 响应速度快
- 推理能力强
- 上下文理解好
- 支持长对话

### 4. 功能完整

- 支持流式输出
- 支持工具调用
- 支持多轮对话
- API 兼容 OpenAI

---

## 切换到其他模型

### 切换到 GPT-4

修改 `.env` 文件：

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_MODEL=gpt-4
```

### 切换到 Claude

修改 `.env` 文件：

```env
OPENAI_API_KEY=your_anthropic_api_key
OPENAI_BASE_URL=https://api.anthropic.com/v1
DEFAULT_MODEL=claude-3-opus
```

---

## 最佳实践

### 1. 场景选择

- **日常对话**：`deepseek-chat`
- **代码开发**：`deepseek-coder`
- **复杂推理**：`gpt-4`（如果有 API Key）
- **快速响应**：`gpt-3.5-turbo`

### 2. 成本优化

- 优先使用 DeepSeek
- 复杂任务才用 GPT-4
- 测试时用 DeepSeek
- 生产环境根据需求选择

### 3. 性能优化

- 使用流式输出提升体验
- 合理设置 max_tokens
- 使用知识库减少 token 消耗

---

## 测试验证

### 1. 测试 DeepSeek Chat

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "请介绍一下你自己"}
    ]
  }'
```

### 2. 测试 DeepSeek Coder

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "写一个 Python 快速排序算法"}
    ],
    "model": "deepseek-coder"
  }'
```

### 3. 测试中文理解

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "解释一下量子计算的原理"}
    ]
  }'
```

---

## 常见问题

### Q1: DeepSeek API 调用失败

**检查**：
1. API Key 是否正确
2. Base URL 是否正确（`https://api.deepseek.com`）
3. 网络是否可访问

### Q2: 响应速度慢

**原因**：
- DeepSeek 服务器在国内，速度较快
- 如果慢，可能是网络问题

**解决**：
- 检查网络连接
- 使用代理（如需要）

### Q3: 如何查看 token 使用量

响应中包含 usage 信息：

```json
{
  "content": "...",
  "model": "deepseek-chat",
  "usage": {
    "total_tokens": 150
  }
}
```

---

## 总结

**DeepSeek 配置已完成**：
- ✅ API Key 已配置
- ✅ Base URL 已设置
- ✅ 默认模型已设置
- ✅ 多模型支持已启用

**现在可以**：
- 直接使用 DeepSeek Chat
- 切换到 DeepSeek Coder
- 或切换到其他模型
- 享受高性价比服务

**推荐使用 DeepSeek**：
- 性价比高
- 中文优秀
- 性能良好
- 完全够用
