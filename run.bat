@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1

:: ========================================================================
:: ULTRON Agent 3.0 - Master Launcher
:: ========================================================================
:: Purpose: Single-command startup for complete ULTRON Agent system
:: Services: Ollama LLM, Web GUI (8080), Frontend UI (5175), NVIDIA Chat (8002)
:: Dependencies: Python 3.8+, Ollama, Web browser
:: Usage: Just run this file - everything starts automatically
:: ========================================================================

title ULTRON Agent 3.0 - Master Launcher

:: ──────────────────────────────────────────────────────────────────────
:: CONFIGURATION SECTION
:: ──────────────────────────────────────────────────────────────────────
:: Customize these settings if needed

set "PYTHON_CMD=python"
set "OLLAMA_CMD=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
set "LOG_FILE=ultron_master_startup.log"
set "OLLAMA_MODEL=llava:7b"
set "OLLAMA_PORT=11434"
set "WEB_GUI_PORT=8080"
set "FRONTEND_PORT=5175"
set "NVIDIA_CHAT_PORT=8002"

set "NVIDIA_CHAT_PORT=8002"

:: ──────────────────────────────────────────────────────────────────────
:: INITIALIZATION
:: ──────────────────────────────────────────────────────────────────────
:: Initialize logging and display startup banner

:: Create/clear log file
echo. > "%LOG_FILE%"
echo [%date% %time%] ULTRON Agent 3.0 Master Startup >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ULTRON AGENT 3.0                         ║
echo ║                   MASTER LAUNCHER                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Starting ULTRON Agent system...
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 0: CLEANUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Stop any existing ULTRON processes to prevent conflicts
:: Targets: Python, Ngrok, Ollama processes

echo [1/9] Cleaning up existing processes...
powershell -Command "Get-Process python,ngrok,ollama -ErrorAction SilentlyContinue | Stop-Process -Force" >nul 2>&1
timeout /t 2 /nobreak >nul
echo       ✓ Cleanup complete
echo.

echo       ✓ Cleanup complete
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 1: PRE-FLIGHT CHECKS
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Verify required files exist before starting services
:: Checks: Python scripts, configuration files, GUI files

echo [2/9] Running pre-flight checks...

:: Check critical Python files
if not exist "web_gui_server.py" (
    echo       ✗ ERROR: web_gui_server.py not found
    pause
    exit /b 1
)
if not exist "main.py" (
    echo       ✗ ERROR: main.py not found
    pause
    exit /b 1
)

:: Check configuration (warning only)
if not exist "ultron_config.json" (
    echo       ⚠ WARNING: ultron_config.json not found ^(using defaults^)
) >nul 2>&1

:: Check GUI directory
if exist "gui\ultron_enhanced\web\index.html" (
    echo       ✓ GUI files verified
) else (
    echo       ⚠ WARNING: Primary GUI not found ^(fallback will be used^)
)

echo       ✓ Pre-flight checks passed
echo.

echo       ✓ Pre-flight checks passed
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 2: PYTHON VERIFICATION
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Ensure Python is installed and accessible
:: Requirement: Python 3.8 or higher

echo [3/9] Verifying Python installation...
where %PYTHON_CMD% >nul 2>&1
if !errorlevel! neq 0 (
    echo       ✗ ERROR: Python not found in PATH
    echo       Install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Get Python version silently
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo       ✓ Python %PYTHON_VERSION% detected
echo.

echo       ✓ Python %PYTHON_VERSION% detected
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 3: OLLAMA SERVICE STARTUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Start Ollama LLM backend for AI reasoning
:: Port: 11434
:: Dependency: All AI features require Ollama running

echo [4/9] Starting Ollama service...

:: Check if already running
curl -s http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ Ollama already running
    goto ollama_ready
)

:: Verify Ollama installation
if not exist "%OLLAMA_CMD%" (
    echo       ✗ ERROR: Ollama not found
    echo       Install from https://ollama.ai/download
    pause
    exit /b 1
)

