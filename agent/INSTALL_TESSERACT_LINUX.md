# Linux 服务端部署 - Tesseract OCR 安装指南

## 一、系统要求

- **操作系统**：Linux (Ubuntu/Debian/CentOS/RHEL/Alpine)
- **Python**：3.10+
- **Tesseract OCR**：4.0+ (推荐 5.0+)
- **内存**：至少 2GB（OCR 处理需要）

## 二、各发行版安装方法

### 1. Ubuntu/Debian 系列

#### Ubuntu 20.04/22.04/24.04

```bash
# 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 安装 Tesseract OCR
sudo apt-get install -y tesseract-ocr

# 安装语言包
sudo apt-get install -y \
    tesseract-ocr-chi-sim \    # 简体中文
    tesseract-ocr-chi-tra \    # 繁体中文
    tesseract-ocr-eng \        # 英文
    tesseract-ocr-jpn \        # 日文
    tesseract-ocr-kor          # 韩文

# 安装开发库（可选，用于编译扩展）
sudo apt-get install -y libtesseract-dev libleptonica-dev

# 验证安装
tesseract --version
tesseract --list-langs
```

#### Debian 10/11/12

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y tesseract-ocr-chi-sim tesseract-ocr-eng
```

### 2. CentOS/RHEL/Fedora 系列

#### CentOS 7

```bash
# 安装 EPEL 源
sudo yum install -y epel-release

# 安装 Tesseract
sudo yum install -y tesseract

# 安装语言包
sudo yum install -y \
    tesseract-langpack-chi_sim \
    tesseract-langpack-eng \
    tesseract-langpack-chi_tra

# 验证
tesseract --version
```

#### CentOS 8 / Rocky Linux / AlmaLinux

```bash
# 启用 PowerTools/CRB
sudo dnf config-manager --set-enabled powertools  # CentOS 8
# 或
sudo dnf config-manager --set-enabled crb         # Rocky/Alma

# 安装 EPEL
sudo dnf install -y epel-release

# 安装 Tesseract
sudo dnf install -y tesseract
sudo dnf install -y tesseract-langpack-chi_sim
sudo dnf install -y tesseract-langpack-eng
```

#### RHEL 8/9

```bash
# 启用 CodeReady Builder
sudo subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms

# 安装 EPEL
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm

# 安装 Tesseract
sudo dnf install -y tesseract
sudo dnf install -y tesseract-langpack-chi_sim
```

#### Fedora

```bash
sudo dnf install -y tesseract
sudo dnf install -y tesseract-langpack-chi_sim
sudo dnf install -y tesseract-langpack-eng
```

### 3. Alpine Linux（适用于 Docker）

```bash
# 安装 Tesseract
apk add --no-cache tesseract-ocr

# 安装语言包
apk add --no-cache \
    tesseract-ocr-data-chi_sim \
    tesseract-ocr-data-eng \
    tesseract-ocr-data-chi_tra

# 安装开发库（可选）
apk add --no-cache tesseract-ocr-dev
```

### 4. Arch Linux / Manjaro

```bash
sudo pacman -S tesseract
sudo pacman -S tesseract-data-chi_sim
sudo pacman -S tesseract-data-eng
```

### 5. openSUSE

```bash
sudo zypper install tesseract-ocr
sudo zypper install tesseract-ocr-traineddata-chinese_simplified
sudo zypper install tesseract-ocr-traineddata-english
```

## 三、Docker 部署

### 方案1：使用修改后的 Dockerfile（推荐）

项目已包含配置好的 Dockerfile，直接构建即可：

```bash
cd agent

# 构建镜像
docker build -t ai-assistant:latest .

# 运行容器
docker run -d \
    --name ai-assistant \
    -p 8000:8000 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    ai-assistant:latest
```

### 方案2：Docker Compose（推荐）

```yaml
version: '3.8'

services:
  ai-assistant:
    build: ./agent
    container_name: ai-assistant
    ports:
      - "8000:8000"
    volumes:
      - ./agent/data:/app/data
      - ./agent/logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL}
    restart: unless-stopped
```

运行：
```bash
docker-compose up -d
```

### 方案3：使用预装 Tesseract 的基础镜像

创建 `Dockerfile.tesseract`：

```dockerfile
# 使用预装 Tesseract 的镜像
FROM ubuntu:22.04

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# 安装系统依赖和 Tesseract
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# 复制应用
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/chroma data/attachments logs

EXPOSE 8000

CMD ["python", "main.py"]
```

### 方案4：Alpine Linux（最小化镜像）

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

# 安装 Tesseract 和依赖
RUN apk add --no-cache \
    tesseract-ocr \
    tesseract-ocr-data-chi_sim \
    tesseract-ocr-data-eng \
    tesseract-ocr-dev \
    gcc \
    musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/chroma data/attachments logs

EXPOSE 8000

CMD ["python", "main.py"]
```

## 四、验证安装

### 1. 命令行验证

```bash
# 检查版本
tesseract --version
# 输出示例：
# tesseract 5.3.3
#  leptonica-1.83.0

# 查看已安装语言
tesseract --list-langs
# 输出示例：
# List of available languages in "..."：
# chi_sim
# chi_tra
# eng
# osd
```

