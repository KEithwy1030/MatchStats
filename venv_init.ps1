# MatchStats 虚拟环境初始化脚本 (Windows)
# 使用方法: 在 PowerShell 中运行 .\venv_init.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "MatchStats 虚拟环境初始化" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "检查 Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  Python 版本: $pythonVersion" -ForegroundColor Green

# 创建虚拟环境
Write-Host ""
Write-Host "创建虚拟环境..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "  虚拟环境已创建: venv/" -ForegroundColor Green
} else {
    Write-Host "  虚拟环境已存在" -ForegroundColor Cyan
}

# 激活虚拟环境
Write-Host ""
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 升级 pip
Write-Host ""
Write-Host "升级 pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
Write-Host ""
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 创建 .env 文件
Write-Host ""
Write-Host "检查配置文件..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  已创建 .env 文件，请配置你的 API Token" -ForegroundColor Green
} else {
    Write-Host "  .env 文件已存在" -ForegroundColor Cyan
}

# 创建数据目录
Write-Host ""
Write-Host "创建数据目录..." -ForegroundColor Yellow
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
    Write-Host "  已创建 data/ 目录" -ForegroundColor Green
}
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "  已创建 logs/ 目录" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "初始化完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方法:" -ForegroundColor Yellow
Write-Host "1. 激活虚拟环境: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. 编辑 .env 文件，配置 FD_API_TOKEN" -ForegroundColor White
Write-Host "3. 运行服务: python -m app.main" -ForegroundColor White
Write-Host ""
