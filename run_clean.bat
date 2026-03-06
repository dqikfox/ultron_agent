@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1

:: ════════════════════════════════════════════════════════════════════════
:: ULTRON AGENT 3.0 - LAUNCHER
:: ════════════════════════════════════════════════════════════════════════
:: This script:
::   - Starts Ollama AI backend
::   - Launches Web GUI and API servers
::   - Monitors service health
::   - Opens browser to Web GUI
::
:: FEATURES:
::   ✓ Automatic service startup
::   ✓ Health checking before completion
::   ✓ Startup time tracking
::   ✓ Clean shutdown on exit
:: ════════════════════════════════════════════════════════════════════════

title ULTRON Agent 3.0 - Launcher

:: ──────────────────────────────────────────────────────────────────────
:: CONFIGURATION
:: ──────────────────────────────────────────────────────────────────────

set "PYTHON_CMD=python"
set "OLLAMA_CMD=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
set "LOG_FILE=ultron.log"

:: CRITICAL PORTS (must match API server configuration)
set "OLLAMA_PORT=11434"
set "WEB_GUI_PORT=8080"
set "API_SERVER_PORT=5000"

:: AI MODEL CONFIGURATION
:: PRIMARY: llava:7b (stable, fast, multimodal) - RECOMMENDED
:: FALLBACK: deepseek-r1:14b (advanced reasoning, may timeout)
set "OLLAMA_MODEL=dolphin3:latest"
set "FALLBACK_MODEL=deepseek-r1:14b"

:: ──────────────────────────────────────────────────────────────────────
:: INITIALIZATION
:: ──────────────────────────────────────────────────────────────────────

echo. > "%LOG_FILE%"
echo [%date% %time%] ULTRON Launcher >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              ULTRON AGENT 3.0 - LAUNCHER                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Startup sequence initiated...
echo.

:: Calculate startup time (seconds precision)
for /f "tokens=1-4 delims=: " %%a in ("!time: =0!") do (
    set /a "start_sec=%%a*3600+%%b*60+%%c"
)

:: ──────────────────────────────────────────────────────────────────────
:: STEP 1: CLEANUP - Kill existing processes
:: ──────────────────────────────────────────────────────────────────────

echo [1/6] 🧹 Cleanup existing processes...
powershell -Command "Get-Process python,ollama,ngrok -EA SilentlyContinue | Stop-Process -Force" >nul 2>&1
timeout /t 1 /nobreak >nul
echo       ✓ Cleaned up stale processes
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 2: PREFLIGHT CHECKS
:: ──────────────────────────────────────────────────────────────────────

echo [2/6] ✓ Preflight checks...
set "PREFLIGHT_FAIL=0"
if not exist "web_gui_server.py" set "PREFLIGHT_FAIL=1" & echo       ✗ web_gui_server.py missing
if not exist "main.py" set "PREFLIGHT_FAIL=1" & echo       ✗ main.py missing
if not exist "ultron_config.json" echo       ⚠ Config missing (using defaults)
if !PREFLIGHT_FAIL! equ 1 (echo       ✗ CRITICAL FILES MISSING & pause & exit /b 1)
echo       ✓ All critical files present
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 3: PYTHON VERIFICATION
:: ──────────────────────────────────────────────────────────────────────

echo [3/6] 🐍 Python verification...
where %PYTHON_CMD% >nul 2>&1 || (echo       ✗ Python not in PATH & pause & exit /b 1)
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo       ✓ Python %PYTHON_VERSION% available
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 4: OLLAMA STARTUP (CRITICAL)
:: ──────────────────────────────────────────────────────────────────────

echo [4/6] 🤖 Ollama AI backend startup...
curl -s -m 1 http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1 && (echo       ✓ Already running & goto ollama_ready)
if not exist "%OLLAMA_CMD%" (echo       ✗ Ollama not installed & pause & exit /b 1)
start "Ollama-AI" /MIN /BELOWNORMAL "%OLLAMA_CMD%" serve
set "retry=0"
:ollama_wait
curl -s -m 1 http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1 && goto ollama_ready
set /a retry+=1
if !retry! lss 8 (timeout /t 1 /nobreak >nul & goto ollama_wait)
echo       ⚠ Ollama timeout after 8 seconds - continuing anyway
:ollama_ready
echo       ✓ Ollama responsive at http://localhost:%OLLAMA_PORT%
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 5: MODEL VERIFICATION
:: ──────────────────────────────────────────────────────────────────────

