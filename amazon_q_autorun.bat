@echo off
echo [AMAZON Q] Auto-Run for ULTRON Agent
echo =====================================

cd /d "%~dp0"

echo Starting Amazon Q auto-run commands...
python test_amazon_q.py

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Auto-run completed successfully!
) else (
    echo [ERROR] Auto-run failed with error code %ERRORLEVEL%
)

echo.
echo Press any key to continue...
pause >nul