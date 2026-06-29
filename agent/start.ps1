#!/usr/bin/env pwsh
# 快速启动脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enterprise Agent Backend - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 版本
Write-Host "[1/4] Checking Python version..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Cyan

if ($pythonVersion -notmatch "3\.(10|11)") {
    Write-Host ""
    Write-Host "  WARNING: Python 3.10.x or 3.11.x is recommended" -ForegroundColor Yellow
    Write-Host "  Current version may have compatibility issues" -ForegroundColor Yellow
}

# 检查虚拟环境
Write-Host ""
Write-Host "[2/4] Checking virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  Virtual environment exists" -ForegroundColor Green
}

# 激活虚拟环境
Write-Host ""
Write-Host "[3/4] Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# 检查依赖
Write-Host ""
Write-Host "[4/4] Checking dependencies..." -ForegroundColor Green
try {
    $fastapi = python -c "import fastapi; print(fastapi.__version__)" 2>&1
    Write-Host "  Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "  Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
}

# 检查配置
Write-Host ""
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "  Creating from template..." -ForegroundColor Yellow
    copy .env.example .env
    Write-Host "  Please edit .env file with your configuration" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Application..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动应用
python main.py
