@echo off
REM This script requests Admin privileges and starts LangFlow
REM It will automatically escalate to Admin if not already running as Admin

:: Check if running as admin
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

:: If error flag is set, we do not have admin privileges
if errorlevel 1 (
    echo Requesting Administrator privileges...
    echo.

    :: Get the current directory
    setlocal enabledelayedexpansion
    set "SCRIPT=%~f0"

    :: Create VBScript to request elevation
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\elevate.vbs"
    echo UAC.ShellExecute "cmd.exe", "/k cd /d %cd% && %SCRIPT%", "", "runas", 1 >> "%temp%\elevate.vbs"

    cscript "%temp%\elevate.vbs"
    del "%temp%\elevate.vbs"
    exit /b
)

REM Now we have admin privileges - proceed with startup
echo ✓ Running as Administrator
echo.
echo Starting LangFlow server...
echo.

cd /d C:\Projects\ultron_agent

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Display startup info
echo ========================================
echo LangFlow Server Starting
echo ========================================
echo URL: http://localhost:7860
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start LangFlow with verbose output
python -m langflow run --host 127.0.0.1 --port 7860

REM If LangFlow exits, keep window open to see any errors
echo.
echo LangFlow server stopped.
pause
