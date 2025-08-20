@echo off
setlocal enabledelayedexpansion

echo =====================================
echo   ULTRON Agent Command Center
echo   Quick Deployment Script
echo =====================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Checking PowerShell execution policy...
powershell -Command "Get-ExecutionPolicy" | findstr /i "restricted" >nul
if %errorLevel% equ 0 (
    echo Setting PowerShell execution policy...
    powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
)

echo.
echo Running ULTRON deployment script...
echo.

powershell -ExecutionPolicy Bypass -File "deploy-ultron.ps1"

if %errorLevel% equ 0 (
    echo.
    echo =====================================
    echo   DEPLOYMENT COMPLETED SUCCESSFULLY
    echo =====================================
    echo.
    echo ULTRON Agent Command Center has been installed.
    echo Check your desktop for the shortcut.
    echo.
) else (
    echo.
    echo =====================================
    echo   DEPLOYMENT FAILED
    echo =====================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause