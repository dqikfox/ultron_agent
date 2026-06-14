@echo off
REM ============================================================================
REM ULTRON Agent 3.0 - Windows Setup Script
REM ============================================================================
REM Sets up the ULTRON Agent environment for Windows systems
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1

title ULTRON Agent 3.0 - Windows Setup

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              ULTRON AGENT 3.0 - WINDOWS SETUP              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo       ✗ Python not found in PATH
    echo       💡 Please install Python 3.8+ from https://python.org
    pause & exit /b 1
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
    echo       ✓ Python %PYTHON_VERSION% found
)

REM Check pip
echo [2/5] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo       ✗ pip not found
    echo       💡 Please ensure pip is installed with Python
    pause & exit /b 1
) else (
    echo       ✓ pip available
)

REM Install requirements
echo [3/5] Installing Python dependencies...
if exist requirements.txt (
    echo       Installing from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo       ⚠ Some packages may have failed to install
        echo       💡 This is normal for packages that require system dependencies
    ) else (
        echo       ✓ Dependencies installed successfully
    )
) else (
    echo       ⚠ requirements.txt not found, installing core dependencies...
    pip install fastapi uvicorn python-socketio requests psutil
    echo       ✓ Core dependencies installed
)

REM Check Ollama
echo [4/5] Checking Ollama installation...
set "OLLAMA_CMD=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
if exist "%OLLAMA_CMD%" (
    echo       ✓ Ollama found at %OLLAMA_CMD%
) else (
    echo       ⚠ Ollama not found in default location
    echo       💡 Please install Ollama from https://ollama.ai
    echo       💡 After installation, run: ollama pull llama3.2:latest
)

REM Create config if missing
echo [5/5] Setting up configuration...
if not exist ultron_config.json (
    if exist ultron_config.json.example (
        copy ultron_config.json.example ultron_config.json >nul
        echo       ✓ Configuration created from example
    ) else (
        echo       ⚠ No configuration template found
        echo       💡 Creating minimal configuration...
        echo {> ultron_config.json
        echo   "use_voice": false,>> ultron_config.json
        echo   "use_gui": true,>> ultron_config.json
        echo   "use_vision": false,>> ultron_config.json
        echo   "llm_model": "llama3.2:latest",>> ultron_config.json
        echo   "log_level": "INFO",>> ultron_config.json
        echo   "voice_enabled": false,>> ultron_config.json
        echo   "vision_enabled": false,>> ultron_config.json
        echo   "memory_enabled": true,>> ultron_config.json
        echo   "tools_enabled": true>> ultron_config.json
        echo }>> ultron_config.json
        echo       ✓ Minimal configuration created
    )
) else (
    echo       ✓ Configuration already exists
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              ✅ WINDOWS SETUP COMPLETE                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🚀 To start ULTRON Agent:
echo     • Simple mode: python main_windows.py
echo     • Full mode:   run.bat
echo.
echo  🤖 To install AI models (if Ollama is installed):
echo     ollama pull llama3.2:latest
echo     ollama pull llava:7b
echo.
echo  📝 Configuration file: ultron_config.json
echo  🌐 Web GUI will be available at: http://localhost:8080/
echo.
echo ╚══════════════════════════════════════════════════════════════╝
echo.

pause
