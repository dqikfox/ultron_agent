@echo off
title ULTRON Agent 2.0 - Complete Launch System
color 0A

echo.
echo ██    ██ ██   ████████ ██████   ██████  ███    ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ████   ██
echo ██    ██ ██      ██    ██████  ██    ██ ██ ██  ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ██  ██ ██
echo  ██████  ███████ ██    ██   ██  ██████  ██   ████
echo.
echo ═══════════════════════════════════════════════════════════
echo  ULTRON Agent 2.0 - Complete System Launcher
echo  Launching: Frontend + Backend + Agent Core + Web Bridge
echo ═══════════════════════════════════════════════════════════
echo.

REM Kill any existing processes
echo 🔄 Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "agent_core.py" (
    echo ❌ agent_core.py not found!
    pause
    exit /b 1
)

if not exist "web_bridge.py" (
    echo ❌ web_bridge.py not found!
    pause
    exit /b 1
)

if not exist "frontend_server.py" (
    echo ❌ frontend_server.py not found!
    pause
    exit /b 1
)

if not exist "gui\ultron_enhanced\web\index.html" (
    echo ❌ Pokédex GUI not found at gui\ultron_enhanced\web\index.html
    pause
    exit /b 1
)

echo ✅ All components found, starting launch sequence...
echo.

REM Create log directory
if not exist "logs" mkdir logs

REM Launch Frontend Server (localhost:5173) - Pokédex GUI
echo 🎮 [1/4] Starting Frontend Server (Pokédx GUI)...
echo      URL: http://localhost:5173
start "ULTRON Frontend Server" cmd /c "python frontend_server.py > logs\frontend.log 2>&1"
timeout /t 3 >nul

REM Launch Agent Core Server (localhost:8000) - NVIDIA API Backend
echo 🤖 [2/4] Starting Agent Core (NVIDIA Backend)...
echo      URL: http://localhost:8000
start "ULTRON Agent Core" cmd /c "python agent_core.py > logs\agent_core.log 2>&1"
timeout /t 5 >nul

REM Launch Web Bridge (connects GUI to Agent)
echo 🌉 [3/4] Starting Web Bridge (GUI ↔ Agent Connection)...
start "ULTRON Web Bridge" cmd /c "python -c \"import asyncio; from web_bridge import UltronWebBridge; bridge = UltronWebBridge(); asyncio.run(bridge.bridge_connection())\" > logs\web_bridge.log 2>&1"
timeout /t 3 >nul

REM Launch Simple HTTP Server for additional resources (localhost:5000)
echo 🌐 [4/4] Starting Additional HTTP Server (localhost:5000)...
start "ULTRON HTTP Server" cmd /c "cd gui\ultron_enhanced\web && python -m http.server 5000 > ..\..\..\logs\http_server.log 2>&1"
timeout /t 2 >nul

echo.
echo ✅ ULTRON System Launch Complete!
echo.
echo 🔗 AVAILABLE ENDPOINTS:
echo    🎮 Pokédx GUI:     http://localhost:5173  (Main Interface)
echo    🤖 Agent Core:     http://localhost:8000  (NVIDIA Backend)
echo    🌐 HTTP Server:    http://localhost:5000  (Static Files)
echo    🌉 Web Bridge:     Background Service     (Connection Manager)
echo.
echo 📊 MONITORING:
echo    📝 Logs:          .\logs\*.log
echo    ⚡ Agent Status:  http://localhost:8000/health
echo    🖥️  Agent UI:      http://localhost:8000
echo.
echo 🎯 NEXT STEPS:
echo    1. Open Pokédx GUI: http://localhost:5173
echo    2. Test chat functionality in the GUI
echo    3. Monitor logs for any errors
echo.
echo ⚠️  To stop all services: Close all command windows or run stop_ultron.bat
echo.

REM Wait and show status
echo 🔄 Checking service status...
timeout /t 5 >nul

echo.
echo 🚀 ULTRON is now fully operational!
echo 🎮 Main Interface: http://localhost:5173
echo.

REM Open main GUI in default browser
echo 🌐 Opening main interface...
timeout /t 2 >nul
start http://localhost:5173

echo.
echo 📊 System is running. Press any key to open monitoring dashboard...
pause >nul

REM Open monitoring URLs
start http://localhost:8000
start http://localhost:8000/health
start http://localhost:5000

echo.
echo ✨ ULTRON Agent 2.0 is fully operational!
echo.
echo Keep this window open to maintain the system.
echo Close this window to shutdown all services.
echo.
pause
