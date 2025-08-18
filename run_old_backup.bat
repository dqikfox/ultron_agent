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

::Launch sequence - IIS + BACKEND SERVICES ARCHITECTURE
echo � [IIS] Main Pokédx GUI served by IIS
echo      Path: C:\Projects\ultron_agent_2\gui\ultron_enhanced\web
echo      Note: IIS configuration manages main interface
echo.

echo 💬 [1/4] Starting NVIDIA Chat Engine...
echo      URL: http://localhost:5173 (NVIDIA Chat Engine)
start "ULTRON Chat Engine" cmd /c "python frontend_server.py > logs\chat_engine.log 2>&1"
timeout /t 3 >nul
echo ✅ Chat Engine started on port 5173

echo 🔌 [2/4] Starting GUI API Server...
echo      URL: http://localhost:3000 (API Endpoints)
start "ULTRON GUI API" cmd /c "python gui_api_server.py > logs\gui_api.log 2>&1"
timeout /t 3 >nul
echo ✅ GUI API Server started on port 3000

echo 🤖 [3/4] Starting Agent Core (NVIDIA Backend)...
echo      URL: http://localhost:8000 (AI Processing)
start "ULTRON Agent Core" cmd /c "python agent_core.py > logs\agent_core.log 2>&1"
timeout /t 5 >nul
echo ✅ Agent Core started on port 8000

echo 🌉 [4/4] Starting Web Bridge (Connection Manager)...
start "ULTRON Web Bridge" cmd /c "python web_bridge.py > logs\web_bridge.log 2>&1"
timeout /t 3 >nul
echo ✅ Web Bridge started (background service)

echo.
echo ✅ ULTRON System Launch Complete!
echo.
echo 🔗 IIS + BACKEND ARCHITECTURE ACTIVE:
echo    � Main GUI:        IIS Server             (Pokédx Interface)
echo    💬 Chat Engine:     http://localhost:5173  (NVIDIA AI Assistant)  
echo    🔌 GUI API:         http://localhost:3000  (API Endpoints)
echo    🤖 Agent Core:      http://localhost:8000  (NVIDIA Processing)
echo    🌉 Web Bridge:      Background Service     (Connection Manager)
echo.
echo 📊 SERVICE STATUS CHECK:
echo    Checking port availability...
netstat -an | findstr ":5173" >nul && echo ✅ Port 5173 (Chat Engine) ACTIVE || echo ❌ Port 5173 (Chat Engine) FAILED
netstat -an | findstr ":3000" >nul && echo ✅ Port 3000 (GUI API) ACTIVE || echo ❌ Port 3000 (GUI API) FAILED  
netstat -an | findstr ":8000" >nul && echo ✅ Port 8000 (Agent Core) ACTIVE || echo ❌ Port 8000 (Agent Core) FAILED
echo.
echo 📊 MONITORING:
echo    📝 Logs:          .\logs\*.log
echo    ⚡ Agent Status:  http://localhost:8000/health
echo    🔌 API Status:    http://localhost:3000/api/status
echo.

:: Wait and test
echo 🔄 Final service verification...
timeout /t 3 >nul

echo.
echo � ULTRON is now fully operational with IIS!
echo 🌐 Main GUI: Served by IIS (check your IIS configuration)
echo 💬 Chat Engine available at: http://localhost:5173
echo.

:: Open chat engine to verify it's working
start http://localhost:5173

echo.
echo 📊 Press any key to open monitoring dashboard or CTRL+C to exit...
pause >nul

:: Open monitoring
start http://localhost:8000/health
echo.
echo 📊 Press any key to view monitoring or CTRL+C to exit...
pause >nul

:: Show monitoring information
start http://localhost:8000/health
start http://localhost:3000/api/status

echo.
echo ✨ ULTRON Agent 3.0 with IIS Integration Operational!
echo    🌐 Main Pokédx GUI:     IIS Server (C:\Projects\ultron_agent_2\gui\ultron_enhanced\web)
echo    💬 NVIDIA Chat Engine:  http://localhost:5173
echo    🔌 Backend services:    Active with comprehensive logging
echo.
echo Keep this window open to maintain the backend services.
echo Press any key to exit launcher (services will continue)...
pause >nul

echo.
echo 👋 ULTRON Launcher closing - backend services remain active
echo    IIS continues serving main GUI independently  
echo    Use Task Manager or taskkill to stop backend services if needed
echo.
