@echo off
REM MatchStats 服务启动脚本

echo ========================================
echo   MatchStats 服务启动中...
echo ========================================
echo.

REM 激活虚拟环境并启动服务
call venv\Scripts\activate.bat
python -m app.main

pause