:: Start Ollama service in background
start "Ollama Service" /MIN "%OLLAMA_CMD%" serve
timeout /t 10 /nobreak >nul

:: Verify startup with retry logic (max 5 attempts)
set "retry_count=0"
:ollama_retry
curl -s http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ Ollama service started
    goto ollama_ready
)

set /a retry_count+=1
if !retry_count! lss 5 (
    timeout /t 3 /nobreak >nul
    goto ollama_retry
)

echo       ✗ ERROR: Ollama failed to start after 5 attempts
pause
exit /b 1

:ollama_ready
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 4: AI MODEL VERIFICATION
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Ensure required AI model is downloaded
:: Model: llava:7b (multimodal vision-enabled LLM)
:: Note: First-time download may take 10-30 minutes

echo [5/9] Checking AI model...
"%OLLAMA_CMD%" list 2>nul | findstr "%OLLAMA_MODEL%" >nul
if !errorlevel! neq 0 (
    echo       ⚠ Model %OLLAMA_MODEL% not found - downloading...
    "%OLLAMA_CMD%" pull %OLLAMA_MODEL%
    if !errorlevel! neq 0 (
        echo       ✗ ERROR: Failed to download model
        pause
        exit /b 1
    )
    echo       ✓ Model downloaded successfully
) else (
    echo       ✓ Model %OLLAMA_MODEL% ready
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 5: PYTHON SYNTAX VALIDATION
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Quick syntax check of core Python files
:: Files tested: main.py, web_gui_server.py

echo [6/9] Validating Python scripts...
set SYNTAX_ERROR=0
for %%f in (web_gui_server.py main.py) do (
    python -m py_compile "%%f" >nul 2>&1
    if !errorlevel! neq 0 (
        echo       ✗ Syntax error in %%f
        set SYNTAX_ERROR=1
    )
)
if !SYNTAX_ERROR! equ 1 (
    echo       ✗ ERROR: Python syntax errors detected
    pause
    exit /b 1
)
echo       ✓ All scripts valid
echo.

:: ──────────────────────────────────────────────────────────────────────
:: ──────────────────────────────────────────────────────────────────────
:: STEP 6: WEB GUI SERVER STARTUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Launch Pokédex-style web interface (PRIMARY GUI)
:: Port: 8080 (configurable via WEB_GUI_PORT)
:: Endpoint: http://localhost:8080/

echo [7/9] Starting Web GUI Server (port %WEB_GUI_PORT%)...
start "ULTRON Web GUI" /MIN python web_gui_server.py
timeout /t 5 /nobreak >nul

curl -s "http://localhost:%WEB_GUI_PORT%/" >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ Web GUI Server running
) else (
    echo       ⚠ Web GUI Server may not have started
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 7: FRONTEND UI SERVER STARTUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Alternative frontend interface
:: Port: 5175 (configurable via FRONTEND_PORT)
:: Endpoint: http://localhost:5175/

echo [8/11] Starting Frontend UI Server (port %FRONTEND_PORT%)...
start "ULTRON Frontend UI" /MIN python frontend_server.py --port %FRONTEND_PORT%
timeout /t 3 /nobreak >nul

curl -s "http://localhost:%FRONTEND_PORT%/" >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ Frontend UI Server running
) else (
    echo       ⚠ Frontend UI Server may not have started
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 8: NVIDIA ENHANCED CHAT SERVER STARTUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: NVIDIA-enhanced AI chat service
:: Port: 8002 (configurable via NVIDIA_CHAT_PORT)
:: Endpoint: http://localhost:8002/health

echo [9/11] Starting NVIDIA Chat Server (port 8002)...
start "ULTRON NVIDIA Chat" /MIN python nvidia_enhanced_ultron.py
timeout /t 3 /nobreak >nul

curl -s "http://localhost:8002/health" >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ NVIDIA Chat Server running
) else (
    echo       ⚠ NVIDIA Chat Server may not have started
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 9: API SERVER STARTUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: REST API for ULTRON services
:: Port: 5000
:: Endpoint: http://localhost:5000/health

echo [10/11] Starting API Server (port 5000)...
start "ULTRON API Server" /MIN python api_server.py
timeout /t 3 /nobreak >nul

curl -s "http://localhost:5000/health" >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ API Server running
) else (
    echo       ⚠ API Server may not have started
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 10: DIAGNOSTICS DASHBOARD STARTUP
:: ──────────────────────────────────────────────────────────────────────
:: Purpose: Real-time crash reporting and performance monitoring
:: Port: 5001 (configurable via diagnostics_dashboard_port in config)
:: Endpoint: http://localhost:5001

echo [11/11] Starting Diagnostics Dashboard (port 5001)...
start "ULTRON Diagnostics" /MIN python -m diagnostics.diagnostics_dashboard
timeout /t 3 /nobreak >nul

curl -s "http://localhost:5001/" >nul 2>&1
if !errorlevel! equ 0 (
    echo       ✓ Diagnostics Dashboard running
) else (
    echo       ⚠ Diagnostics Dashboard may not have started
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 11: STARTUP COMPLETE
:: ──────────────────────────────────────────────────────────────────────

:: Optional: Start Ngrok tunnel for remote access
where ngrok >nul 2>&1
if !errorlevel! equ 0 (
    echo [OPTIONAL] Starting Ngrok tunnel...
    start "ULTRON Ngrok Tunnel" /MIN cmd /c "ngrok http 8080"
    timeout /t 5 /nobreak >nul

    for /f "tokens=*" %%i in ('curl -s http://localhost:4040/api/tunnels ^| findstr /C:"public_url" ^| findstr /C:"https://"') do (
        set NGROK_LINE=%%i
    )

    if defined NGROK_LINE (
        for /f "tokens=2 delims=:," %%a in ("!NGROK_LINE!") do (
            set NGROK_RAW=%%a
            set NGROK_URL=!NGROK_RAW:"=!
            set NGROK_URL=!NGROK_URL: =!
            set NGROK_URL=https:!NGROK_URL!
        )
    )

    if defined NGROK_URL (
        echo          ✓ Ngrok tunnel: !NGROK_URL!
        echo          Dashboard: http://localhost:4040
    ) else (
        echo          ⚠ Ngrok started - check http://localhost:4040 for URL
    )
) else (
    echo          - Ngrok not installed (optional)
)
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STARTUP SUMMARY
:: ──────────────────────────────────────────────────────────────────────

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  🚀 ULTRON AGENT 3.0 READY                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo    Services Running:
echo    • Ollama LLM       : http://localhost:%OLLAMA_PORT%
echo    • Web GUI          : http://localhost:%WEB_GUI_PORT%
echo    • Frontend UI      : http://localhost:%FRONTEND_PORT%
echo    • NVIDIA Chat      : http://localhost:8002
echo    • API Server       : http://localhost:5000
echo    • Diagnostics      : http://localhost:5001
echo.
echo    Opening Web GUI in browser...
echo.

:: Auto-open PRIMARY GUI only (Web GUI on port 8080)
start http://localhost:%WEB_GUI_PORT%

echo    Press any key to stop all services...
pause
echo.
echo    Shutting down ULTRON services...
echo.

:: ──────────────────────────────────────────────────────────────────────
:: HELPER FUNCTIONS
:: ──────────────────────────────────────────────────────────────────────

:: ──────────────────────────────────────────────────────────────────────
:: HELPER FUNCTIONS
:: ──────────────────────────────────────────────────────────────────────

:info
echo [INFO] %~1
echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%" 2>nul
goto :eof

:success
echo [SUCCESS] %~1
echo [%date% %time%] [SUCCESS] %~1 >> "%LOG_FILE%" 2>nul
goto :eof

:error
echo [ERROR] %~1
echo [%date% %time%] [ERROR] %~1 >> "%LOG_FILE%" 2>nul
goto :eof
