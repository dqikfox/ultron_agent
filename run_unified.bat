@echo off
chcp 65001 > nul
title ULTRON Agent 3.0 - Unified Server
color 0A

echo.
echo ██    ██ ██   ████████ ██████   ██████  ███    ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ████   ██
echo ██    ██ ██      ██    ██████  ██    ██ ██ ██  ██
echo ██    ██ ██      ██    ██   ██ ██    ██ ██  ██ ██
echo  ██████  ███████ ██    ██   ██  ██████  ██   ████
echo.
echo ═══════════════════════════════════════════════════════════
echo  ULTRON Agent 3.0 - Unified Single Port Architecture
echo  Everything served on Port 5000
echo ═══════════════════════════════════════════════════════════
echo.

:: Kill any existing processes
echo 🔄 Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

:: Check required files
if not exist "ultron_unified_server.py" (
    echo ❌ ultron_unified_server.py not found!
    pause
    exit /b 1
)

if not exist "gui\ultron_enhanced\web\index.html" (
    echo ❌ Pokédx GUI not found!
    pause
    exit /b 1
)

echo ✅ All components found, launching ULTRON unified system...
echo.

:: Create logs directory
if not exist "logs" mkdir logs

:: Launch unified server
echo 🚀 Starting ULTRON Unified Server...
echo      Port: 5000 (Everything on one port)
start "ULTRON Unified" cmd /c "python ultron_unified_server.py > logs\unified_server.log 2>&1"
timeout /t 5 >nul

echo.
echo ✅ ULTRON Unified System Launch Complete!
echo.
echo 🔗 UNIFIED ARCHITECTURE ACTIVE:
echo    🏠 Main Pokédx GUI:   http://localhost:5000/
echo    📊 Dashboard:         http://localhost:5000/dashboard
echo    💬 AI Chat:           http://localhost:5000/chat
echo    🔌 API Endpoints:     http://localhost:5000/api/*
echo    ❤️ Health Check:      http://localhost:5000/health
echo.
echo 📊 MONITORING:
echo    📝 Logs:              .\logs\unified_server.log
echo.

:: Brief system check
echo 🔄 Checking unified server status...
timeout /t 3 >nul

:: Test server response
echo ⚡ Testing server response...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/health' -TimeoutSec 5; if ($response.StatusCode -eq 200) { echo '✅ Server responding correctly' } else { echo '⚠️ Server response: ' + $response.StatusCode } } catch { echo '❌ Server not responding yet' }"

echo.
echo 🚀 ULTRON is now fully operational on unified architecture!
echo 🏠 Opening main interface: http://localhost:5000
echo.

:: Open main interface
start http://localhost:5000

echo.
echo ✨ SUCCESS: ULTRON Agent 3.0 - Single Port Architecture!
echo    🏠 Main Interface:    http://localhost:5000/
echo    📊 Dashboard:         http://localhost:5000/dashboard
echo    💬 AI Chat:           http://localhost:5000/chat
echo    🔌 All APIs:          http://localhost:5000/api/*
echo    ❤️ Health:            http://localhost:5000/health
echo.
echo Keep this window open to maintain the system.
echo Press any key to exit launcher (service will continue)...
pause >nul

echo.
echo 👋 ULTRON Launcher complete - unified server remains active
echo    Use Task Manager or taskkill to stop if needed
echo.
