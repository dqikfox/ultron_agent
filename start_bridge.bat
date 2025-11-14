@echo off
REM Start Copilot ↔ Amazon Q Direct Bridge (NO ADMIN REQUIRED)
REM This enables automatic workflow routing without copy-paste

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================
echo COPILOT ^arrow AMAZON Q DIRECT BRIDGE
echo ============================================
echo.

if "%1"=="--demo" (
    echo [*] Starting in DEMO mode...
    echo [*] This will submit sample workflows
    echo.
    python copilot_amazon_q_bridge.py --demo
    pause
    exit /b 0
)

if "%1"=="--help" (
    echo Usage: start_bridge.bat [--demo^|--listen]
    echo.
    echo Options:
    echo   --demo    Test mode with sample workflows
    echo   --listen  Production mode (default)
    echo   --help    Show this help message
    pause
    exit /b 0
)

echo [+] Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [+] Checking aiohttp module...
python -c "import aiohttp" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing aiohttp...
    pip install aiohttp
)

echo [+] Verifying bridge script...
if not exist "copilot_amazon_q_bridge.py" (
    echo [ERROR] Bridge script not found!
    pause
    exit /b 1
)

echo.
echo [✓] All checks passed. Starting bridge in PRODUCTION mode...
echo [*] Bridge will route workflows to Amazon Q automatically
echo [*] Press Ctrl+C to stop
echo.

python copilot_amazon_q_bridge.py --listen

echo.
echo [!] Bridge stopped
pause
