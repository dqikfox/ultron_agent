@echo off

REM === ULTRON Agent 2 Startup Script ===
echo.
echo ================================
echo   Starting ULTRON Agent 2
echo ================================
echo.

REM Run from repository root
pushd "%~dp0" >nul

REM --- Start GUI Server (Port 5000) ---
set "GUI_SERVER="
if exist "%~dp0main_gui_server.py" (
	set "GUI_SERVER=main_gui_server.py"
) else (
	if exist "%~dp0web_gui_server.py" (
		set "GUI_SERVER=web_gui_server.py"
	)
)
if defined GUI_SERVER (
	echo Starting GUI Server %GUI_SERVER% on port 5000...
	start "ULTRON GUI Server" cmd /k "pushd "%~dp0" && python "%GUI_SERVER%" && popd"
) else (
	echo No GUI server script found (main_gui_server.py or web_gui_server.py).
)

REM --- Wait for GUI Server to initialize ---
timeout /t 2 /nobreak >nul

REM --- Start AI Chat Server (Port 8000) ---
if exist "%~dp0nvidia_enhanced_ultron.py" (
	echo Starting AI Chat Server (nvidia_enhanced_ultron.py) on port 8000...
	start "ULTRON AI Chat" cmd /k "pushd "%~dp0" && python "nvidia_enhanced_ultron.py" && popd"
) else (
	if exist "%~dp0ultron_assistant\run_ultron_assistant.py" (
		echo Starting ULTRON Assistant on port 8000...
		start "ULTRON Assistant" cmd /k "pushd "%~dp0ultron_assistant" && python "run_ultron_assistant.py" && popd"
	) else (
		echo No AI server found. Skipping AI Chat Server startup.
	)
)

REM --- Start Tamagotchi Server (Port 3000) ---
if exist "%~dp0tamagotchi_server.py" (
	echo Starting Tamagotchi Server on port 3000...
	start "ULTRON Tamagotchi" cmd /k "pushd "%~dp0" && python "tamagotchi_server.py" && popd"
) else (
	echo tamagotchi_server.py not found. Skipping Tamagotchi Server.
)

REM --- Start Gateway Server (Port 9000) ---
if exist "%~dp0gateway\server.py" (
	echo Starting Gateway Server on port 9000...
	start "ULTRON Gateway" cmd /k "pushd "%~dp0gateway" && python "server.py" && popd"
) else (
	echo Gateway server not found. Skipping Gateway Server.
)

REM --- Start Web Bridge (Port 7000) ---
if exist "%~dp0web_bridge.py" (
	echo Starting Web Bridge on port 7000...
	start "ULTRON Web Bridge" cmd /k "pushd "%~dp0" && python "web_bridge.py" && popd"
) else (
	echo Web bridge not found. Skipping Web Bridge.
)

REM --- Wait for servers to start ---
timeout /t 3 /nobreak >nul

REM --- Start Electron GUI (Command Center) ---
if exist "%~dp0core\ultron-agent-command-center\package.json" (
	echo Starting Electron Command Center GUI...
	start "ULTRON Electron GUI" cmd /k "pushd "%~dp0core\ultron-agent-command-center" && npm run electron:dev && popd"
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
echo GUI Server:     http://localhost:5000
echo AI Chat:        http://localhost:8000
echo Tamagotchi:     http://localhost:3000
echo Gateway:        http://localhost:9000
echo Web Bridge:     http://localhost:7000
echo Electron GUI:   Command Center
echo Enhanced GUI:   %ENHANCED_INDEX%
echo.
echo Press any key to exit...
pause

popd >nul
