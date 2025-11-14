@echo off
echo ========================================
echo EXECUTING ALL 3 PATHS SIMULTANEOUSLY
echo ========================================
echo.

REM Path 1: Unity Game
echo [PATH 1] Opening Unity Assets...
start explorer "%~dp0UnityGame\Assets"
timeout /t 2 /nobreak > nul

REM Path 2: Azure Deployment
echo [PATH 2] Preparing Azure Deployment...
echo.
echo Azure CLI Commands:
echo   az login
echo   bash deploy_azure.sh
echo   bash deploy_logic_apps.sh
echo   bash deploy_automation.sh
echo.

REM Path 3: SSH Server
echo [PATH 3] Starting SSH Server...
start /B python ssh_server.py
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo ALL PATHS INITIATED
echo ========================================
echo.
echo [PATH 1] Unity Assets: OPEN
echo [PATH 2] Azure Commands: READY
echo [PATH 3] SSH Server: RUNNING on port 2222
echo.
echo NEXT ACTIONS:
echo.
echo [Unity] Import files from opened folder to Unity project
echo [Azure] Run: az login (then deployment scripts)
echo [SSH]   Test from Termux: ssh -p 2222 anyuser@192.168.1.104
echo.
pause
