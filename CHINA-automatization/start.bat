@echo off
chcp 65001 >nul
echo.
echo  ══════════════════════════════════════════
echo   CATHAY DMC — Генератор Proposal
echo  ══════════════════════════════════════════
echo.
echo  Запускаю сервер...
echo  Открой браузер: http://localhost:5002
echo.
cd /d "%~dp0"
python app.py
pause
