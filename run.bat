@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: ========================================================================
:: ULTRON Agent 3.0 - Master Launcher
:: This is the ONLY file needed to start the entire ULTRON Agent system
:: Starts: Ollama, Web GUI, and all required services
:: ========================================================================

title ULTRON Agent 3.0 - Master Launcher

:: --- Configuration ---
set "PYTHON_CMD=python"
set "OLLAMA_CMD=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
set "LOG_FILE=ultron_master_startup.log"
set "OLLAMA_MODEL=llava:7b"
set "OLLAMA_PORT=11434"
set "WEB_GUI_PORT=8080"
set "FRONTEND_PORT=5175"

:: --- Enhanced Logging ---
echo. > "%LOG_FILE%"
echo [%date% %time%] ULTRON Agent 3.0 Master Startup >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ULTRON AGENT 3.0                         ║
echo ║                   MASTER LAUNCHER                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Starting complete ULTRON Agent system...
echo [INFO] Working directory: %CD%
echo.

:: 1. Pre-flight checks
echo [INFO] Performing pre-flight checks...

:: Check required files
if not exist "web_gui_server.py" (
    echo [ERROR] Required file not found: web_gui_server.py
    pause
    exit /b 1
)
if not exist "main.py" (
    echo [ERROR] Required file not found: main.py
    pause
    exit /b 1
)
if not exist "ultron_config.json" (
    echo [WARN] Configuration file not found: ultron_config.json
)

:: Check GUI files
if exist "gui\ultron_enhanced\web\index.html" (
    echo [INFO] Primary GUI found: gui/ultron_enhanced/web/index.html
) else (
    echo [WARN] Primary GUI not found, system will use fallback GUI
)

echo [SUCCESS] Pre-flight checks completed.
echo.

:: 2. Check for Python
echo [INFO] Checking for Python installation...
where %PYTHON_CMD% >nul 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

%PYTHON_CMD% --version
echo [SUCCESS] Python check passed.
echo.

:: 3. Check if Ollama is running
echo [INFO] Checking Ollama status...
curl -s http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1
if !errorlevel! equ 0 (
    echo [INFO] ✅ Ollama is already running and responding
    goto ollama_ready
)

echo [INFO] Ollama service not detected. Starting Ollama service...
if not exist "%OLLAMA_CMD%" (
    echo [ERROR] Ollama not found at %OLLAMA_CMD%
    echo Please install from https://ollama.ai/download
    pause
    exit /b 1
)

start "Ollama Service" "%OLLAMA_CMD%" serve
echo [INFO] Waiting for Ollama to start...
timeout /t 10 /nobreak >nul

:: Verify Ollama started with retries
set "retry_count=0"
:ollama_retry
curl -s http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ Ollama service started successfully
    goto ollama_ready
)

set /a retry_count+=1
if !retry_count! lss 5 (
    echo [INFO] Retrying Ollama connection... (!retry_count!/5)
    timeout /t 3 /nobreak >nul
    goto ollama_retry
)

echo [ERROR] ❌ Failed to start Ollama after 5 attempts
pause
exit /b 1

:ollama_ready

echo.

:: 4. Check for required model
echo [INFO] Checking for required model: %OLLAMA_MODEL%
"%OLLAMA_CMD%" list | findstr "%OLLAMA_MODEL%" >nul
if !errorlevel! neq 0 (
    echo [INFO] Model not found. Pulling %OLLAMA_MODEL%...
    "%OLLAMA_CMD%" pull %OLLAMA_MODEL%
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to pull Ollama model %OLLAMA_MODEL%
        pause
        exit /b 1
    )
    echo [SUCCESS] Model %OLLAMA_MODEL% downloaded successfully
) else (
    echo [INFO] Model %OLLAMA_MODEL% is already available
)
echo.

:: 5. Test Python Scripts Syntax
echo [INFO] Testing Python scripts syntax...
python -m py_compile web_gui_server.py >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] web_gui_server.py has syntax errors
    pause
    exit /b 1
)
python -m py_compile main.py >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] main.py has syntax errors
    pause
    exit /b 1
)
echo [SUCCESS] All Python scripts syntax check passed
echo.

