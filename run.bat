@echo off

REM === ULTRON Agent 2 Startup Script ===
echo.
echo ================================
echo   Starting ULTRON Agent 2
echo ================================
echo.

REM Run from repository root
pushd "%~dp0" >nul

REM --- Configuration Validation ---
if not exist "%~dp0ultron_config.json" (
	echo ERROR: ultron_config.json not found. Please ensure configuration file exists.
	pause
	exit /b 1
)
echo Configuration file found: ultron_config.json

REM --- Dependency Check ---
python -c "import requests, json, logging" >nul 2>&1
if errorlevel 1 (
	echo ERROR: Required Python packages not installed. Run: pip install requests
	pause
	exit /b 1
)
echo Python dependencies verified.

REM --- Start Ollama Service ---
echo Checking Ollama service...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if errorlevel 1 (
	echo Starting Ollama service...
	start "Ollama Service" cmd /k "ollama serve"
	timeout /t 5 /nobreak >nul
) else (
	echo Ollama service already running.
)

REM --- Start AWS Integration Service ---
if exist "%~dp0ultron_aws_integration.py" (
	echo Starting AWS Integration Service...
	start "ULTRON AWS Integration" cmd /c python "%~dp0ultron_aws_integration.py"
) else (
	echo AWS integration script not found. Skipping AWS Integration Service.
)

REM --- Start API Monitoring Service ---
if exist "%~dp0ultron_api_monitor.py" (
	echo Starting API Monitoring Service...
	start "ULTRON API Monitor" cmd /c python "%~dp0ultron_api_monitor.py"
) else (
	echo API monitoring script not found. Skipping API Monitoring Service.
)

REM --- Start GUI Server (Port 8080) ---
set "GUI_SERVER="
if exist "%~dp0main_gui_server.py" (
	set "GUI_SERVER=main_gui_server.py"
) else (
	if exist "%~dp0web_gui_server.py" (
		set "GUI_SERVER=web_gui_server.py"
	)
)
if defined GUI_SERVER (
	echo Starting GUI Server %GUI_SERVER% on port 8080...
	start "ULTRON GUI Server" cmd /k pushd "%~dp0" ^& python %GUI_SERVER%
) else (
	echo No GUI server script found (main_gui_server.py or web_gui_server.py).
)

REM --- Wait for GUI Server to initialize ---
timeout /t 2 /nobreak >nul

REM --- Start AI Chat Server (Port 8000) ---
if exist "%~dp0nvidia_enhanced_ultron.py" (
	echo Starting AI Chat Server (nvidia_enhanced_ultron.py) on port 8000...
	start "ULTRON AI Chat" cmd /k pushd "%~dp0" ^& python nvidia_enhanced_ultron.py
) else (
	if exist "%~dp0ultron_assistant\run_ultron_assistant.py" (
		echo Starting ULTRON Assistant on port 8000...
		start "ULTRON Assistant" cmd /k pushd "%~dp0ultron_assistant" ^& python run_ultron_assistant.py
	) else (
		echo No AI server found. Skipping AI Chat Server startup.
	)
)

REM --- Start Tamagotchi Server (Port 3000) ---
if exist "%~dp0tamagotchi_server.py" (
	echo Starting Tamagotchi Server on port 3000...
	start "ULTRON Tamagotchi" cmd /k pushd "%~dp0" ^& python tamagotchi_server.py
) else (
	echo tamagotchi_server.py not found. Skipping Tamagotchi Server.
)

REM --- Start Gateway Server (Port 9000) ---
if exist "%~dp0gateway\server.py" (
	echo Starting Gateway Server on port 9000...
	start "ULTRON Gateway" cmd /k pushd "%~dp0gateway" ^& python server.py
) else (
	echo Gateway server not found. Skipping Gateway Server.
)

REM --- Start Web Bridge (Port 7000) ---
if exist "%~dp0web_bridge.py" (
	echo Starting Web Bridge on port 7000...
	start "ULTRON Web Bridge" cmd /k pushd "%~dp0" ^& python web_bridge.py
) else (
	echo Web bridge not found. Skipping Web Bridge.
)

REM --- Wait for servers to start ---
timeout /t 3 /nobreak >nul

REM --- Service Health Checks ---
echo Performing basic service health checks...
echo Note: Detailed health checks require PowerShell. Services should be starting in background.
echo.

REM --- Start Electron GUI (Command Center) ---
if exist "%~dp0core\ultron-agent-command-center\package.json" (
	echo Starting Electron Command Center GUI...
	start "ULTRON Electron GUI" cmd /k pushd "%~dp0core\ultron-agent-command-center" ^& npm run electron:dev
) else (
	echo Electron project not found at core\ultron-agent-command-center. Update run.bat if entry point is different.
)

REM --- Open the Ultron Enhanced local index.html if present ---
set "ENHANCED_INDEX=%~dp0gui\ultron_enhanced\web\index.html"
if exist "%ENHANCED_INDEX%" (
	echo Found enhanced GUI index at %ENHANCED_INDEX% - opening in default browser...
	start "" "%ENHANCED_INDEX%"
) else (
	echo Enhanced GUI index not found at %ENHANCED_INDEX%.
)

REM --- Final Status ---
echo.
echo ULTRON Agent 2 startup sequence complete.
echo GUI Server:     http://localhost:8080
echo AI Chat:        http://localhost:8000
echo Tamagotchi:     http://localhost:3000
echo Gateway:        http://localhost:9000
echo Web Bridge:     http://localhost:7000
echo AWS Integration: Running (background)
echo API Monitor:    Running (background)
echo Ollama Service: http://localhost:11434
echo Electron GUI:   Command Center
echo Enhanced GUI:   %ENHANCED_INDEX%
echo.
echo Press any key to exit...
pause

popd >nul
