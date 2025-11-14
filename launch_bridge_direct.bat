@echo off
REM Bridge Launcher - No Admin, No Restrictions
REM This batch file can be executed directly without CMD shell

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ==================================================
echo  COPILOT ^arrow AMAZON Q DIRECT BRIDGE
echo ==================================================
echo.

echo [+] Python: %~dp0.venv\Scripts\python.exe
echo [+] Script: %~dp0copilot_amazon_q_bridge.py
echo.
echo [^!] Starting bridge in PRODUCTION mode...
echo [*] Press Ctrl+C to stop
echo.

%~dp0.venv\Scripts\python.exe "%~dp0copilot_amazon_q_bridge.py" --listen

echo.
pause
