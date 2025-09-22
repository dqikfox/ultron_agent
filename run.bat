@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: --- ULTRON AGENT 3.0 MASTER LAUNCHER ---
:: This is the ONLY file needed to start the entire ULTRON Agent system
:: Starts: Ollama, Bridge, Web GUI, API Server, and all required services

:: --- Configuration ---
set "PYTHON_CMD=python"
set "OLLAMA_CMD=ollama"
set "LOG_FILE=ultron_master_startup.log"
set "OLLAMA_MODEL=qwen3-coder:480b-cloud"
set "OLLAMA_PORT=11434"
set "BRIDGE_PORT=5001"
set "WEB_GUI_PORT=8080"
set "API_PORT=5000"

:: --- Title ---
title ULTRON Agent 3.0 - Master Launcher

:: --- Enhanced Logging ---
echo. > "%LOG_FILE%"
echo [%date% %time%] ULTRON Agent 3.0 Master Startup >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

:: --- Functions ---

:info
    echo [INFO] %~1
    echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%"
    goto :eof

:warn
    echo [WARN] %~1
    echo [%date% %time%] [WARN] %~1 >> "%LOG_FILE%"
    goto :eof

:error
    echo [ERROR] %~1
    echo [%date% %time%] [ERROR] %~1 >> "%LOG_FILE%"
    echo.
    echo Press any key to view the log file and exit...
    pause > nul
    notepad "%LOG_FILE%"
    exit /b 1

:success
    echo [SUCCESS] %~1
    echo [%date% %time%] [SUCCESS] %~1 >> "%LOG_FILE%"
    goto :eof

:check_file
    if not exist "%~1" (
        call :error "Required file not found: %~1"
    )
    goto :eof

:check_port
    netstat -an | find ":%~1 " >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PORT] Port %~1 is already in use
        exit /b 1
    ) else (
        echo [PORT] Port %~1 is available
        exit /b 0
    )
    goto :eof

:wait_for_service
    setlocal
    set "url=%~1"
    set "service_name=%~2"
    set "max_attempts=%~3"
    set "attempt=1"

    :retry_loop
    if !attempt! gtr %max_attempts% (
        echo [TIMEOUT] %service_name% failed to start after %max_attempts% attempts
        endlocal & exit /b 1
    )

    echo [WAIT] Checking %service_name% (attempt !attempt!/%max_attempts%)...
    curl -s "%url%" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] %service_name% is responding at %url%
        endlocal & exit /b 0
    )

    timeout /t 3 /nobreak >nul
    set /a "attempt+=1"
    goto retry_loop
    goto :eof

:: --- Main Script ---

call :info "=== ULTRON AGENT 3.0 MASTER LAUNCHER ==="
call :info "Starting complete ULTRON Agent system..."
call :info "Working directory: %CD%"

:: 0. Pre-flight checks
call :info "Performing comprehensive pre-flight checks..."

:: Check required files
call :check_file "ultron_bridge.py"
call :check_file "web_gui_server.py"
call :check_file "api_server.py"
call :check_file "main.py"
call :check_file "requirements.txt"
call :check_file "requirements_bridge.txt"
call :check_file "ultron_config.json"

:: Check GUI files
if exist "gui\ultron_enhanced\web\index.html" (
    call :info "Primary GUI found: gui/ultron_enhanced/web/index.html"
) else (
    call :warn "Primary GUI not found, system will use fallback GUI"
)

call :success "Pre-flight checks completed."

:: 1. Check for Python
call :info "Checking for Python installation..."
where %PYTHON_CMD% >nul 2>nul
if !errorlevel! neq 0 (
    call :error "Python is not installed or not in PATH. Please install Python 3.8+ from https://python.org"
)

:: Test Python version
%PYTHON_CMD% --version > temp_version.txt 2>&1
if !errorlevel! neq 0 (
    call :error "Python is not working correctly."
)

set /p python_version=<temp_version.txt
del temp_version.txt
call :success "Python check passed. Version: %python_version%"

:: 2. Install/Upgrade Dependencies
call :info "Installing/updating Python dependencies..."
%PYTHON_CMD% -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
%PYTHON_CMD% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "Failed to install main dependencies. Check %LOG_FILE% for details."
)
%PYTHON_CMD% -m pip install -r requirements_bridge.txt >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "Failed to install bridge dependencies. Check %LOG_FILE% for details."
)
call :success "All Python dependencies installed successfully."

:: 3. Check and Start Ollama Service
call :info "Checking Ollama installation and service..."
where %OLLAMA_CMD% >nul 2>nul
if !errorlevel! neq 0 (
    call :error "Ollama is not installed. Please install from https://ollama.ai/download"
)

