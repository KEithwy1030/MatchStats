# MatchStats 启动脚本 (Windows)
# 使用前请确保已激活虚拟环境

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "错误: 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先运行 .\venv_init.ps1 创建虚拟环境" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "警告: .env 文件不存在，使用默认配置" -ForegroundColor Yellow
}

# 启动服务
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "启动 MatchStats 服务" -ForegroundColor Cyan
Write-Host "端口: 9999" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API 文档: http://localhost:9999/docs" -ForegroundColor Green
Write-Host "Web 界面: http://localhost:9999/" -ForegroundColor Green
Write-Host ""
Write-Host "按 Ctrl+C 停止服务"
Write-Host ""

python -m app.main