### 2. 功能测试

```bash
# 创建测试图片（包含中文和英文）
echo "Hello 你好 World 世界" | convert -pointsize 20 text:- test.png

# 执行 OCR
tesseract test.png output -l chi_sim+eng

# 查看结果
cat output.txt
```

### 3. Python 验证

```bash
python3 << 'EOF'
import pytesseract
from PIL import Image

# 检查 Tesseract 是否可用
try:
    version = pytesseract.get_tesseract_version()
    print(f"Tesseract version: {version}")
    
    # 检查语言包
    langs = pytesseract.get_languages()
    print(f"Available languages: {langs}")
    
    print("✅ Tesseract OCR 安装成功！")
except Exception as e:
    print(f"❌ 错误: {e}")
EOF
```

### 4. 在应用中验证

```bash
# 启动应用后访问健康检查
curl http://localhost:8000/health

# 上传测试图片
curl -X POST \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -F "file=@test.png" \
    http://localhost:8000/api/v1/attachments/upload
```

## 五、性能优化

### 1. 多线程配置

```bash
# 设置 OMP 线程数（根据 CPU 核心数调整）
export OMP_THREAD_LIMIT=4
```

### 2. 语言包优化

只安装需要的语言包，减少内存占用：

```bash
# 最小化安装（仅中文和英文）
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng
```

### 3. 缓存配置

```python
# 在应用中配置 Tesseract 缓存
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
```

## 六、生产环境建议

### 1. 使用 Supervisor 管理进程

```ini
# /etc/supervisor/conf.d/ai-assistant.conf
[program:ai-assistant]
directory=/app/agent
command=python main.py
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-assistant/err.log
stdout_logfile=/var/log/ai-assistant/out.log
environment=OMP_THREAD_LIMIT="4"
```

### 2. Systemd 服务

```ini
# /etc/systemd/system/ai-assistant.service
[Unit]
Description=AI Assistant Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/app/agent
ExecStart=/usr/bin/python3 main.py
Restart=always
Environment="OMP_THREAD_LIMIT=4"

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-assistant
sudo systemctl start ai-assistant
```

### 3. Nginx 反向代理

```nginx
upstream ai_assistant {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;  # 允许上传大文件

    location / {
        proxy_pass http://ai_assistant;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## 七、故障排查

### 问题1：找不到 tesseract 命令

```bash
# 检查是否安装
which tesseract

# 检查 PATH
echo $PATH

# 手动添加到 PATH
export PATH=$PATH:/usr/bin
```

### 问题2：语言包缺失

```bash
# 查看已安装语言
tesseract --list-langs

# 如果缺少中文，重新安装
sudo apt-get install -y tesseract-ocr-chi-sim
```

### 问题3：权限问题

```bash
# 确保 tesseract 可执行
sudo chmod +x /usr/bin/tesseract

# 确保语言包目录可读
sudo chmod -R 755 /usr/share/tesseract-ocr
```

### 问题4：内存不足

```bash
# 增加系统内存或使用 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 八、自动化安装脚本

创建 `install_tesseract.sh`：

```bash
#!/bin/bash

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "无法检测系统类型"
    exit 1
fi

echo "检测到系统: $OS"

# 根据系统类型安装
case $OS in
    ubuntu|debian)
        echo "安装 Tesseract OCR (Ubuntu/Debian)..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
        sudo apt-get install -y tesseract-ocr-chi-sim tesseract-ocr-chi-tra tesseract-ocr-eng
        ;;
    centos|rhel|rocky|almalinux)
        echo "安装 Tesseract OCR (CentOS/RHEL)..."
        sudo yum install -y epel-release
        sudo yum install -y tesseract
        sudo yum install -y tesseract-langpack-chi_sim tesseract-langpack-eng
        ;;
    alpine)
        echo "安装 Tesseract OCR (Alpine)..."
        apk add --no-cache tesseract-ocr
        apk add --no-cache tesseract-ocr-data-chi_sim tesseract-ocr-data-eng
        ;;
    arch|manjaro)
        echo "安装 Tesseract OCR (Arch)..."
        sudo pacman -S --noconfirm tesseract
        sudo pacman -S --noconfirm tesseract-data-chi_sim tesseract-data-eng
        ;;
    *)
        echo "不支持的系统: $OS"
        exit 1
        ;;
esac

# 验证安装
echo ""
echo "验证安装..."
tesseract --version
echo ""
echo "已安装语言包:"
tesseract --list-langs

echo ""
echo "✅ Tesseract OCR 安装完成！"
```

使用：
```bash
chmod +x install_tesseract.sh
./install_tesseract.sh
```

## 九、总结

### 推荐方案

1. **Docker 部署**：使用项目提供的 Dockerfile，自动安装 Tesseract
2. **Ubuntu/Debian**：最简单，包管理完善
3. **Alpine**：镜像最小，适合生产环境

### 最小化安装命令

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng

# CentOS/RHEL
sudo yum install -y epel-release tesseract tesseract-langpack-chi_sim tesseract-langpack-eng

# Alpine
apk add --no-cache tesseract-ocr tesseract-ocr-data-chi_sim tesseract-ocr-data-eng
```

安装完成后重启应用即可使用图片 OCR 功能！
