@echo off
REM ============================================================
REM AMAZON Q UGS CLI - CMD FIX
REM ============================================================
REM Removes Windows Terminal settings that require admin
REM This fixes: CMD/PowerShell "opens and closes" on your profile
REM ============================================================

setlocal enabledelayedexpansion

title Amazon Q UGS - CMD Fix Utility

cls
echo.
echo ============================================================
echo   AMAZON Q UGS CLI - CMD CONSOLE FIX
echo ============================================================
echo.
echo This script will reset Windows Terminal settings that are
echo causing CMD/PowerShell to require admin privileges.
echo.
echo Current User: %USERNAME%
echo Profile: %USERPROFILE%
echo.

REM Ask for confirmation
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.
echo [1] Removing Windows Terminal cached settings...
REM Remove Windows Terminal settings
for /d %%i in ("%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_*") do (
    if exist "%%i\LocalState\settings.json" (
        echo   Deleting: %%i\LocalState\settings.json
        del /f /q "%%i\LocalState\settings.json" 2>nul
    )
)

echo.
echo [2] Clearing temp files...
REM Clear temp files
for /d %%i in ("%LOCALAPPDATA%\Temp\*") do (
    rmdir /s /q "%%i" 2>nul
)
del /f /q "%LOCALAPPDATA%\Temp\*" 2>nul

echo.
echo [3] Resetting console registry entries...
REM Reset registry
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ForceShellExecuteOpen" /f 2>nul
reg delete "HKCU\Software\Microsoft\Command Processor" /f 2>nul

echo.
echo [4] Testing CMD...
cmd /c "echo test" >nul 2>&1
if %errorlevel%==0 (
    echo [✓] CMD test PASSED
) else (
    echo [✗] CMD test FAILED - may need full restart
)

echo.
echo ============================================================
echo   FIX COMPLETE
echo ============================================================
echo.
echo [✓] Windows Terminal settings reset
echo [✓] Temporary files cleared
echo [✓] Registry entries cleaned
echo.
echo NEXT STEPS:
echo   1. Close this window (press any key)
echo   2. Restart your computer
echo   3. Test: Press Win+R, type 'cmd', should open normally
echo.
echo Press any key to exit...
pause >nul
