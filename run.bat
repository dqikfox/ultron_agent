@echo off

REM === ULTRON Agent 2 Startup Script ===
echo.
echo ================================
echo   Starting ULTRON Agent 2
echo ================================
echo.

REM Run from repository root
cd /d "%~dp0" >nul

REM --- Configuration Validation ---
if not exist "%~dp0ultron_config.json" (
	echo ERROR: ultron_config.json not found. Please ensure configuration file exists.
	pause
	exit /b 1
)
echo Configuration file found: ultron_config.json

REM --- Enhanced Dependency Check ---
python -c "import fastapi, uvicorn, websockets" >nul 2>&1
if errorlevel 1 (
	echo Installing missing dependencies...
	pip install -r requirements.txt --quiet
	if errorlevel 1 (
		echo ERROR: Failed to install dependencies
		pause
		exit /b 1
	)
)
echo Dependencies verified.

REM --- Start Ollama Service ---
echo Checking Ollama service...
where ollama >nul 2>&1
if errorlevel 1 (
	echo Ollama not found in PATH. Please install Ollama.
) else (
	echo Ollama is available.
	tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I "ollama.exe" >NUL
	if errorlevel 1 (
		echo Starting Ollama service...
		start "" ollama serve >nul 2>&1
		timeout /t 3 >nul
	)
)

REM --- Start GUI Server (Port 5000) ---
if exist "%~dp0main_gui_server_fixed.py" goto :start_fixed_gui
if exist "%~dp0main_gui_server.py" goto :start_legacy_gui
echo GUI server script not found. Skipping GUI Server startup.
goto :skip_gui

:start_fixed_gui
echo Starting GUI Server on port 5000 (with auto-fallback)...
start "ULTRON GUI Server" cmd /k cd /d "%~dp0" ^&^& python main_gui_server_fixed.py
goto :skip_gui

:start_legacy_gui
echo Starting GUI Server on port 5000 (legacy version)...
start "ULTRON GUI Server" cmd /k cd /d "%~dp0" ^&^& python main_gui_server.py
goto :skip_gui

:skip_gui

REM --- Environment Variables Check ---
echo Checking environment variables...
if "%OPENAI_API_KEY%"=="" (
	echo WARNING: OPENAI_API_KEY not set in environment variables
) else (
	echo OPENAI_API_KEY: %OPENAI_API_KEY:~0,8%...
)
if "%ELEVENLABS_API_KEY%"=="" (
	echo WARNING: ELEVENLABS_API_KEY not set in environment variables
) else (
	echo ELEVENLABS_API_KEY: %ELEVENLABS_API_KEY:~0,8%...
)

REM --- Start Production Voice Assistant ---
if exist "%~dp0ultron_production.py" (
	echo Starting ULTRON Production Voice Assistant...
	start "ULTRON Voice" cmd /k cd /d "%~dp0" ^&^& python ultron_production.py
)

REM --- Start Core Agent ---
if exist "%~dp0main.py" (
	echo Starting ULTRON Core Agent...
	start "ULTRON Agent" cmd /k cd /d "%~dp0" ^&^& python main.py
)

REM --- Service Verification ---
echo Verifying services...
timeout /t 2 >nul
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5000' -TimeoutSec 3 -UseBasicParsing | Out-Null; Write-Host 'GUI Server: ONLINE' } catch { Write-Host 'GUI Server: OFFLINE' }" 2>nul

echo.
echo ULTRON Agent 2 startup sequence complete.
echo GUI Server:     http://localhost:5000
echo AI Chat:        http://localhost:8000
echo Ollama Service: http://localhost:11434
echo.
echo Press any key to exit...
pause
