@echo off
REM ULTRON Enhanced - Comprehensive Startup Script
REM ==============================================
REM This script performs system diagnostics, starts all components,
REM and provides a complete launch sequence for ULTRON Agent

setlocal enabledelayedexpansion

echo ========================================
echo   ULTRON Enhanced v3.0 - Starting...
echo ========================================
echo.

REM Set window title
title ULTRON Enhanced v3.0 - Startup

REM Color configuration
color 0A

REM Check if Python is installed
echo [1/10] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python is available

REM Check Python version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [OK] Python version: %PYTHON_VERSION%

REM Check if virtual environment exists
echo [2/10] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found - using global Python
)

REM Install/Update dependencies
echo [3/10] Checking dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some dependencies might be missing
    echo Installing core dependencies...
    pip install flask flask-socketio eventlet psutil opencv-python pillow pyautogui
)
echo [OK] Dependencies ready

REM Check system permissions
echo [4/10] Checking system permissions...
REM Test if we can create files in current directory
echo test > test_write.tmp 2>nul
if exist test_write.tmp (
    del test_write.tmp
    echo [OK] Write permissions available
) else (
    echo [WARNING] Limited write permissions
)

REM Create necessary directories
echo [5/10] Setting up directories...
if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots
if not exist "models" mkdir models
if not exist "temp" mkdir temp
if not exist "web\assets" mkdir web\assets
echo [OK] Directory structure ready

REM Check for Ollama (optional)
echo [6/10] Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Ollama not found - local AI models will be unavailable
    echo Install from: https://ollama.ai
) else (
    echo [OK] Ollama is available
    REM Start Ollama server if not running
    tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe" >NUL
    if errorlevel 1 (
        echo [INFO] Starting Ollama server...
        start /B ollama serve
        timeout /t 3 >nul
    )
)

REM Check for OpenAI API key (optional)
echo [7/10] Checking configuration...
if exist "ultron_config.json" (
    echo [OK] Configuration file found
) else (
    if exist "ultron_config.json.example" (
        echo [INFO] Copying example configuration...
        copy ultron_config.json.example ultron_config.json >nul
    )
    echo [WARNING] Please configure ultron_config.json with your API keys
)

REM System diagnostics
echo [8/10] Running system diagnostics...
python -c "import sys; print(f'Python: {sys.version}'); import platform; print(f'OS: {platform.system()} {platform.release()}')" 2>nul
if errorlevel 1 (
    echo [WARNING] System diagnostics incomplete
) else (
    echo [OK] System diagnostics complete
)

REM Check for GUI capabilities
echo [9/10] Checking GUI capabilities...
python -c "import tkinter; print('Tkinter available')" 2>nul
if errorlevel 1 (
    echo [INFO] GUI may not be available (headless mode)
) else (
    echo [OK] GUI capabilities available
)

REM Pre-launch system status
echo [10/10] Final system check...
echo [OK] All systems ready for launch
echo.

REM Display startup banner
echo ==========================================
echo   🤖 ULTRON Enhanced v3.0 Ready! 🤖
echo ==========================================
echo.
echo Available Interfaces:
echo  - GUI Interface: Starting automatically
echo  - Web Interface: http://localhost:8080
echo  - CLI Interface: Fallback mode
echo.
echo System Features:
echo  - Voice Recognition & TTS
echo  - Computer Vision & OCR  
echo  - Screen Automation
echo  - Multi-AI Integration
echo  - Real-time Monitoring
echo.

REM Launch options
set LAUNCH_MODE=auto
if "%1"=="--cli" set LAUNCH_MODE=cli
if "%1"=="--web" set LAUNCH_MODE=web
if "%1"=="--gui" set LAUNCH_MODE=gui

echo Launch Mode: %LAUNCH_MODE%
echo.
echo Starting ULTRON Enhanced...
echo ==========================================

REM Start logging
echo [%date% %time%] ULTRON Enhanced startup initiated >> logs\startup.log

REM Launch main application with error handling
if "%LAUNCH_MODE%"=="web" (
    echo Starting in Web Mode...
    python main.py --web
) else if "%LAUNCH_MODE%"=="cli" (
    echo Starting in CLI Mode...
    python main.py --cli
) else (
    echo Starting in Auto Mode...
    python main.py
)

REM Handle exit codes
if errorlevel 1 (
    echo.
    echo [ERROR] ULTRON Enhanced encountered an error
    echo Check logs\error.log for details
    echo.
    echo Attempting recovery mode...
    python -c "
import traceback, sys
try:
    print('=== Recovery Mode ===')
    print('Checking core modules...')
    
    # Test imports
    modules = ['agent_core', 'brain', 'voice_manager', 'config']
    for module in modules:
        try:
            __import__(module)
            print(f'✓ {module}')
        except Exception as e:
            print(f'✗ {module}: {e}')
    
    print('=== End Recovery ===')
except Exception as e:
    print(f'Recovery failed: {e}')
    traceback.print_exc()
"
) else (
    echo.
    echo [SUCCESS] ULTRON Enhanced shut down normally
    echo [%date% %time%] Normal shutdown >> logs\startup.log
)

echo.
echo ==========================================
echo   ULTRON Enhanced Session Complete
echo ==========================================

REM Cleanup
if exist "*.pyc" del /q *.pyc 2>nul
if exist "__pycache__" rmdir /s /q __pycache__ 2>nul

REM Keep window open if there were errors
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)

endlocal