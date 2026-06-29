@echo off
chcp 65001 >nul
echo ========================================
echo 企业级 Agent 后端 - 一键安装脚本
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先创建虚拟环境
    echo 运行: python -m venv venv
    pause
    exit /b 1
)

echo [步骤 1/5] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [步骤 2/5] 升级 pip...
python -m pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [步骤 3/5] 下载预编译 wheel 文件...
python scripts\download_wheels.py

echo.
echo [步骤 4/5] 安装预编译 wheel...
if exist "wheels\duckdb-0.9.1-cp38-cp38-win_amd64.whl" (
    python -m pip install wheels\duckdb-0.9.1-cp38-cp38-win_amd64.whl
)
if exist "wheels\hnswlib-0.8.0-cp38-cp38-win_amd64.whl" (
    python -m pip install wheels\hnswlib-0.8.0-cp38-cp38-win_amd64.whl
)

echo.
echo [步骤 5/5] 安装其他依赖...
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 验证安装:
python -c "import chromadb; print('✓ chromadb:', chromadb.__version__)"
python -c "import sentence_transformers; print('✓ sentence_transformers 安装成功')"
python -c "import duckdb; print('✓ duckdb:', duckdb.__version__)"
python -c "import hnswlib; print('✓ hnswlib 安装成功')"

echo.
echo 下一步:
echo   1. 复制 .env.example 为 .env 并配置
echo   2. 运行 python scripts\init_knowledge.py 初始化知识库
echo   3. 运行 python main.py 启动服务
echo.
pause
