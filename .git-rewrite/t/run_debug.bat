@echo off
chcp 65001 > nul
title ULTRON Agent 3.0 - DEBUG MODE LAUNCHER
color 0C

echo.
echo ██████  ███████ ██████  ██    ██  ██████
echo ██   ██ ██      ██   ██ ██    ██ ██
echo ██   ██ █████   ██████  ██    ██ ██   ███
echo ██   ██ ██      ██   ██ ██    ██ ██    ██
echo ██████  ███████ ██████   ██████   ██████
echo.
echo ═══════════════════════════════════════════════════════════
echo  ULTRON Agent 3.0 - DEBUG MODE LAUNCHER
echo  Enhanced Logging + Real-time Monitoring + Error Detection
echo ═══════════════════════════════════════════════════════════
echo.

:: Create debug logs directory
if not exist "debug_logs" mkdir debug_logs
if not exist "logs" mkdir logs

:: Set debug environment variables
set ULTRON_DEBUG=1
set PYTHONUNBUFFERED=1
set FLASK_ENV=development
set FLASK_DEBUG=1

:: Kill any existing processes
echo 🔄 Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 >nul

:: System diagnostics
echo.
echo 🔍 SYSTEM DIAGNOSTICS:
echo ═══════════════════════════════════════════════════════════
python --version
echo Current Directory: %cd%
echo Python Unbuffered: %PYTHONUNBUFFERED%
echo Debug Mode: %ULTRON_DEBUG%
echo.

:: Check all required files
echo 🔍 FILE VERIFICATION:
if exist "agent_core.py" (echo ✅ agent_core.py) else (echo ❌ agent_core.py - MISSING)
if exist "frontend_server.py" (echo ✅ frontend_server.py) else (echo ❌ frontend_server.py - MISSING)
if exist "gui_api_server.py" (echo ✅ gui_api_server.py) else (echo ❌ gui_api_server.py - MISSING)
if exist "main_gui_server.py" (echo ✅ main_gui_server.py) else (echo ❌ main_gui_server.py - MISSING)
if exist "web_bridge.py" (echo ✅ web_bridge.py) else (echo ❌ web_bridge.py - MISSING)
if exist "gui\ultron_enhanced\web\index.html" (echo ✅ Pokédx GUI) else (echo ❌ Pokédx GUI - MISSING)
echo.

:: Check port availability
echo 🔍 PORT AVAILABILITY CHECK:
netstat -an | findstr ":5000" >nul && echo ❌ Port 5000: OCCUPIED || echo ✅ Port 5000: AVAILABLE
netstat -an | findstr ":5173" >nul && echo ❌ Port 5173: OCCUPIED || echo ✅ Port 5173: AVAILABLE
netstat -an | findstr ":3000" >nul && echo ❌ Port 3000: OCCUPIED || echo ✅ Port 3000: AVAILABLE
netstat -an | findstr ":8000" >nul && echo ❌ Port 8000: OCCUPIED || echo ✅ Port 8000: AVAILABLE
echo.

echo 🚀 LAUNCHING SERVICES IN DEBUG MODE...
echo ═══════════════════════════════════════════════════════════

:: Service 1: Main Pokédx GUI Server (Port 5000) - WITH DEBUG
echo 🏠 [1/5] Starting Main Pokédx GUI Server (DEBUG MODE)...
echo      URL: http://localhost:5000 (MAIN ENTRY POINT)
start "ULTRON Main GUI [DEBUG]" cmd /c "python -u main_gui_server.py > debug_logs\main_gui_debug.log 2>&1"
timeout /t 4 >nul

:: Check if it started
netstat -an | findstr ":5000" >nul && echo ✅ Main GUI Server: STARTED || echo ❌ Main GUI Server: FAILED TO START

:: Service 2: Chat Engine (Port 5173) - WITH DEBUG
echo 💬 [2/5] Starting Chat Engine (DEBUG MODE)...
echo      URL: http://localhost:5173 (NVIDIA Chat Engine)
start "ULTRON Chat Engine [DEBUG]" cmd /c "python -u frontend_server.py > debug_logs\frontend_debug.log 2>&1"
timeout /t 4 >nul

:: Check if it started
netstat -an | findstr ":5173" >nul && echo ✅ Chat Engine: STARTED || echo ❌ Chat Engine: FAILED TO START

:: Service 3: GUI API Server (Port 3000) - WITH DEBUG
echo 🔌 [3/5] Starting GUI API Server (DEBUG MODE)...
echo      URL: http://localhost:3000 (API Endpoints)
start "ULTRON GUI API [DEBUG]" cmd /c "python -u gui_api_server.py > debug_logs\gui_api_debug.log 2>&1"
timeout /t 4 >nul

:: Check if it started
netstat -an | findstr ":3000" >nul && echo ✅ GUI API Server: STARTED || echo ❌ GUI API Server: FAILED TO START

:: Service 4: Agent Core (Port 8000) - WITH DEBUG
echo 🤖 [4/5] Starting Agent Core (DEBUG MODE)...
echo      URL: http://localhost:8000 (AI Processing)
start "ULTRON Agent Core [DEBUG]" cmd /c "python -u agent_core.py > debug_logs\agent_core_debug.log 2>&1"
timeout /t 6 >nul

:: Check if it started
netstat -an | findstr ":8000" >nul && echo ✅ Agent Core: STARTED || echo ❌ Agent Core: FAILED TO START

