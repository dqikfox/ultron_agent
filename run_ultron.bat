@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1

title ULTRON Agent 3.0 - Master Launcher

set "PYTHON_CMD=python"
set "OLLAMA_CMD=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
set "LOG_FILE=ultron_master_startup.log"
set "OLLAMA_PORT=11434"
set "WEB_GUI_PORT=8080"
set "OLLAMA_MODEL=llava:7b"

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║                   ULTRON AGENT 3.0 - MASTER LAUNCHER                      ║
echo ║                                                                            ║
echo ║                Intelligent • Fast • Reliable • Production-Ready            ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

:: CLEANUP
echo [1/8] Cleaning up existing processes...
powershell -Command "Get-Process python,ngrok,ollama -ErrorAction SilentlyContinue | Stop-Process -Force" >nul 2>&1
timeout /t 1 /nobreak >nul
echo       ✓ Cleanup complete
echo.

:: PRE-FLIGHT CHECKS
echo [2/8] Running pre-flight checks...
if not exist "web_gui_server.py" (
    echo       ✗ ERROR: web_gui_server.py not found
    pause
    exit /b 1
)
echo       ✓ GUI files verified
echo.

:: PYTHON VERIFICATION
echo [3/8] Verifying Python...
where %PYTHON_CMD% >nul 2>&1
if errorlevel 1 (
    echo       ✗ ERROR: Python not found
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo       ✓ Python %PYTHON_VERSION% detected
echo.

:: OLLAMA SERVICE
echo [4/8] Starting Ollama service...
curl -s http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1
if errorlevel 0 (
    echo       ✓ Ollama already running
    goto ollama_ready
)

if not exist "%OLLAMA_CMD%" (
    echo       ✗ ERROR: Ollama not found at %OLLAMA_CMD%
    echo          Install from https://ollama.ai
    pause
    exit /b 1
)

start "Ollama Service" /MIN "%OLLAMA_CMD%" serve
set "retry_count=0"

:ollama_retry
curl -s http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1
if errorlevel 0 (
    echo       ✓ Ollama service started
    goto ollama_ready
)
set /a retry_count+=1
if !retry_count! lss 5 (
    timeout /t 3 /nobreak >nul
    goto ollama_retry
)
echo       ✗ ERROR: Ollama failed to start
pause
exit /b 1

:ollama_ready
echo.

:: AI MODEL CHECK
echo [5/8] Checking AI model...
"%OLLAMA_CMD%" list 2>nul | findstr "%OLLAMA_MODEL%" >nul
if errorlevel 1 (
    echo       ⚠ Model not found - downloading (may take 10-30 min)...
    "%OLLAMA_CMD%" pull %OLLAMA_MODEL%
    if errorlevel 1 (
        echo       ✗ ERROR: Failed to download model
        pause
        exit /b 1
    )
)
echo       ✓ Model %OLLAMA_MODEL% ready
echo.

:: SYNTAX CHECK
echo [6/8] Validating Python syntax...
python -m py_compile "web_gui_server.py" >nul 2>&1
if errorlevel 1 (
    echo       ✗ ERROR: Syntax errors in web_gui_server.py
    pause
    exit /b 1
)
echo       ✓ Python syntax verified
echo.

:: START WEB GUI (PRIMARY SERVICE)
echo [7/8] Starting Web GUI Server...
echo       → Launching http://localhost:8080
start "ULTRON-WebGUI" /MIN python web_gui_server.py
timeout /t 8 /nobreak >nul
echo       ✓ Web GUI launched
echo.

:: OPEN BROWSER
echo [8/8] Opening web interface...
where chrome.exe >nul 2>&1
if errorlevel 0 (
    start chrome.exe "http://localhost:8080"
    goto browser_done
)
where msedge.exe >nul 2>&1
if errorlevel 0 (
    start msedge.exe "http://localhost:8080"
    goto browser_done
)
start "" "http://localhost:8080"

:browser_done
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo  ✅ ULTRON AGENT 3.0 READY
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo  🌐 PRIMARY GUI         → http://localhost:8080
echo  📱 ADB Manager         → http://localhost:8080/adb.html
echo  🎮 Avatar Game         → http://localhost:8080/ultron_avatar_game.html
echo.
echo  🤖 Ollama AI Backend   → http://localhost:11434
echo  ⚙️  Model Loaded        → %OLLAMA_MODEL%
echo.
echo  📝 Logs                → %LOG_FILE%
echo  ⏸️  Press Ctrl+C to stop all services
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo.

pause

echo.
echo Shutting down ULTRON services...
powershell -Command "Get-Process | Where-Object {$_.MainWindowTitle -like '*ULTRON*'} | Stop-Process -Force -ErrorAction SilentlyContinue" 2>nul
echo ✓ All services stopped
echo.

exit /b 0
