@echo off
chcp 65001 >nul
echo ========================================
echo Tesseract OCR 快速配置工具
echo ========================================
echo.

:: 检查常见路径
set TESSERACT_PATH=

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
    echo [OK] 找到 Tesseract: %TESSERACT_PATH%
    goto :found
)

if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
    set TESSERACT_PATH=C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
    echo [OK] 找到 Tesseract: %TESSERACT_PATH%
    goto :found
)

echo [错误] 未找到 Tesseract OCR
echo.
echo 请先安装 Tesseract OCR:
echo 下载地址: https://github.com/UB-Mannheim/tesseract/wiki
echo.
pause
exit /b 1

:found
echo.
echo ========================================
echo 验证安装
echo ========================================
echo.

:: 测试版本
"%TESSERACT_PATH%" --version
echo.

:: 测试语言包
echo 检查语言包...
"%TESSERACT_PATH%" --list-langs
echo.

:: 测试 Python
echo ========================================
echo 测试 Python 集成
echo ========================================
echo.

python verify_tesseract.py

echo.
echo ========================================
echo 配置完成
echo ========================================
echo.
echo 下一步:
echo 1. 重启后端服务: python main.py
echo 2. 上传图片测试 OCR
echo.
pause
