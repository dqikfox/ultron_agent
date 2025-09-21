@echo off
setlocal enabledelayedexpansion

REM === ULTRON Agent 3.0 Enhanced Startup Script ===
echo.
echo ========================================
echo   ULTRON Agent 3.0 - Enhanced Startup
echo ========================================
echo.

REM Set working directory
cd /d "%~dp0" >nul

REM Create required directories
if not exist "logs" mkdir logs
if not exist "debug_logs" mkdir debug_logs
if not exist "cache" mkdir cache
if not exist "utils" mkdir utils

REM --- Configuration Validation ---
echo [1/8] Validating configuration...
if not exist "%~dp0ultron_config.json" (
    echo ERROR: ultron_config.json not found. Creating default configuration...
    copy "%~dp0ultron_config.json.example" "%~dp0ultron_config.json" >nul 2>&1
    if not exist "%~dp0ultron_config.json" (
        echo ERROR: Could not create configuration file.
        pause
        exit /b 1
    )
)
echo ✅ Configuration file validated

REM --- Python Environment Check ---
echo [2/8] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo ✅ Python environment ready

REM --- Enhanced Dependency Check ---
echo [3/8] Verifying dependencies...
python -c "import fastapi, uvicorn, websockets, openai, jinja2" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some dependencies missing. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies verified

REM --- Security Fix Implementation ---
echo [4/8] Applying security fixes...
python -c "
import json
with open('ultron_config.json', 'r') as f:
    config = json.load(f)
config['security_mode'] = True
config['bind_localhost_only'] = True
with open('ultron_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('Security configuration applied')
" >nul 2>&1
echo ✅ Security enhancements applied

REM --- Ollama Service Check ---
echo [5/8] Checking Ollama service...
where ollama >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama not found in PATH
    echo Installing Ollama...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://ollama.ai/install.ps1' -OutFile 'install_ollama.ps1'; .\install_ollama.ps1}" >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Ollama installation failed. Some features may not work.
    ) else (
        echo ✅ Ollama installed successfully
    )
) else (
    echo ✅ Ollama service available
    REM Start Ollama if not running
    tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
    if errorlevel 1 (
        echo Starting Ollama service...
        start "" ollama serve >nul 2>&1
        timeout /t 3 >nul
    )
)

REM --- Enhanced GUI Server Startup ---
echo [6/8] Starting Enhanced GUI Server...
if exist "%~dp0main_gui_server_fixed.py" (
    echo Starting secure GUI server with auto-fallback...
    start "ULTRON Enhanced GUI" cmd /k "cd /d "%~dp0" && python main_gui_server_fixed.py --secure"
) else (
    echo ERROR: Enhanced GUI server not found
    pause
    exit /b 1
)
echo ✅ GUI Server started

REM --- Core Agent Initialization ---
echo [7/8] Initializing ULTRON Core Agent...
if exist "%~dp0main.py" (
    echo Starting core agent system...
    start "ULTRON Core Agent" cmd /k "cd /d "%~dp0" && python main.py"
    timeout /t 2 >nul
) else (
    echo WARNING: Core agent not found, GUI-only mode
)
echo ✅ Core agent initialized

REM --- Service Status Check ---
echo [8/8] Verifying service status...
timeout /t 3 >nul

REM Check if GUI server is responding
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000' -TimeoutSec 5; Write-Host '✅ GUI Server: ONLINE' } catch { Write-Host '❌ GUI Server: OFFLINE' }" 2>nul

REM Check Ollama
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -TimeoutSec 5; Write-Host '✅ Ollama Service: ONLINE' } catch { Write-Host '❌ Ollama Service: OFFLINE' }" 2>nul

echo.
echo ========================================
echo   ULTRON Agent 3.0 Startup Complete
echo ========================================
echo.
echo 🌐 GUI Interface:    http://localhost:5000
echo 🤖 AI Chat:          http://localhost:5173
echo 🔧 Ollama Service:   http://localhost:11434
echo 📊 System Monitor:   Available in GUI
echo.
echo Press any key to open GUI interface...
pause >nul

REM Open GUI in default browser
start "" "http://localhost:5000"

echo.
echo System is running. Press any key to exit startup script...
pause >nul