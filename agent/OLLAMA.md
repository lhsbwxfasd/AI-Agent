# Ollama 本地模型配置指南

## 概述

已将本地 Ollama 的 `deepseek-r1:7b` 模型集成到系统中，可以通过前端界面选择使用。

## 配置说明

### 1. 后端配置 (config.py)

已添加 Ollama 配置：
```python
# Ollama 配置（本地模型）
ollama_base_url: str = "http://localhost:11434/v1"

# 多模型配置
available_models: Dict[str, Dict] = {
    "deepseek-chat": {"name": "DeepSeek Chat", "provider": "deepseek", "max_tokens": 4096},
    "deepseek-coder": {"name": "DeepSeek Coder", "provider": "deepseek", "max_tokens": 4096},
    "deepseek-r1:7b": {"name": "DeepSeek R1 7B (Ollama)", "provider": "ollama", "max_tokens": 4096},
    ...
}
```

### 2. 环境变量 (.env)

已添加：
```
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 3. LLM 服务 (app/core/llm.py)

已更新 `_get_llm` 方法，支持根据 provider 自动选择：
- **ollama**: 使用 Ollama 本地服务
- **deepseek**: 使用 DeepSeek API
- **openai**: 使用 OpenAI API

## 使用方法

### 1. 确保 Ollama 服务运行

```powershell
# 检查 Ollama 服务
curl http://localhost:11434/api/tags

# 应返回已安装的模型列表
```

### 2. 确保 deepseek-r1:7b 模型已安装

```powershell
# 查看已安装模型
ollama list

# 如果没有，拉取模型
ollama pull deepseek-r1:7b
```

### 3. 启动后端

```powershell
cd D:\测试项目\AI2\agent
python main.py
```

### 4. 启动前端

```powershell
cd D:\测试项目\AI2\web
npm run dev
```

### 5. 在前端选择模型

1. 登录系统（admin / admin123）
2. 在聊天页面顶部，点击模型选择器
3. 选择 **"DeepSeek R1 7B (Ollama)"**
4. 开始对话

## 模型对比

| 模型 | 提供者 | 特点 | 速度 | 质量 |
|------|--------|------|------|------|
| deepseek-chat | DeepSeek API | 通用对话模型 | 快 | 高 |
| deepseek-coder | DeepSeek API | 代码专用模型 | 快 | 高 |
| **deepseek-r1:7b** | **Ollama 本地** | **本地推理，隐私保护** | **中** | **中高** |

## 优势

### 使用 Ollama 本地模型的优势：
1. **隐私保护**：数据不离开本地
2. **无 API 费用**：完全免费
3. **离线使用**：无需网络连接
4. **可定制**：可以加载其他开源模型

### 使用 DeepSeek API 的优势：
1. **更高质量**：更大的模型参数
2. **更快速度**：云端 GPU 加速
3. **无需本地资源**：不占用本地显存

## 常见问题

### Q: 选择 Ollama 模型后报错？

A: 检查：
1. Ollama 服务是否运行：`curl http://localhost:11434`
2. 模型是否已安装：`ollama list`
3. 端口是否正确：默认 11434

### Q: Ollama 模型响应很慢？

A: 
1. 检查 GPU 是否被识别：`nvidia-smi`
2. 检查显存是否足够：7B 模型需要约 8GB 显存
3. 如果没有 GPU，会使用 CPU 推理，速度较慢

### Q: 如何添加其他 Ollama 模型？

A: 修改 `config.py`：
```python
available_models: Dict[str, Dict] = {
    ...
    "llama2:7b": {"name": "Llama 2 7B (Ollama)", "provider": "ollama", "max_tokens": 4096},
    "mistral:7b": {"name": "Mistral 7B (Ollama)", "provider": "ollama", "max_tokens": 4096},
}
```

然后拉取模型：
```powershell
ollama pull llama2:7b
```

### Q: 如何修改 Ollama 端口？

A: 修改 `.env`：
```
OLLAMA_BASE_URL=http://localhost:你的端口/v1
```

## 技术细节

### Ollama API 兼容性

Ollama 提供了 OpenAI 兼容的 API 接口：
- Base URL: `http://localhost:11434/v1`
- 无需 API Key（传入任意字符串即可）
- 支持 streaming
- 兼容 OpenAI SDK

### 代码实现

```python
# 根据 provider 选择配置
if provider == "ollama":
    base_url = settings.ollama_base_url
    api_key = "ollama"  # Ollama 不需要真实 API key
elif provider == "deepseek":
    base_url = settings.deepseek_base_url
    api_key = settings.deepseek_api_key
```

## 测试命令

```powershell
# 测试 Ollama API
curl http://localhost:11434/v1/models

# 测试聊天接口
curl -X POST http://localhost:11434/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"model":"deepseek-r1:7b","messages":[{"role":"user","content":"你好"}]}'
```

## 总结

✅ 已成功集成 Ollama 本地模型
✅ 可在前端界面自由切换
✅ 支持流式响应
✅ 保留 API 模型的优势
