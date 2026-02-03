@echo off
cd /d E:\CursorData\MatchStats
call venv\Scripts\activate.bat
python scripts\sync_sporttery_now.py
pause
