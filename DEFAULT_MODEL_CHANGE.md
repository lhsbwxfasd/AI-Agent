# 默认模型配置修改说明

## 修改内容

已将项目默认模型从 `deepseek-chat` 修改为 `deepseek-r1:7b`（本地 Ollama 模型）。

## 修改的文件

### 1. 后端配置文件

#### `agent/config.py`
```python
# 修改前
default_model: str = "deepseek-chat"

# 修改后
default_model: str = "deepseek-r1:7b"
```

#### `agent/.env`
```bash
# 修改前
DEFAULT_MODEL=deepseek-chat

# 修改后
DEFAULT_MODEL=deepseek-r1:7b
```

#### `agent/app/api/chat.py`
```python
# 修改前
return {
    "models": models,
    "default": "deepseek-chat"
}

# 修改后
return {
    "models": models,
    "default": "deepseek-r1:7b"
}
```

### 2. 前端配置文件

#### `web/src/stores/chat.js`
```javascript
// 修改前
const currentModel = ref('deepseek-chat')
currentModel.value = response.default || 'deepseek-chat'

// 修改后
const currentModel = ref('deepseek-r1:7b')
currentModel.value = response.default || 'deepseek-r1:7b'
```

## 使用说明

### 前提条件

确保已安装并运行 Ollama：

```bash
# 1. 安装 Ollama
# Windows: https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. 下载 deepseek-r1:7b 模型
ollama pull deepseek-r1:7b

# 3. 启动 Ollama 服务
ollama serve

# 4. 验证模型
ollama list
```

### 启动应用

```bash
# 后端
cd agent
python main.py

# 前端
cd web
npm run dev
```

### 验证默认模型

1. 打开浏览器访问：http://localhost:3000
2. 登录后，在聊天界面底部的模型选择器中
3. 应该默认显示：**DeepSeek R1 7B (Ollama)**

## 可用的模型列表

项目支持以下模型：

| 模型 ID | 名称 | Provider | 说明 |
|---------|------|----------|------|
| **deepseek-r1:7b** | DeepSeek R1 7B (Ollama) | ollama | ✅ 当前默认 |
| deepseek-chat | DeepSeek Chat | deepseek | DeepSeek API |
| deepseek-coder | DeepSeek Coder | deepseek | DeepSeek API |
| gpt-4 | GPT-4 | openai | OpenAI API |
| gpt-3.5-turbo | GPT-3.5 Turbo | openai | OpenAI API |
| claude-3-opus | Claude 3 Opus | anthropic | Anthropic API |
| claude-3-sonnet | Claude 3 Sonnet | anthropic | Anthropic API |

## 切换模型

用户可以随时在聊天界面切换模型：

1. 点击底部输入框下方的模型选择器
2. 选择想要使用的模型
3. 新消息将使用选中的模型

## 注意事项

### 1. Ollama 服务必须运行

使用 `deepseek-r1:7b` 需要：
- ✅ Ollama 已安装
- ✅ Ollama 服务正在运行（默认端口 11434）
- ✅ deepseek-r1:7b 模型已下载

检查服务状态：
```bash
# 检查 Ollama 服务
curl http://localhost:11434/api/tags

# 检查模型
ollama list | grep deepseek-r1
```

### 2. 资源要求

- **内存**：至少 8GB（推荐 16GB）
- **CPU**：多核处理器
- **GPU**：可选，但会显著提升性能

### 3. 模型特点

DeepSeek R1 7B 特点：
- ✅ 本地运行，数据隐私
- ✅ 无需 API Key
- ✅ 免费使用
- ⚠️ 需要本地资源
- ⚠️ 推理速度取决于硬件

### 4. 如果 Ollama 未运行

如果 Ollama 服务未运行，应用会：
- 前端正常启动
- 发送消息时会报错：`Connection refused` 或 `Service unavailable`
- 解决方案：启动 Ollama 服务

## 回退到 DeepSeek API

如果需要回退到 DeepSeek API：

```bash
# 修改 .env
DEFAULT_MODEL=deepseek-chat

# 重启后端
cd agent
python main.py
```

## 测试建议

### 1. 测试本地模型

```bash
# 直接测试 Ollama
ollama run deepseek-r1:7b
>>> 你好，请介绍一下自己
>>> /bye
```

### 2. 测试应用

```bash
# 启动应用后发送测试消息
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "model": "deepseek-r1:7b"
  }'
```

## 性能优化建议

### 1. 使用 GPU（如果有）

```bash
# 检查 GPU 支持
ollama run deepseek-r1:7b --verbose

# 如果有 NVIDIA GPU，确保安装了 CUDA
nvidia-smi
```

### 2. 调整并发

```bash
# 设置环境变量
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED=1
```

### 3. 量化模型（减少内存）

```bash
# 使用量化版本（如果可用）
ollama pull deepseek-r1:7b-q4_0
```

## 故障排查

### 问题1：模型未找到

```bash
# 解决方案：下载模型
ollama pull deepseek-r1:7b
```

### 问题2：连接失败

```bash
# 检查服务
curl http://localhost:11434

# 启动服务
ollama serve
```

### 问题3：内存不足

```bash
# 检查系统内存
free -h

# 解决方案：
# 1. 增加系统内存
# 2. 使用更小的模型
# 3. 使用量化版本
```

## 总结

✅ 默认模型已修改为 `deepseek-r1:7b`

✅ 配置文件已更新：
- `agent/config.py`
- `agent/.env`
- `agent/app/api/chat.py`
- `web/src/stores/chat.js`

✅ 下一步：
1. 确保 Ollama 已安装并运行
2. 下载 deepseek-r1:7b 模型
3. 重启应用
4. 开始使用本地 AI 模型！