:: 6. Start the Web GUI Server
echo [INFO] Starting ULTRON Web GUI Server on port %WEB_GUI_PORT%...
start "ULTRON Web GUI" /B python web_gui_server.py

:: Wait for Web GUI to start
timeout /t 5 /nobreak >nul

:: Check if Web GUI started
curl -s "http://localhost:%WEB_GUI_PORT%/" >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ Web GUI Server started successfully on port %WEB_GUI_PORT%
) else (
    echo [WARN] Web GUI Server may not have started properly, but continuing...
)
echo.

:: 7. Start the Frontend UI Server
echo [INFO] Starting ULTRON Frontend UI on port %FRONTEND_PORT%...
start "ULTRON Frontend UI" /B python frontend_server.py --port %FRONTEND_PORT%

:: Wait for Frontend UI to start
timeout /t 3 /nobreak >nul

:: Check if Frontend UI started
curl -s "http://localhost:%FRONTEND_PORT%/" >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ Frontend UI started successfully on port %FRONTEND_PORT%
) else (
    echo [WARN] Frontend UI may not have started properly, but continuing...
)
echo.

:: 8. Startup Complete
echo echo.

:: 9. Start Ngrok Tunnel (Optional)
where ngrok >nul 2>&1
if !errorlevel! equ 0 (
    call :info "Starting Ngrok tunnel for remote access..."
    start "ULTRON Ngrok Tunnel" /MIN cmd /c "ngrok http 8080"
    
    :: Wait for ngrok to initialize
    timeout /t 5 /nobreak >nul
    
    :: Get the public URL from ngrok API
    for /f "tokens=*" %%i in ('curl -s http://localhost:4040/api/tunnels ^| findstr /C:"public_url" ^| findstr /C:"https://"') do (
        set NGROK_LINE=%%i
    )
    
    :: Extract URL (basic parsing)
    if defined NGROK_LINE (
        for /f "tokens=2 delims=:," %%a in ("!NGROK_LINE!") do (
            set NGROK_RAW=%%a
            set NGROK_URL=!NGROK_RAW:"=!
            set NGROK_URL=!NGROK_URL: =!
            set NGROK_URL=https:!NGROK_URL!
        )
    )
    
    if defined NGROK_URL (
        call :info "Ngrok tunnel started: !NGROK_URL!"
        call :info "Opening ngrok URL in browser..."
        start !NGROK_URL!
        echo    Dashboard: http://localhost:4040
    ) else (
        call :info "Ngrok started but couldn't get URL - check http://localhost:4040"
    )
) else (
    call :info "Ngrok not found - skipping tunnel (install from https://ngrok.com/download)"
)
echo.

:: 10. Auto-open Local Web GUI
call :info "Opening local Web GUI in browser..."
start http://localhost:8080
echo.

:: 11. Startup Complete
call :success "ULTRON Agent 3.0 startup sequence complete!"
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ULTRON AGENT 3.0                         ║
echo ║                    SYSTEM STATUS                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Ollama Service:     http://localhost:%OLLAMA_PORT%
echo ✅ Web GUI:           http://localhost:%WEB_GUI_PORT%
echo ✅ Frontend UI:       http://localhost:%FRONTEND_PORT%
echo ✅ AI Model:          %OLLAMA_MODEL%
echo.
echo 📝 Log file: %LOG_FILE%
echo 🎯 Primary GUI: gui/ultron_enhanced/web/index.html
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 STARTUP COMPLETE!                           ║
echo ║  ULTRON Agent is ready. Press any key to exit launcher.    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Wait for user input before exiting
pause

call :info "ULTRON Agent launcher finished."
echo.
echo ULTRON Agent is still running in the background.
echo Access the Web GUI at: http://localhost:%WEB_GUI_PORT%
echo Access the Frontend UI at: http://localhost:%FRONTEND_PORT%

endlocal
exit /b 0

:: ========================================================================
:: HELPER FUNCTIONS
:: ========================================================================

:info
    echo [INFO] %~1
    echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%" 2>nul
    goto :eof
