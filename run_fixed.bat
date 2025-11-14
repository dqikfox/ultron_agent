@echo off
setlocal enabledelayedexpansion

title ULTRON Agent 3.0 - Launcher

set "PYTHON_CMD=python"
set "OLLAMA_CMD=%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe"
set "LOG_FILE=ultron_startup.log"
set "OLLAMA_PORT=11434"
set "WEB_GUI_PORT=8080"
set "API_SERVER_PORT=5000"
set "SSH_SERVER_PORT=2222"
set "OLLAMA_MODEL=llava:7b"
set "ENABLE_DIRECT_BRIDGE=1"
set "ENABLE_SSH_SERVER=1"
set "BRIDGE_SCRIPT=copilot_amazon_q_bridge.py"

echo. > "%LOG_FILE%"
echo [%date% %time%] ULTRON Agent Startup >> "%LOG_FILE%"

cls
echo.
echo ==============================================================
echo              ULTRON AGENT 3.0 - LAUNCHER
echo ==============================================================
echo.

echo [1/7] Cleanup...
powershell -Command "Get-Process python,ollama -EA SilentlyContinue | Stop-Process -Force" >nul 2>&1
timeout /t 1 /nobreak >nul
echo       Done
echo.

echo [2/7] Preflight checks...
if not exist "web_gui_server.py" (echo       web_gui_server.py missing & pause & exit /b 1)
if not exist "main.py" (echo       main.py missing & pause & exit /b 1)
echo       Files present
echo.

echo [3/7] Python...
where %PYTHON_CMD% >nul 2>&1 || (echo       Python not in PATH & pause & exit /b 1)
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo       Python %PYTHON_VERSION%
echo.

echo [4/7] Ollama...
curl -s -m 1 http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1 && (echo       Running & goto ollama_ready)
if not exist "%OLLAMA_CMD%" (echo       Not installed & pause & exit /b 1)
start "Ollama" /MIN "%OLLAMA_CMD%" serve
set "retry=0"
:ollama_wait
curl -s -m 1 http://localhost:%OLLAMA_PORT%/api/tags >nul 2>&1 && goto ollama_ready
set /a retry+=1
if !retry! lss 8 (timeout /t 1 /nobreak >nul & goto ollama_wait)
:ollama_ready
echo       Ready
echo.

echo [5/7] Model...
"%OLLAMA_CMD%" list 2>nul | findstr "%OLLAMA_MODEL%" >nul && (echo       %OLLAMA_MODEL% & goto model_ready)
echo       Model missing
:model_ready
echo.

echo [6/7] Services...
start "ULTRON-WebGUI" /MIN python web_gui_server.py
timeout /t 1 /nobreak >nul
start "ULTRON-API" /MIN python api_server.py 2>nul
start "ULTRON-AvatarGame" /MIN python avatar_game_server.py 2>nul
start "ULTRON-ADB" /MIN python adb_backend_enhanced.py 2>nul
if "%ENABLE_SSH_SERVER%"=="1" (
    if exist "ssh_server.py" (
        %PYTHON_CMD% -c "import paramiko" >nul 2>&1
        if errorlevel 1 (
            echo       SSH dependency missing - installing paramiko
            pip install paramiko
        )
        start "ULTRON-SSH" /MIN %PYTHON_CMD% ssh_server.py
        echo       SSH Server port %SSH_SERVER_PORT%
    ) else (
        echo       SSH server missing ssh_server.py
    )
)
if exist "addons\gdrive_ultron\server.js" (
    start "ULTRON-GDrive" /MIN cmd /c "cd addons\gdrive_ultron && npm start"
    echo       GDrive addon
)
echo       Web GUI + API + Avatar Game + ADB
if "%ENABLE_DIRECT_BRIDGE%"=="1" (
    if exist "%BRIDGE_SCRIPT%" (
        %PYTHON_CMD% -c "import aiohttp" >nul 2>&1
        if errorlevel 1 (
            echo       Bridge dependency missing aiohttp
        ) else (
            start "ULTRON-Bridge" /MIN %PYTHON_CMD% "%BRIDGE_SCRIPT%" --listen
            echo       Copilot to Amazon Q Bridge
        )
    ) else (
        echo       Bridge script missing %BRIDGE_SCRIPT%
    )
)
echo.

echo [7/7] Health check...
timeout /t 3 /nobreak >nul
curl -s -m 1 http://localhost:%WEB_GUI_PORT%/ >nul 2>&1 && echo       Web GUI healthy || echo       Initializing
if "%ENABLE_SSH_SERVER%"=="1" (
    powershell -Command "try { $tcp = New-Object System.Net.Sockets.TcpClient; $tcp.Connect('localhost', %SSH_SERVER_PORT%); $tcp.Close(); Write-Host '       SSH Server healthy' } catch { Write-Host '       SSH Server initializing' }" 2>nul
)
echo.

echo ==============================================================
echo           ULTRON AGENT 3.0 - READY
echo ==============================================================
echo.
echo  WEB GUI:    http://localhost:%WEB_GUI_PORT%/
echo  AVATAR:     http://localhost:8082/
echo  ADB:        http://localhost:5003/
echo  API:        http://localhost:%API_SERVER_PORT%/
echo  OLLAMA:     http://localhost:%OLLAMA_PORT%/
if "%ENABLE_SSH_SERVER%"=="1" echo  SSH:        ssh -p %SSH_SERVER_PORT% user@localhost
echo.
echo  LOGS:       %LOG_FILE%
echo  Ctrl+C to stop
echo.

echo Launching browser...
for %%b in (chrome.exe msedge.exe firefox.exe) do (
    where %%b >nul 2>&1 && (start %%b "http://localhost:%WEB_GUI_PORT%/" & goto done)
)
start "" "http://localhost:%WEB_GUI_PORT%/"
:done

pause
powershell -Command "Get-Process python,ollama -EA SilentlyContinue | Stop-Process -Force" 2>nul
echo Stopped
exit /b 0
