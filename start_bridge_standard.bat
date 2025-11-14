@echo off
REM Start Copilot ↔ Amazon Q Direct Bridge (NO ADMIN REQUIRED)
REM This launches without any admin privilege requirements

cd /d "%~dp0"

color 0A
title Bridge - Copilot to Amazon Q Router

echo.
echo ============================================
echo  COPILOT ↔ AMAZON Q DIRECT BRIDGE
echo ============================================
echo.

if "%1"=="--demo" (
    echo [*] Starting in DEMO mode...
    echo [*] This will submit sample workflows
    echo.
    python copilot_amazon_q_bridge.py --demo
    goto end
)

if "%1"=="--help" (
    echo Usage: start_bridge_standard.bat [--demo^|--listen]
    echo.
    echo Options:
    echo   --demo    Test mode with sample workflows
    echo   --listen  Production mode (default)
    echo   --help    Show this help message
    echo.
    goto end
)

echo [+] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    goto end
)

echo [+] Checking aiohttp...
python -c "import aiohttp" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing aiohttp...
    pip install aiohttp
)

echo.
echo [✓] Starting bridge in PRODUCTION mode...
echo [*] Press Ctrl+C to stop
echo.

python copilot_amazon_q_bridge.py --listen

:end
echo.
pause
exit /b 0
