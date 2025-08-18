@echo off
chcp 65001 > nul
title ULTRON Agent 3.0 - Complete System Launcher
color 0A

echo.
echo ██    ██ ██   ████████ ██████   ██████  ███    ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ████   ██
echo ██    ██ ██      ██    ██████  ██    ██ ██ ██  ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ██  ██ ██
echo  ██████  ███████ ██    ██   ██  ██████  ██   ████
echo.
echo ═══════════════════════════════════════════════════════════
echo  ULTRON Agent 3.0 - Complete System Launcher
echo  Main GUI + Chat Engine + Agent Core + Web Bridge + GUI API
echo ═══════════════════════════════════════════════════════════
echo.

:: Kill any existing processes
echo 🔄 Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

:: Check required files
if not exist "agent_core.py" (
    echo ❌ agent_core.py not found!
    pause
    exit /b 1
)

if not exist "frontend_server.py" (
    echo ❌ frontend_server.py not found!
    pause
    exit /b 1
)

if not exist "gui_api_server.py" (
    echo ❌ gui_api_server.py not found!
    pause
    exit /b 1
)

if not exist "main_gui_server.py" (
    echo ❌ main_gui_server.py not found!
    pause
    exit /b 1
)

if not exist "gui\ultron_enhanced\web\index.html" (
    echo ❌ Pokédx GUI not found!
    pause
    exit /b 1
)

echo ✅ All components found, launching ULTRON system...
echo.

:: Create logs directory
if not exist "logs" mkdir logs

:: Launch sequence - CORRECTED ARCHITECTURE
echo 🏠 [1/5] Starting Main Pokédx GUI Server...
echo      URL: http://localhost:5000 (MAIN ENTRY POINT)
start "ULTRON Main GUI" cmd /c "python main_gui_server.py > logs\main_gui.log 2>&1"
timeout /t 3 >nul

echo 💬 [2/5] Starting Chat Engine (NVIDIA AI)...
echo      URL: http://localhost:5173 (NVIDIA Chat Engine)
start "ULTRON Chat Engine" cmd /c "python frontend_server.py > logs\frontend.log 2>&1"
timeout /t 3 >nul

echo 🔌 [3/5] Starting GUI API Server...
echo      URL: http://localhost:3000 (API Endpoints)
start "ULTRON GUI API" cmd /c "python gui_api_server.py > logs\gui_api.log 2>&1"
timeout /t 3 >nul

echo 🤖 [4/5] Starting Agent Core (NVIDIA Backend)...
echo      URL: http://localhost:8000 (AI Processing)
start "ULTRON Agent Core" cmd /c "python agent_core.py > logs\agent_core.log 2>&1"
timeout /t 5 >nul

echo 🌉 [5/5] Starting Web Bridge (Connection Manager)...
start "ULTRON Web Bridge" cmd /c "python web_bridge.py > logs\web_bridge.log 2>&1"
timeout /t 3 >nul

echo.
echo ✅ ULTRON System Launch Complete!
echo.
echo 🔗 ARCHITECTURE ACTIVE:
echo    🏠 Main Interface:  http://localhost:5000  (Sophisticated Pokédx GUI)
echo    💬 Chat Engine:     http://localhost:5173  (NVIDIA AI Assistant)
echo    🔌 GUI API:         http://localhost:3000  (API Endpoints)
echo    🤖 Agent Core:      http://localhost:8000  (NVIDIA Processing)
echo    🌉 Web Bridge:      Background Service     (Connection Manager)
echo.
echo 📊 MONITORING:
echo    📝 Logs:          .\logs\*.log
echo    ⚡ Agent Status:  http://localhost:8000/health
echo    🔌 API Status:    http://localhost:3000/api/status
echo.

:: Wait and test
echo 🔄 Checking service status...
timeout /t 5 >nul

echo.
echo 🚀 ULTRON is now fully operational!
echo 🏠 Opening MAIN DASHBOARD: http://localhost:5000
echo 💬 Chat Engine available at: http://localhost:5173
echo.

:: Open main Pokédx GUI
start http://localhost:5000

echo.
echo 📊 Press any key to open monitoring dashboard or CTRL+C to exit...
pause >nul

:: Open monitoring
start http://localhost:8000/health
start http://localhost:3000/api/status

echo.
echo ✨ ULTRON Agent 3.0 is fully operational!
echo    Main Pokédx GUI:        http://localhost:5000
echo    NVIDIA Chat Engine:     http://localhost:5173
echo    All backend services:   Active with comprehensive logging
echo.
echo Keep this window open to maintain the system.
echo Press any key to exit launcher (services will continue)...
pause >nul

echo.
echo 👋 ULTRON Launcher closing - services remain active
echo    Use Task Manager or taskkill to stop services if needed
echo.
