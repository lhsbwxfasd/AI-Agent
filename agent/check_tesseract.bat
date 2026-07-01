@echo off
echo ========================================
echo Tesseract OCR 安装检测工具
echo ========================================
echo.

:: 检查 Tesseract 是否已安装
where tesseract >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tesseract OCR 已安装
    echo.
    echo 版本信息：
    tesseract --version
    echo.
    echo 支持的语言：
    tesseract --list-langs
    echo.
) else (
    echo [错误] Tesseract OCR 未安装或不在 PATH 中
    echo.
    echo 请按照以下步骤安装：
    echo.
    echo 1. 下载 Tesseract OCR:
    echo    https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo 2. 安装时勾选中文语言包:
    echo    - Chinese (Simplified)
    echo    - English
    echo.
    echo 3. 添加到系统 PATH:
    echo    C:\Program Files\Tesseract-OCR
    echo.
    echo 4. 重启此脚本验证安装
    echo.
)

:: 检查 Python 包
echo.
echo ========================================
echo 检查 Python 依赖
echo ========================================
echo.

python -c "import pytesseract; print('[OK] pytesseract 已安装')" 2>nul
if %errorlevel% neq 0 (
    echo [错误] pytesseract 未安装
    echo 运行: pip install pytesseract
)

python -c "from PIL import Image; print('[OK] Pillow 已安装')" 2>nul
if %errorlevel% neq 0 (
    echo [错误] Pillow 未安装
    echo 运行: pip install Pillow
)

echo.
echo ========================================
echo 检查完成
echo ========================================
pause
