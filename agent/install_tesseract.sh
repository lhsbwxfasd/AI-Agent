#!/bin/bash

# ========================================
# Tesseract OCR 自动安装脚本
# 适用于主流 Linux 发行版
# ========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_warning "建议使用 sudo 运行此脚本"
        SUDO="sudo"
    else
        SUDO=""
    fi
}

# 检测系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        print_info "检测到系统: $OS $OS_VERSION"
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
        print_info "检测到系统: RHEL/CentOS"
    else
        print_error "无法检测系统类型"
        exit 1
    fi
}

# Ubuntu/Debian 安装
install_debian() {
    print_info "安装 Tesseract OCR (Ubuntu/Debian)..."
    
    $SUDO apt-get update
    
    # 安装 Tesseract
    $SUDO apt-get install -y tesseract-ocr
    
    # 安装语言包
    print_info "安装语言包..."
    $SUDO apt-get install -y \
        tesseract-ocr-chi-sim \
        tesseract-ocr-chi-tra \
        tesseract-ocr-eng \
        tesseract-ocr-jpn \
        tesseract-ocr-kor
    
    # 安装开发库（可选）
    read -p "是否安装开发库？(y/n): " install_dev
    if [ "$install_dev" = "y" ]; then
        $SUDO apt-get install -y libtesseract-dev libleptonica-dev
    fi
}

# CentOS/RHEL/Fedora 安装
install_rhel() {
    print_info "安装 Tesseract OCR (CentOS/RHEL/Fedora)..."
    
    # 安装 EPEL
    if command -v dnf &> /dev/null; then
        # Fedora 或 CentOS 8+
        $SUDO dnf install -y epel-release
        
        # CentOS 8 需要启用 PowerTools
        if [ "$OS" = "centos" ] && [ "$OS_VERSION" = "8" ]; then
            $SUDO dnf config-manager --set-enabled powertools
        fi
        
        # 安装 Tesseract
        $SUDO dnf install -y tesseract
        
        # 安装语言包
        print_info "安装语言包..."
        $SUDO dnf install -y \
            tesseract-langpack-chi_sim \
            tesseract-langpack-chi_tra \
            tesseract-langpack-eng
    else
        # CentOS 7
        $SUDO yum install -y epel-release
        $SUDO yum install -y tesseract
        
        print_info "安装语言包..."
        $SUDO yum install -y \
            tesseract-langpack-chi_sim \
            tesseract-langpack-chi_tra \
            tesseract-langpack-eng
    fi
}

# Alpine 安装
install_alpine() {
    print_info "安装 Tesseract OCR (Alpine)..."
    
    $SUDO apk update
    $SUDO apk add --no-cache tesseract-ocr
    
    print_info "安装语言包..."
    $SUDO apk add --no-cache \
        tesseract-ocr-data-chi_sim \
        tesseract-ocr-data-chi_tra \
        tesseract-ocr-data-eng
}

# Arch Linux 安装
install_arch() {
    print_info "安装 Tesseract OCR (Arch Linux)..."
    
    $SUDO pacman -Sy
    $SUDO pacman -S --noconfirm tesseract
    
    print_info "安装语言包..."
    $SUDO pacman -S --noconfirm \
        tesseract-data-chi_sim \
        tesseract-data-chi_tra \
        tesseract-data-eng
}

# openSUSE 安装
install_suse() {
    print_info "安装 Tesseract OCR (openSUSE)..."
    
    $SUDO zypper refresh
    $SUDO zypper install -y tesseract-ocr
    
    print_info "安装语言包..."
    $SUDO zypper install -y \
        tesseract-ocr-traineddata-chinese_simplified \
        tesseract-ocr-traineddata-chinese_traditional \
        tesseract-ocr-traineddata-english
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    # 检查命令
    if command -v tesseract &> /dev/null; then
        print_success "Tesseract 命令已安装"
        
        # 显示版本
        echo ""
        print_info "版本信息:"
        tesseract --version
        echo ""
        
        # 显示语言包
        print_info "已安装语言包:"
        tesseract --list-langs
        echo ""
    else
        print_error "Tesseract 未正确安装"
        exit 1
    fi
    
    # 检查 Python 包
    print_info "检查 Python 包..."
    if python3 -c "import pytesseract" 2>/dev/null; then
        print_success "pytesseract 已安装"
    else
        print_warning "pytesseract 未安装"
        read -p "是否安装 pytesseract？(y/n): " install_py
        if [ "$install_py" = "y" ]; then
            pip3 install pytesseract Pillow
        fi
    fi
}

# 测试 OCR
test_ocr() {
    read -p "是否测试 OCR 功能？(y/n): " do_test
    if [ "$do_test" != "y" ]; then
        return
    fi
    
    print_info "创建测试图片..."
    
    # 检查 ImageMagick
    if ! command -v convert &> /dev/null; then
        print_warning "ImageMagick 未安装，跳过测试"
        return
    fi
    
    # 创建测试图片
    echo "Hello 你好 World 世界" | convert -pointsize 20 text:- /tmp/test_ocr.png
    
    # 执行 OCR
    print_info "执行 OCR 测试..."
    tesseract /tmp/test_ocr.png /tmp/test_output -l chi_sim+eng
    
    # 显示结果
    echo ""
    print_info "OCR 结果:"
    cat /tmp/test_output.txt
    echo ""
    
    # 清理
    rm -f /tmp/test_ocr.png /tmp/test_output.txt
    
    print_success "OCR 测试完成"
}

# 主函数
main() {
    echo ""
    echo "========================================"
    echo "  Tesseract OCR 自动安装脚本"
    echo "========================================"
    echo ""
    
    # 检查 root
    check_root
    
    # 检测系统
    detect_os
    
    # 根据系统安装
    case $OS in
        ubuntu|debian|linuxmint|pop)
            install_debian
            ;;
        centos|rhel|rocky|almalinux|fedora)
            install_rhel
            ;;
        alpine)
            install_alpine
            ;;
        arch|manjaro)
            install_arch
            ;;
        opensuse-leap|opensuse-tumbleweed)
            install_suse
            ;;
        *)
            print_error "不支持的系统: $OS"
            print_info "支持的系统: Ubuntu, Debian, CentOS, RHEL, Fedora, Alpine, Arch, openSUSE"
            exit 1
            ;;
    esac
    
    # 验证
    verify_installation
    
    # 测试
    test_ocr
    
    echo ""
    echo "========================================"
    print_success "Tesseract OCR 安装完成！"
    echo "========================================"
    echo ""
    echo "下一步："
    echo "1. 重启 AI Assistant 服务"
    echo "2. 上传图片测试 OCR 功能"
    echo ""
}

# 运行主函数
main
