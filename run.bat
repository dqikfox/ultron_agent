@echo off
echo Setting up Ultron Agent 2.0...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /B 1
)

:: Check if Ollama is running
curl -s http://localhost:11434 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama is not running. Please start Ollama with 'ollama run llama3.2:latest' (install from https://ollama.ai).
    exit /B 1
)

:: Run setup script
echo Running setup script...
python setup.py
if %ERRORLEVEL% NEQ 0 (
    echo Setup failed. Check setup.log for details.
    exit /B 1
)

:: Run the agent
echo Starting Ultron Agent...
cd ultron_agent_2
python agent_core.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start Ultron Agent. Check logs/ultron.log for details.
    exit /B 1
)

PAUSE