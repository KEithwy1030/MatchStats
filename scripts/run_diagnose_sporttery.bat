@echo off
chcp 65001 >nul
cd /d %~dp0..\..
echo ========================================
echo 竞彩 API 诊断工具
echo ========================================
echo.

venv\Scripts\python.exe scripts\diagnose_sporttery.py

echo.
echo ========================================
echo 诊断完成！
echo ========================================
pause
