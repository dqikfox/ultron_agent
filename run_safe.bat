@echo off
chcp 65001 > nul
title ULTRON Agent 3.0 - SAFE LAUNCHER
color 0A

echo.
echo ██    ██ ██   ████████ ██████   ██████  ███    ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ████   ██
echo ██    ██ ██      ██    ██████  ██    ██ ██ ██  ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ██  ██ ██
echo  ██████  ███████ ██    ██   ██  ██████  ██   ████
echo.
echo ═══════════════════════════════════════════════════════════
echo  ULTRON Agent 3.0 - SAFE LAUNCHER (Terminal Multiplication Fixed)
echo ═══════════════════════════════════════════════════════════
echo.

:: Step 1: Clean up existing ULTRON processes ONLY
echo 🔄 Cleaning up existing ULTRON processes...

:: Kill only processes that contain ULTRON or are from our specific scripts
for /f "tokens=2" %%i in ('tasklist /FI "WINDOWTITLE eq ULTRON*" /FO CSV ^| find /V "PID"') do (
    if not "%%i"=="" taskkill /F /PID %%i >nul 2>&1
)

:: Kill processes running our specific Python scripts
wmic process where "commandline like '%%nvidia_enhanced_ultron.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%main_gui_server.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%frontend_server.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%gui_api_server.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%agent_core.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%web_bridge.py%%'" delete >nul 2>&1

timeout /t 2 >nul

:: Step 2: Check prerequisites
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

:: Step 3: Create logs directory
if not exist "logs" mkdir logs

:: Step 4: Launch services with CONTROLLED terminals (using /c instead of /k)
echo.
echo 🚀 Starting ULTRON services with controlled terminals...
echo.

:: Service 1: Main GUI Server (Port 5000)
echo 🏠 [1/5] Starting Main GUI Server (Port 5000)...
if exist "main_gui_server.py" (
    start "ULTRON-GUI-5000" /MIN cmd /c "python main_gui_server.py > logs\main_gui.log 2>&1"
    timeout /t 2 >nul
) else (
    echo ❌ main_gui_server.py not found!
)

:: Service 2: Frontend Server (Port 5173)
echo 💬 [2/5] Starting Frontend Server (Port 5173)...
if exist "frontend_server.py" (
    start "ULTRON-FRONTEND-5173" /MIN cmd /c "python frontend_server.py > logs\frontend.log 2>&1"
    timeout /t 2 >nul
) else (
    echo ❌ frontend_server.py not found!
)

:: Service 3: GUI API Server (Port 3000)
echo 🔌 [3/5] Starting GUI API Server (Port 3000)...
if exist "gui_api_server.py" (
    start "ULTRON-API-3000" /MIN cmd /c "python gui_api_server.py > logs\gui_api.log 2>&1"
    timeout /t 2 >nul
) else (
    echo ❌ gui_api_server.py not found!
)

:: Service 4: Agent Core (Port 8000)
echo 🤖 [4/5] Starting Agent Core (Port 8000)...
if exist "agent_core.py" (
    start "ULTRON-CORE-8000" /MIN cmd /c "python agent_core.py > logs\agent_core.log 2>&1"
    timeout /t 3 >nul
) else if exist "nvidia_enhanced_ultron.py" (
    start "ULTRON-NVIDIA-8000" /MIN cmd /c "python nvidia_enhanced_ultron.py > logs\nvidia_core.log 2>&1"
    timeout /t 3 >nul
) else (
    echo ❌ No core server found!
)

:: Service 5: Web Bridge
echo 🌉 [5/5] Starting Web Bridge...
if exist "web_bridge.py" (
    start "ULTRON-BRIDGE" /MIN cmd /c "python web_bridge.py > logs\web_bridge.log 2>&1"
    timeout /t 2 >nul
) else (
    echo ℹ️ web_bridge.py not found (optional service)
)

:: Step 5: Verify services are running
echo.
echo 🔍 VERIFYING SERVICES:
timeout /t 5 >nul

:: Check each port
echo 🏠 Port 5000: Main GUI Server
netstat -an | find ":5000 " >nul && echo ✅ RUNNING || echo ❌ NOT RESPONDING

echo 💬 Port 5173: Frontend Server
netstat -an | find ":5173 " >nul && echo ✅ RUNNING || echo ❌ NOT RESPONDING

echo 🔌 Port 3000: GUI API Server
netstat -an | find ":3000 " >nul && echo ✅ RUNNING || echo ❌ NOT RESPONDING

echo 🤖 Port 8000: Agent Core
netstat -an | find ":8000 " >nul && echo ✅ RUNNING || echo ❌ NOT RESPONDING

echo.
echo 🚀 ULTRON SYSTEM STATUS:
echo ═══════════════════════════════════════════════════════════
echo 🌐 Main Interface:  http://localhost:5000  (Pokédx GUI)
echo 💬 Chat Engine:     http://localhost:5173  (NVIDIA AI Chat)
echo 🔌 API Endpoints:   http://localhost:3000  (Backend API)
echo 🤖 AI Core:         http://localhost:8000  (Processing Engine)
echo ═══════════════════════════════════════════════════════════
echo 📊 System Logs:     .\logs\*.log
echo 🔧 Debug Mode:      Use run_debug.bat for enhanced monitoring
echo.

:: Open main interface
echo 🌐 Opening main interface...
start http://localhost:5000

echo.
echo ✅ ULTRON is operational!
echo 💡 This launcher prevents terminal multiplication.
echo 📝 Check logs in .\logs\ for any issues.
echo.
echo Press any key to exit launcher (services will continue)...
pause >nul