:: Check if Ollama is already running
call :check_port "%OLLAMA_PORT%"
if !errorlevel! equ 0 (
    call :info "Starting Ollama service..."
    start "Ollama Service" %OLLAMA_CMD% serve
    timeout /t 5 /nobreak >nul
) else (
    call :info "Ollama service appears to be running already."
)

:: Wait for Ollama to be ready
call :wait_for_service "http://localhost:%OLLAMA_PORT%/api/tags" "Ollama API" "10"
if !errorlevel! neq 0 (
    call :error "Ollama service failed to start properly."
)

:: Check if model is available, pull if needed
%OLLAMA_CMD% list | find "%OLLAMA_MODEL%" >nul 2>&1
if !errorlevel! neq 0 (
    call :info "Pulling Ollama model: %OLLAMA_MODEL%"
    %OLLAMA_CMD% pull %OLLAMA_MODEL%
    if !errorlevel! neq 0 (
        call :error "Failed to pull Ollama model %OLLAMA_MODEL%"
    )
    call :success "Ollama model %OLLAMA_MODEL% downloaded successfully."
) else (
    call :info "Ollama model %OLLAMA_MODEL% is already available."
)

call :success "Ollama service is ready and model loaded."

:: 4. Test Python Scripts Syntax
call :info "Testing Python scripts syntax..."
%PYTHON_CMD% -m py_compile ultron_bridge.py >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "ultron_bridge.py has syntax errors."
)
%PYTHON_CMD% -m py_compile web_gui_server.py >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "web_gui_server.py has syntax errors."
)
%PYTHON_CMD% -m py_compile api_server.py >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "api_server.py has syntax errors."
)
%PYTHON_CMD% -m py_compile main.py >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "main.py has syntax errors."
)
call :success "All Python scripts syntax check passed."

:: 5. Start Services in Background
call :info "Starting ULTRON Agent services..."

:: Start API Server in background
call :info "Starting API Server on port %API_PORT%..."
start "ULTRON API Server" /B %PYTHON_CMD% api_server.py

:: Wait a moment for API server to start
timeout /t 3 /nobreak >nul

:: Check if API server started
call :wait_for_service "http://localhost:%API_PORT%/health" "API Server" "5"
if !errorlevel! neq 0 (
    call :warn "API Server may not have started properly, but continuing..."
) else (
    call :success "API Server started successfully on port %API_PORT%"
)

:: Start Web GUI Server in background
call :info "Starting Web GUI Server on port %WEB_GUI_PORT%..."
start "ULTRON Web GUI" /B %PYTHON_CMD% web_gui_server.py

:: Wait for Web GUI to start
timeout /t 5 /nobreak >nul

:: Check if Web GUI started (try a few times)
call :wait_for_service "http://localhost:%WEB_GUI_PORT%/" "Web GUI Server" "8"
if !errorlevel! neq 0 (
    call :warn "Web GUI Server may not have started properly, but continuing..."
) else (
    call :success "Web GUI Server started successfully on port %WEB_GUI_PORT%"
)

:: 6. Start Main ULTRON Bridge (this will be the primary interface)
call :info "Starting ULTRON Bridge (main interface) on port %BRIDGE_PORT%..."
call :success "ULTRON Agent 3.0 startup sequence complete!"
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ULTRON AGENT 3.0                         ║
echo ║                    SYSTEM STATUS                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Ollama Service:     http://localhost:%OLLAMA_PORT%
echo ✅ ULTRON Bridge:      http://localhost:%BRIDGE_PORT%
echo ✅ Web GUI:           http://localhost:%WEB_GUI_PORT%
echo ✅ API Server:        http://localhost:%API_PORT%
echo.
echo 📝 Log file: %LOG_FILE%
echo 🔧 Configuration: ultron_config.json
echo 🎯 Primary GUI: gui/ultron_enhanced/web/index.html
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 STARTUP COMPLETE!                           ║
echo ║  All services are running. Press Ctrl+C to stop all.       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Start the main bridge in foreground (this will be interactive)
%PYTHON_CMD% ultron_bridge.py

:: Cleanup on exit
call :info "ULTRON Agent shutdown initiated..."
call :info "Stopping background services..."

:: Kill background processes (this is a simple approach)
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq ULTRON API Server" >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq ULTRON Web GUI" >nul 2>&1

call :success "ULTRON Agent shutdown complete."
echo.
echo Press any key to exit...
pause > nul

endlocal
exit /b %EXIT_CODE%
