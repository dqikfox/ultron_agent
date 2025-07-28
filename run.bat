@echo off
setlocal
echo Setting up Ultron Agent 2.0...

:: Detect project root (if run from subfolder)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /B 1
)

:: Check if Ollama is running
curl -s http://localhost:11434 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama is not running.
    echo Attempting to auto-launch Ollama with 'ollama run qwen2.5'...
    start "Ollama" cmd /c "ollama run qwen2.5"
    timeout /t 5 >nul
    curl -s http://localhost:11434 >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Ollama still not running. Please install/start Ollama from https://ollama.ai.
        exit /B 1
    )
)

:: Run setup script (only if not already installed)
if not exist setup.log (
    echo Running setup script...
    python setup.py
    if %ERRORLEVEL% NEQ 0 (
        echo Setup failed. Check setup.log for details.
        exit /B 1
    )
)

:: Run the agent from the correct directory
if exist agent_core.py (
    echo Starting Ultron Agent...
    python agent_core.py
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to start Ultron Agent. Check logs/ultron.log for details.
        exit /B 1
    )
) else if exist ultron_agent_2\agent_core.py (
    echo Starting Ultron Agent from ultron_agent_2 folder...
    cd ultron_agent_2
    python agent_core.py
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to start Ultron Agent. Check logs/ultron.log for details.
        exit /B 1
    )
    cd ..
) else (
    echo Could not find agent_core.py. Please check your installation.
    exit /B 1
)

echo.
echo Ultron Agent exited. Press any key to close this window.
pause >nul
endlocal