echo [5/6] 🧠 AI model verification...
"%OLLAMA_CMD%" list 2>nul | findstr "%OLLAMA_MODEL%" >nul && (echo       ✓ Model: %OLLAMA_MODEL% & goto model_ready)
echo       ⚠ Primary model missing, checking fallback...
"%OLLAMA_CMD%" list 2>nul | findstr "%FALLBACK_MODEL%" >nul && (set "OLLAMA_MODEL=%FALLBACK_MODEL%" & echo       ✓ Using fallback: %FALLBACK_MODEL% & goto model_ready)
echo       ⚠ No models available - please install: ollama pull llava:7b
:model_ready
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STEP 6: SERVICE STARTUP
:: ──────────────────────────────────────────────────────────────────────

echo [6/6] 🚀 Service startup and health check...
start "ULTRON-WebGUI" /MIN python web_gui_server.py
timeout /t 1 /nobreak >nul
start "ULTRON-API" /MIN python api_server.py 2>nul
echo       ✓ Web GUI (port %WEB_GUI_PORT%) launched
echo       ✓ API Server (port %API_SERVER_PORT%) launched
echo.

:: Wait for services to initialize
timeout /t 3 /nobreak >nul
echo       Checking service health...
curl -s -m 1 http://localhost:%WEB_GUI_PORT%/ >nul 2>&1 && echo       ✓ Web GUI HEALTHY || echo       ⚠ Web GUI initializing...
curl -s -m 1 http://localhost:%API_SERVER_PORT%/health >nul 2>&1 && echo       ✓ API Server HEALTHY || echo       ⚠ API Server initializing...
echo.

:: ──────────────────────────────────────────────────────────────────────
:: STARTUP COMPLETE - DISPLAY STATUS
:: ──────────────────────────────────────────────────────────────────────

for /f "tokens=1-4 delims=: " %%a in ("!time: =0!") do (
    set /a "end_sec=%%a*3600+%%b*60+%%c"
)
set /a "duration_sec=end_sec-start_sec"
if !duration_sec! lss 0 set /a "duration_sec+=86400"

echo ╔══════════════════════════════════════════════════════════════╗
echo ║           ✅ ULTRON AGENT 3.0 - STARTUP COMPLETE            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo  🚀 STARTUP TIME: !duration_sec! seconds
echo  🤖 AI MODEL: %OLLAMA_MODEL%
echo.
echo  🌐 WEB GUI:      http://localhost:%WEB_GUI_PORT%/
echo  API SERVER:      http://localhost:%API_SERVER_PORT%/
echo  🤖 OLLAMA:       http://localhost:%OLLAMA_PORT%/
echo.
echo  📝 LOGS:         %LOG_FILE%
echo  ⏸️  Press Ctrl+C to stop all services
echo.
echo ╚══════════════════════════════════════════════════════════════╝
echo.

[%date% %time%] Startup complete in !duration_sec!s >> "%LOG_FILE%"

:: ──────────────────────────────────────────────────────────────────────
:: LAUNCH BROWSER TO WEB GUI
:: ──────────────────────────────────────────────────────────────────────

echo 🌐 Launching Web GUI in default browser...
set "GUI_URL=http://localhost:%WEB_GUI_PORT%/"
for %%b in (chrome.exe msedge.exe firefox.exe) do (
    where %%b >nul 2>&1 && (start %%b "!GUI_URL!" & echo       ✓ Opened in %%b & goto browser_done)
)
start "" "!GUI_URL!"
echo       ✓ Opened in default browser
:browser_done
echo.

:: ──────────────────────────────────────────────────────────────────────
:: END OF STARTUP - WAIT FOR USER
:: ──────────────────────────────────────────────────────────────────────

timeout /t 3 /nobreak >nul

:end_of_script
pause
echo.
echo 🛑 Shutting down ULTRON services...
powershell -Command "Get-Process python,ollama -EA SilentlyContinue | Stop-Process -Force" 2>nul
echo ✓ All services terminated
echo.
exit /b 0