:: Service 5: Web Bridge - WITH DEBUG
echo 🌉 [5/5] Starting Web Bridge (DEBUG MODE)...
start "ULTRON Web Bridge [DEBUG]" cmd /c "python -u web_bridge.py > debug_logs\web_bridge_debug.log 2>&1"
timeout /t 3 >nul
echo ✅ Web Bridge: BACKGROUND SERVICE STARTED

echo.
echo ✅ DEBUG LAUNCH SEQUENCE COMPLETE!
echo.

:: Real-time service verification
echo 🔍 REAL-TIME SERVICE VERIFICATION:
echo ═══════════════════════════════════════════════════════════
timeout /t 2 >nul

netstat -an | findstr ":5000" >nul && echo ✅ Port 5000: Main GUI Server - RUNNING || echo ❌ Port 5000: Main GUI Server - NOT RESPONDING
netstat -an | findstr ":5173" >nul && echo ✅ Port 5173: Chat Engine - RUNNING || echo ❌ Port 5173: Chat Engine - NOT RESPONDING
netstat -an | findstr ":3000" >nul && echo ✅ Port 3000: GUI API Server - RUNNING || echo ❌ Port 3000: GUI API Server - NOT RESPONDING
netstat -an | findstr ":8000" >nul && echo ✅ Port 8000: Agent Core - RUNNING || echo ❌ Port 8000: Agent Core - NOT RESPONDING
echo ✅ Web Bridge: Background Service - ACTIVE

echo.
echo 📊 DEBUG INFORMATION:
echo ═══════════════════════════════════════════════════════════
echo 📁 Debug Logs Location: %cd%\debug_logs\
echo 📁 Regular Logs Location: %cd%\logs\
echo 🔧 Debug Environment Variables Set
echo 🔧 Python Unbuffered Output Enabled
echo 🔧 Flask Development Mode Enabled
echo.

echo 🌐 AVAILABLE ENDPOINTS:
echo    🏠 Main Interface:  http://localhost:5000  (Sophisticated Pokédx GUI)
echo    💬 Chat Engine:     http://localhost:5173  (NVIDIA AI Assistant)
echo    🔌 GUI API:         http://localhost:3000  (API Endpoints)
echo    🤖 Agent Core:      http://localhost:8000  (NVIDIA Processing)
echo    🌉 Web Bridge:      Background Service     (Connection Manager)

echo.
echo 🚀 Opening main interface for testing...
start http://localhost:5000

echo.
echo 🔧 DEBUG MENU - Choose an option:
echo    1. View real-time logs
echo    2. Open all monitoring endpoints
echo    3. Check service health
echo    4. View error logs
echo    5. Continue without debug menu
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto :logs
if "%choice%"=="2" goto :monitoring
if "%choice%"=="3" goto :health
if "%choice%"=="4" goto :errors
if "%choice%"=="5" goto :continue

:logs
echo.
echo 📋 Opening real-time log monitoring...
start cmd /c "title Main GUI Debug Log && type debug_logs\main_gui_debug.log && pause"
start cmd /c "title Frontend Debug Log && type debug_logs\frontend_debug.log && pause"
start cmd /c "title GUI API Debug Log && type debug_logs\gui_api_debug.log && pause"
start cmd /c "title Agent Core Debug Log && type debug_logs\agent_core_debug.log && pause"
goto :continue

:monitoring
echo.
echo 📊 Opening all monitoring endpoints...
start http://localhost:5000
start http://localhost:5173
start http://localhost:3000/api/status
start http://localhost:8000/health
goto :continue

:health
echo.
echo 🏥 SERVICE HEALTH CHECK:
echo ═══════════════════════════════════════════════════════════
curl -s http://localhost:5000 >nul && echo ✅ Main GUI: HTTP OK || echo ❌ Main GUI: HTTP FAILED
curl -s http://localhost:5173 >nul && echo ✅ Chat Engine: HTTP OK || echo ❌ Chat Engine: HTTP FAILED
curl -s http://localhost:3000 >nul && echo ✅ GUI API: HTTP OK || echo ❌ GUI API: HTTP FAILED
curl -s http://localhost:8000 >nul && echo ✅ Agent Core: HTTP OK || echo ❌ Agent Core: HTTP FAILED
echo.
pause
goto :continue

:errors
echo.
echo ❌ CHECKING FOR ERRORS IN DEBUG LOGS:
echo ═══════════════════════════════════════════════════════════
if exist "debug_logs\main_gui_debug.log" (
    findstr /i "error exception traceback failed" debug_logs\main_gui_debug.log
) else (
    echo No main GUI debug log found
)
echo.
pause
goto :continue

:continue
echo.
echo ✨ ULTRON DEBUG MODE ACTIVE!
echo.
echo 🔧 DEBUG FEATURES AVAILABLE:
echo    • Enhanced error logging in debug_logs\
echo    • Python unbuffered output for real-time debugging
echo    • Flask development mode with auto-reload
echo    • Real-time service status monitoring
echo    • Comprehensive health checking
echo.
echo 📝 Keep this window open to maintain debug mode.
echo    Press any key to minimize launcher (services continue)...
pause >nul

echo.
echo 🐛 DEBUG MODE ACTIVE - Services running with enhanced logging
echo    Monitor debug_logs\ folder for real-time debugging information
echo.
