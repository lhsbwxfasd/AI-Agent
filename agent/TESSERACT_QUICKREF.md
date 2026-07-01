# Tesseract OCR 安装快速参考

## 🚀 快速安装命令

### Ubuntu/Debian
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
```

### CentOS/RHEL 8
```bash
sudo dnf install -y epel-release tesseract tesseract-langpack-chi_sim tesseract-langpack-eng
```

### CentOS 7
```bash
sudo yum install -y epel-release tesseract tesseract-langpack-chi_sim tesseract-langpack-eng
```

### Alpine Linux
```bash
apk add --no-cache tesseract-ocr tesseract-ocr-data-chi_sim tesseract-ocr-data-eng
```

### Fedora
```bash
sudo dnf install -y tesseract tesseract-langpack-chi_sim tesseract-langpack-eng
```

### Arch Linux
```bash
sudo pacman -S tesseract tesseract-data-chi_sim tesseract-data-eng
```

## 🐳 Docker 部署

### 方案1：使用项目 Dockerfile（推荐）
```bash
cd agent
docker build -t ai-assistant:latest .
docker run -d -p 8000:8000 ai-assistant:latest
```

### 方案2：Docker Compose
```bash
docker-compose up -d
```

## ✅ 验证安装

```bash
# 检查版本
tesseract --version

# 查看语言包
tesseract --list-langs

# Python 验证
python3 -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## 🔧 自动安装脚本

```bash
# 下载并运行
chmod +x install_tesseract.sh
sudo ./install_tesseract.sh
```

## 📦 完整文档

- 详细安装指南：`INSTALL_TESSERACT_LINUX.md`
- 功能说明：`ATTACHMENT_GUIDE.md`
- Windows 安装：`ATTACHMENT_GUIDE.md` 中的 Windows 部分

## 🎯 语言包说明

| 语言包 | 说明 | 包名示例 |
|--------|------|----------|
| chi_sim | 简体中文 | tesseract-ocr-chi-sim |
| chi_tra | 繁体中文 | tesseract-ocr-chi-tra |
| eng | 英文 | tesseract-ocr-eng |
| jpn | 日文 | tesseract-ocr-jpn |
| kor | 韩文 | tesseract-ocr-kor |

## 🐛 常见问题

### Q: 找不到 tesseract 命令？
```bash
which tesseract  # 检查路径
export PATH=$PATH:/usr/bin  # 添加到 PATH
```

### Q: 语言包缺失？
```bash
tesseract --list-langs  # 查看已安装
sudo apt-get install -y tesseract-ocr-chi-sim  # 安装中文
```

### Q: Docker 中使用？
```bash
# Dockerfile 已配置，直接构建即可
docker build -t ai-assistant:latest .
```

## 📊 性能建议

- **线程数**：`export OMP_THREAD_LIMIT=4`（根据 CPU 核心数）
- **内存**：至少 2GB
- **语言包**：只安装需要的，减少内存占用

## 🔗 下载地址

- **Tesseract 官方**：https://github.com/tesseract-ocr/tesseract
- **Windows 安装包**：https://github.com/UB-Mannheim/tesseract/wiki
- **语言包下载**：https://github.com/tesseract-ocr/tessdata

## 📝 下一步

1. ✅ 安装 Tesseract OCR
2. ✅ 验证安装
3. 🔄 重启 AI Assistant 服务
4. 🖼️ 上传图片测试

安装完成后，系统将支持：
- ✅ PDF 文档解析
- ✅ Word 文档解析
- ✅ 图片 OCR 文字识别
- ✅ 多语言支持（中英日韩）
