@echo off
setlocal EnableDelayedExpansion
title ULTRON Agent 2.0 - Startup Manager
color 0A

:: Enhanced batch features
set "LOG_FILE=%~dp0startup.log"
set "ERROR_LOG=%~dp0error.log"
set "SCRIPT_DIR=%~dp0"
set "TIMESTAMP=%DATE% %TIME%"

echo ===============================================
echo  ULTRON Agent 2.0 - AI Assistant Startup
echo ===============================================
echo [%TIMESTAMP%] Starting ULTRON Agent initialization...
echo [%TIMESTAMP%] Starting ULTRON Agent initialization... >> "%LOG_FILE%"

:: Change to project directory
cd /d "%SCRIPT_DIR%"
echo [INFO] Working directory: %CD%

:: System Information Display
echo.
echo [SYSTEM INFO] Gathering system information...
echo Computer: %COMPUTERNAME%
echo User: %USERNAME%
echo OS Version: 
ver
echo Current Time: %DATE% %TIME%
echo Working Directory: %CD%

:: Enhanced Python Detection
echo.
echo [CHECK] Verifying Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo [ERROR] Please install Python 3.8 or higher from https://python.org
    echo [ERROR] Make sure to add Python to PATH during installation.
    echo [%TIMESTAMP%] Python not found >> "%ERROR_LOG%"
    goto :error_exit
) else (
    for /f "tokens=*" %%i in ('python --version') do echo [SUCCESS] %%i detected
)

:: Check Python packages
echo [CHECK] Verifying required packages...
python -c "import requests, openai, pygame" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some Python packages may be missing. Running setup...
    python -m pip install --upgrade pip
    if exist requirements.txt (
        python -m pip install -r requirements.txt
    )
)

:: Enhanced Ollama Detection and Management
echo.
echo [CHECK] Verifying Ollama service...
curl -s --connect-timeout 3 http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Ollama is not running on port 11434.
    echo [ACTION] Attempting to start Ollama service...
    
    :: Try to start Ollama service
    net start ollama >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ACTION] Starting Ollama with default model qwen2.5...
        start "Ollama Service" /min cmd /c "ollama serve"
        timeout /t 3 >nul
        
        :: Start default model
        start "Ollama Model" /min cmd /c "ollama run qwen2.5:latest"
        timeout /t 5 >nul
    )
    
    :: Verify Ollama is now running
    curl -s --connect-timeout 5 http://localhost:11434/api/tags >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to start Ollama. Please install from https://ollama.ai
        echo [INFO] You can continue without Ollama, but AI features will be limited.
        echo [%TIMESTAMP%] Ollama startup failed >> "%ERROR_LOG%"
        choice /c YN /m "Continue without Ollama"
        if errorlevel 2 goto :error_exit
    ) else (
        echo [SUCCESS] Ollama service is now running
    )
) else (
    echo [SUCCESS] Ollama service detected and responsive
    
    :: Show available models
    echo [INFO] Available Ollama models:
    for /f "tokens=*" %%i in ('ollama list 2^>nul') do echo   %%i
)

:: Environment Variables Setup
echo.
echo [CONFIG] Setting up environment variables...
if exist ultron_config.json (
    echo [SUCCESS] Configuration file found
) else (
    echo [WARNING] ultron_config.json not found, creating from example...
    if exist ultron_config.json.example (
        copy ultron_config.json.example ultron_config.json >nul
    )
)

:: Process Management Check
echo.
echo [CHECK] Checking for existing ULTRON processes...
tasklist /fi "imagename eq python.exe" | find "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Python processes detected. Checking for ULTRON...
    tasklist /fi "windowtitle eq ULTRON*" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [WARNING] ULTRON may already be running.
        choice /c YN /m "Kill existing processes and continue"
        if errorlevel 2 goto :error_exit
        taskkill /f /im "python.exe" /fi "windowtitle eq ULTRON*" >nul 2>&1
    )
)

:: Setup Check
echo.
echo [SETUP] Checking installation status...
if not exist setup.log (
    echo [ACTION] Running first-time setup...
    python setup.py
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Setup failed. Check setup.log for details.
        echo [%TIMESTAMP%] Setup failed >> "%ERROR_LOG%"
        goto :error_exit
    )
    echo [SUCCESS] Setup completed successfully
) else (
    echo [INFO] Setup already completed (setup.log exists)
)

:: Network Check
echo.
echo [CHECK] Testing network connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Internet connectivity confirmed
) else (
    echo [WARNING] No internet connection detected. Some features may be limited.
)

:: GPU Detection
echo.
echo [CHECK] Detecting GPU resources...
wmic path win32_VideoController get name /format:value | find "Name=" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] GPU detection completed
)

:: Main Application Launch
echo.
echo ===============================================
echo  Launching ULTRON Agent 2.0
echo ===============================================

:: Enhanced startup with proper file detection
if exist main.py (
    echo [LAUNCH] Starting ULTRON Agent via main.py...
    echo [%TIMESTAMP%] Launching via main.py >> "%LOG_FILE%"
    python main.py
    set "EXIT_CODE=%ERRORLEVEL%"
) else if exist agent_core.py (
    echo [LAUNCH] Starting ULTRON Agent via agent_core.py...
    echo [%TIMESTAMP%] Launching via agent_core.py >> "%LOG_FILE%"
    python agent_core.py
    set "EXIT_CODE=%ERRORLEVEL%"
) else if exist ultron_agent_2\main.py (
    echo [LAUNCH] Starting ULTRON Agent from ultron_agent_2 folder...
    cd ultron_agent_2
    python main.py
    set "EXIT_CODE=%ERRORLEVEL%"
    cd ..
) else (
    echo [ERROR] Could not find main entry point (main.py or agent_core.py)
    echo [ERROR] Please check your installation.
    echo [%TIMESTAMP%] Entry point not found >> "%ERROR_LOG%"
    goto :error_exit
)

:: Exit handling
echo.
if %EXIT_CODE% EQU 0 (
    echo [SUCCESS] ULTRON Agent exited normally
    echo [%TIMESTAMP%] Normal exit with code %EXIT_CODE% >> "%LOG_FILE%"
) else (
    echo [ERROR] ULTRON Agent exited with error code: %EXIT_CODE%
    echo [%TIMESTAMP%] Error exit with code %EXIT_CODE% >> "%ERROR_LOG%"
    echo [INFO] Check logs for more details:
    echo   - startup.log: General startup information
    echo   - error.log: Error details
    echo   - ultron.log: Application logs
)

:: Optional Git Operations (commented out for safety)
:: echo.
:: echo [GIT] Committing session data...
:: git add . >nul 2>&1
:: git commit -m "ULTRON session %DATE% %TIME%" >nul 2>&1
:: git push >nul 2>&1

goto :normal_exit

:error_exit
echo.
echo [ERROR] ULTRON Agent startup failed!
echo [INFO] Check the following:
echo   1. Python 3.8+ installed and in PATH
echo   2. Required packages installed (run: pip install -r requirements.txt)
echo   3. Ollama installed and running (optional but recommended)
echo   4. Configuration files present
echo.
echo [LOGS] Error details saved to: %ERROR_LOG%
echo [%TIMESTAMP%] Startup failed >> "%ERROR_LOG%"
pause
exit /B 1

:normal_exit
echo.
echo [INFO] ULTRON Agent session ended.
echo [%TIMESTAMP%] Session ended >> "%LOG_FILE%"
echo Press any key to close this window...
pause >nul
endlocal
exit /B 0