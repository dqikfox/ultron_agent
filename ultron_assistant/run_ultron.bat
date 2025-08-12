@echo off
echo ====================================
echo     ULTRON ASSISTANT LAUNCHER
echo ====================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Starting Ultron Assistant...
echo.

REM Try to start with dependency installation if needed
python run_ultron_assistant.py --install-deps

if errorlevel 1 (
    echo.
    echo ====================================
    echo     STARTUP FAILED
    echo ====================================
    echo.
    echo Troubleshooting steps:
    echo 1. Ensure Ollama is installed and running
    echo 2. Check Python version (requires 3.8+)
    echo 3. Try: python run_ultron_assistant.py --check-only
    echo.
    pause
) else (
    echo.
    echo Ultron Assistant started successfully!
)
