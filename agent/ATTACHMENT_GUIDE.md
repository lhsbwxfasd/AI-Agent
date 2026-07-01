# 附件上传功能说明

## 功能概述

系统支持用户上传以下类型的附件，AI会自动解析内容并基于附件回答问题：

- **PDF文档**：自动提取文本内容
- **Word文档**：自动提取文本内容
- **文本文件**：直接读取内容
- **图片文件**：OCR文字识别或视觉模型分析

## 图片识别方案

### 方案1：Tesseract OCR（推荐用于文字识别）

#### Windows 安装步骤

1. **下载 Tesseract OCR**
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载最新版本：`tesseract-ocr-w64-setup-5.3.3-20231014.exe`

2. **安装**
   - 运行安装程序
   - **重要**：勾选 "Additional language data" → 选择：
     - Chinese (Simplified) - 简体中文
     - Chinese (Traditional) - 繁体中文
     - English - 英文
   - 安装路径：`C:\Program Files\Tesseract-OCR\`

3. **配置环境变量**
   - 添加到系统 PATH：`C:\Program Files\Tesseract-OCR`
   - 或者设置 TESSERACT_CMD 环境变量：
     ```
     TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
     ```

4. **重启服务**
   ```bash
   # 重启后端服务
   cd agent
   python main.py
   ```

5. **验证安装**
   ```bash
   tesseract --version
   tesseract --list-langs
   ```

#### Linux 安装步骤

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文简体
sudo apt-get install tesseract-ocr-chi-tra  # 中文繁体

# CentOS/RHEL
sudo yum install tesseract
sudo yum install tesseract-langpack-chi_sim
```

#### macOS 安装步骤

```bash
brew install tesseract
brew install tesseract-lang
```

### 方案2：使用视觉模型（推荐用于图片理解）

如果需要AI理解图片内容（图表、场景、物体等），建议使用支持视觉的模型：

#### 支持视觉的模型

- **OpenAI**：
  - `gpt-4o` (推荐)
  - `gpt-4o-mini`
  - `gpt-4-vision-preview`

- **Anthropic Claude**：
  - `claude-3-opus-20240229`
  - `claude-3-sonnet-20240229`
  - `claude-3-haiku-20240229`

- **Google**：
  - `gemini-pro-vision`

#### 使用方法

1. 在聊天界面切换到支持视觉的模型
2. 上传图片
3. 提问（如："请分析这张图表"、"图片中是什么？"）

### 方案3：混合方案（最佳实践）

1. **安装 Tesseract OCR**：用于提取图片中的文字
2. **配置视觉模型**：用于理解图片内容

这样系统会：
- 先尝试 OCR 提取文字
- 如果用户使用视觉模型，还会进行深度图片理解

## 当前状态检查

### 检查 Tesseract 是否安装

```bash
# Windows
where tesseract

# Linux/macOS
which tesseract
```

### 检查 Python 包

```bash
python -c "import pytesseract; print('OK')"
```

## 常见问题

### Q1: 提示 "tesseract is not installed"

**解决方案**：
1. 按照上述步骤安装 Tesseract OCR
2. 确保添加到系统 PATH
3. 重启后端服务

### Q2: OCR 识别准确率低

**解决方案**：
1. 确保安装了中文语言包
2. 图片清晰度要足够
3. 对于复杂图片，建议使用视觉模型

### Q3: 想要理解图片内容，不只是文字

**解决方案**：
- 切换到支持视觉的模型（如 GPT-4o）
- 视觉模型可以理解图表、场景、物体等

### Q4: 使用本地模型（如 Ollama）如何处理图片？

**解决方案**：
- 安装 Tesseract OCR 提取文字
- 或者使用支持视觉的本地模型：
  - `llava`
  - `bakllava`
  - `moondream`

## 技术架构

```
用户上传图片
    ↓
后端接收文件
    ↓
尝试 Tesseract OCR
    ├─ 成功 → 返回文字内容
    └─ 失败 → 检查模型类型
              ├─ 视觉模型 → 调用视觉API分析
              └─ 文本模型 → 返回提示信息
```

## 示例用法

### 示例1：提取图片中的文字

1. 上传包含文字的图片
2. 提问："请提取图片中的文字"
3. AI返回：OCR识别的文字内容

### 示例2：分析图表

1. 上传图表图片
2. 使用视觉模型（如 GPT-4o）
3. 提问："请分析这个图表的趋势"
4. AI返回：图表分析和见解

### 示例3：理解场景

1. 上传照片
2. 使用视觉模型
3. 提问："图片中是什么场景？"
4. AI返回：场景描述和分析
