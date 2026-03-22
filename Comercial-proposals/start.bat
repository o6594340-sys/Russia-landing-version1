@echo off
chcp 65001 > nul
title Tozai Tours - Generator KP
echo.
echo  ================================================
echo   TOZAI TOURS - Generator KP (Japan)
echo  ================================================
echo.
echo  Server starting...
echo  Open browser: http://localhost:5000
echo.
echo  To stop: close this window or Ctrl+C
echo  ================================================
echo.
cd /d "%~dp0"
python app.py
pause
