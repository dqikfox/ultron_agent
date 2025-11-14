@echo off
REM Start Unity Integration Server for ULTRON Agent
REM Port: 9000

echo ================================================
echo  ULTRON Agent - Unity Integration Server
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.10+ and add to PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [WARNING] Virtual environment not found
    echo Using system Python
    set PYTHON_CMD=python
) else (
    echo [+] Using virtual environment
    set PYTHON_CMD=.venv\Scripts\python.exe
)

REM Check if unity_integration.py exists
if not exist "unity_integration.py" (
    echo [ERROR] unity_integration.py not found
    echo Please ensure you're in the ultron_agent directory
    pause
    exit /b 1
)

echo.
echo [+] Starting Unity Integration Server...
echo [+] Port: 9000
echo [+] CORS: Enabled (WebGL support)
echo [+] Press Ctrl+C to stop
echo.

REM Start the server
%PYTHON_CMD% unity_integration.py

pause
