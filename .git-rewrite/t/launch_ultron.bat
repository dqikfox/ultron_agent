@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo ====================================
echo     ULTRON ASSISTANT LAUNCHER
echo ====================================
echo.

cd /d "%~dp0ultron_assistant"
python run_ultron_assistant.py --install-deps

pause