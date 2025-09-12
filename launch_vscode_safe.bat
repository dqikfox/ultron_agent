@echo off
REM VS Code Safe Launch Script for ULTRON Agent
REM This script prevents VS Code crashes by optimizing system resources

echo.
echo ████████████████████████████████████████████████████████████████
echo  ULTRON Agent - VS Code Safe Launch System
echo ████████████████████████████████████████████████████████████████
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo [INFO] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

echo [INFO] Checking required modules...
python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo [WARN] psutil not found - installing...
    pip install psutil
    if errorlevel 1 (
        echo [ERROR] Failed to install psutil
        pause
        exit /b 1
    )
)

echo [INFO] Starting crash prevention system...
python vscode_crash_prevention.py --launch-vscode

if errorlevel 1 (
    echo [ERROR] Failed to start VS Code safely
    echo.
    echo Possible solutions:
    echo 1. Close other resource-intensive applications
    echo 2. Restart your computer
    echo 3. Check if VS Code is already running
    echo 4. Run as administrator
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] VS Code launched with crash prevention active
echo.
echo The crash prevention system is now monitoring your system resources.
echo If VS Code becomes unstable, the system will automatically:
echo  - Reduce CPU usage by pausing background processes
echo  - Free up memory by running garbage collection
echo  - Prevent system overload with circuit breaker protection
echo.
echo To stop monitoring, close this window or press Ctrl+C
echo.

REM Keep monitoring running
python vscode_crash_prevention.py