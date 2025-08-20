@echo off
echo 🚀 Starting ULTRON Agent Command Center...
echo.

REM Clean up any existing ULTRON processes first
echo 🔄 Cleaning up existing processes...
wmic process where "commandline like '%%nvidia_enhanced_ultron.py%%'" delete >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start the AI Chat Server on port 8000 (FIXED: using /c instead of /k)
echo 📡 Starting AI Chat Server...
start "ULTRON AI Chat" /MIN cmd /c "cd /d C:\Projects\ultron_agent_2 && python nvidia_enhanced_ultron.py > logs\nvidia_chat.log 2>&1"

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Verify server is running
echo 🔍 Verifying AI Chat Server...
netstat -an | find ":8000 " >nul && echo ✅ AI Chat Server: RUNNING || echo ❌ AI Chat Server: FAILED

REM Start the Electron GUI if it exists
if exist "C:\Projects\ultron_agent_2\core\ultron-agent-command-center\release\win-unpacked\Ultron Agent Command Center.exe" (
    echo 🖥️ Starting Command Center GUI...
    start "ULTRON GUI" "C:\Projects\ultron_agent_2\core\ultron-agent-command-center\release\win-unpacked\Ultron Agent Command Center.exe"
) else (
    echo ⚠️ GUI not found, opening web interface...
    timeout /t 2 /nobreak >nul
    start http://localhost:8000
)

echo.
echo ✅ ULTRON Agent 2 is operational!
echo 🌐 AI Chat: http://localhost:8000
echo 🖥️ Interface: GUI launched (or web fallback)
echo 📊 Logs: .\logs\nvidia_chat.log
echo.
echo 💡 NOTE: This launcher now prevents terminal multiplication!
echo Press any key to exit launcher (services continue running)...
pause
