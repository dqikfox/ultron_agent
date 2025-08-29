@echo off
setlocal enabledelayedexpansion

REM Define colors for better readability
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "RESET=[0m"

title ULTRON Agent 2 - Unified Launcher

echo %BLUE%
echo  _    _ _   _______ _____   ____  _   _                            _     ___  
echo ^| ^|  ^| ^| ^| ^|__   __^|  __ \ / __ \^| \ ^| ^|     /\                  ^| ^|   ^|__ \ 
echo ^| ^|  ^| ^| ^|    ^| ^|  ^| ^|__) ^| ^|  ^| ^|  \^| ^|    /  \   __ _  ___ _ __ ^| ^|_     ) ^|
echo ^| ^|  ^| ^| ^|    ^| ^|  ^|  _  /^| ^|  ^| ^| . ` ^|   / /\ \ / _` ^|/ _ \ '_ \^| __^|   / / 
echo ^| ^|__^| ^| ^|____^| ^|  ^| ^| \ \^| ^|__^| ^| ^|\  ^|  / ____ \ (_^| ^|  __/ ^| ^| ^| ^|_   / /_ 
echo  \____/^|______^|_^|  ^|_^|  \_\\____/^|_^| \_^| /_/    \_\__, ^|\___ ^|_^| ^|_^|\__^| ^|____^|
echo                                                  __/ ^|                      
echo                                                 ^|___/                       
echo %RESET%
echo %GREEN%===== Unified Launcher v1.0 =====%RESET%
echo.

:menu
echo %YELLOW%Select launch mode:%RESET%
echo %GREEN%1.%RESET% Full System (NVIDIA AI + Web GUI + API Server + Command Center)
echo %GREEN%2.%RESET% NVIDIA Enhanced AI Only
echo %GREEN%3.%RESET% Web GUI Only
echo %GREEN%4.%RESET% Pokédex GUI
echo %GREEN%5.%RESET% Development Mode (with debug logging)
echo %GREEN%6.%RESET% Clean Logs
echo %GREEN%7.%RESET% Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto full_system
if "%choice%"=="2" goto nvidia_only
if "%choice%"=="3" goto web_gui_only
if "%choice%"=="4" goto pokedex_gui
if "%choice%"=="5" goto dev_mode
if "%choice%"=="6" goto clean_logs
if "%choice%"=="7" goto end

echo %RED%Invalid choice. Please try again.%RESET%
goto menu

:full_system
echo.
echo %GREEN%🚀 Starting ULTRON Agent - Full System...%RESET%
echo.

REM Clean up any existing ULTRON processes first
echo %YELLOW%🔄 Cleaning up existing processes...%RESET%
wmic process where "commandline like '%%nvidia_enhanced_ultron.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%web_gui_server.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%api_server.py%%'" delete >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start the AI Chat Server on port 8000
echo %YELLOW%📡 Starting ULTRON NVIDIA Enhanced AI Chat Server (port 8000)...%RESET%
start "ULTRON NVIDIA Chat" /MIN cmd /c "cd /d C:\Projects\ultron_agent_2 && python nvidia_enhanced_ultron.py > logs\nvidia_chat.log 2>&1"

echo %YELLOW%🌐 Starting ULTRON Web GUI Server (port 8080)...%RESET%
start "ULTRON Web GUI" /MIN cmd /c "cd /d C:\Projects\ultron_agent_2 && python web_gui_server.py > logs\web_gui_server.log 2>&1"

echo %YELLOW%🔗 Starting ULTRON API Server (port 5000)...%RESET%
start "ULTRON API Server" /MIN cmd /c "cd /d C:\Projects\ultron_agent_2 && python api_server.py > logs\api_server.log 2>&1"

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Verify servers are running
echo %YELLOW%🔍 Verifying servers...%RESET%
netstat -an | find ":8000 " >nul && echo %GREEN%✅ AI Chat Server: RUNNING%RESET% || echo %RED%❌ AI Chat Server: FAILED%RESET%
netstat -an | find ":8080 " >nul && echo %GREEN%✅ Web GUI Server: RUNNING%RESET% || echo %RED%❌ Web GUI Server: FAILED%RESET%
netstat -an | find ":5000 " >nul && echo %GREEN%✅ API Server: RUNNING%RESET% || echo %RED%❌ API Server: FAILED%RESET%

REM Start the Electron GUI if it exists
if exist "C:\Projects\ultron_agent_2\core\ultron-agent-command-center\release\win-unpacked\Ultron Agent Command Center.exe" (
    echo %YELLOW%🖥️ Starting Command Center GUI...%RESET%
    start "ULTRON GUI" "C:\Projects\ultron_agent_2\core\ultron-agent-command-center\release\win-unpacked\Ultron Agent Command Center.exe"
) else (
    echo %YELLOW%⚠️ GUI not found, opening web interface...%RESET%
    timeout /t 2 /nobreak >nul
    start http://localhost:8000
)

echo.
echo %GREEN%✅ ULTRON Agent 2 is operational!%RESET%
echo %YELLOW%🌐 AI Chat: http://localhost:8000%RESET%
echo %YELLOW%🖥️ Interface: GUI launched (or web fallback)%RESET%
echo %YELLOW%📊 Logs: .\logs\%RESET%
echo.
goto end_with_pause

:nvidia_only
echo.
echo %GREEN%🚀 Starting ULTRON NVIDIA Enhanced AI Only...%RESET%
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo %YELLOW%📋 Checking requirements...%RESET%
python -m pip install fastapi uvicorn python-socketio requests openai

echo.
echo %YELLOW%🔑 NVIDIA API Status:%RESET%
echo   Key 1: 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
echo   Key 2: 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
echo   Expiration: 02/08/2026
echo.

echo %YELLOW%🤖 Available NVIDIA Models:%RESET%
echo   1. Llama 4 Maverick 17B 128E (Advanced reasoning)
echo   2. GPT-OSS 120B (Large-scale processing)  
echo   3. Llama 3.3 70B (Balanced performance)
echo.

echo %YELLOW%🚀 Starting NVIDIA Enhanced ULTRON...%RESET%
echo %YELLOW%🌐 Web UI will be available at: http://localhost:8000%RESET%
echo %YELLOW%📡 WebSocket support: ACTIVE%RESET%
echo %YELLOW%🔄 Real-time streaming: ENABLED%RESET%
echo.

echo %YELLOW%Press Ctrl+C to stop the server%RESET%
echo.

python nvidia_enhanced_ultron.py
goto end

:web_gui_only
echo.
echo %GREEN%🚀 Starting ULTRON Web GUI Only...%RESET%
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo %YELLOW%🌐 Starting ULTRON Web GUI Server (port 8080)...%RESET%
start "ULTRON Web GUI" /MIN cmd /c "cd /d C:\Projects\ultron_agent_2 && python web_gui_server.py > logs\web_gui_server.log 2>&1"

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

REM Verify server is running
echo %YELLOW%🔍 Verifying Web GUI Server...%RESET%
netstat -an | find ":8080 " >nul && echo %GREEN%✅ Web GUI Server: RUNNING%RESET% || echo %RED%❌ Web GUI Server: FAILED%RESET%

echo.
echo %GREEN%✅ ULTRON Web GUI is operational!%RESET%
echo %YELLOW%🌐 Web Interface: http://localhost:8080%RESET%
echo %YELLOW%📊 Logs: .\logs\web_gui_server.log%RESET%
echo.
goto end_with_pause

:pokedex_gui
echo.
echo %GREEN%🚀 Starting ULTRON Pokédex GUI...%RESET%
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo %YELLOW%🔍 Checking for Pokédex GUI...%RESET%
if exist "C:\Projects\ultron_agent_2\gui\ultron_enhanced\web\index.html" (
    echo %GREEN%✅ Pokédex GUI found!%RESET%
) else (
    echo %RED%❌ Pokédex GUI not found!%RESET%
    goto menu
)

echo %YELLOW%🚀 Starting Pokédex GUI...%RESET%
python run_pokedex_ultron.py
goto end

:dev_mode
echo.
echo %GREEN%🚀 Starting ULTRON in Development Mode...%RESET%
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo %YELLOW%📋 Setting up development environment...%RESET%
set "DEBUG_MODE=true"
set "LOG_LEVEL=DEBUG"

echo %YELLOW%📡 Starting ULTRON NVIDIA Enhanced AI Chat Server with debug logging...%RESET%
start "ULTRON NVIDIA Chat Debug" cmd /c "cd /d C:\Projects\ultron_agent_2 && python nvidia_enhanced_ultron.py --debug > logs\nvidia_chat_debug.log 2>&1"

echo %YELLOW%🌐 Starting ULTRON Web GUI Server with debug logging...%RESET%
start "ULTRON Web GUI Debug" cmd /c "cd /d C:\Projects\ultron_agent_2 && python web_gui_server.py --debug > logs\web_gui_server_debug.log 2>&1"

echo %YELLOW%🔗 Starting ULTRON API Server with debug logging...%RESET%
start "ULTRON API Server Debug" cmd /c "cd /d C:\Projects\ultron_agent_2 && python api_server.py --debug > logs\api_server_debug.log 2>&1"

echo.
echo %GREEN%✅ ULTRON Development Mode is operational!%RESET%
echo %YELLOW%🌐 AI Chat: http://localhost:8000%RESET%
echo %YELLOW%🌐 Web GUI: http://localhost:8080%RESET%
echo %YELLOW%🌐 API: http://localhost:5000%RESET%
echo %YELLOW%📊 Debug Logs: .\logs\*_debug.log%RESET%
echo.
goto end_with_pause

:clean_logs
echo.
echo %YELLOW%🧹 Cleaning log files...%RESET%

if exist "logs" (
    del /q "logs\*.log" 2>nul
    echo %GREEN%✅ Log files cleaned!%RESET%
) else (
    echo %YELLOW%⚠️ No logs directory found.%RESET%
    mkdir logs
    echo %GREEN%✅ Created logs directory.%RESET%
)

echo.
goto menu

:end_with_pause
echo %YELLOW%Press any key to return to menu (services will continue running)...%RESET%
pause >nul
cls
goto menu

:end
echo.
echo %GREEN%Thank you for using ULTRON Agent 2!%RESET%
echo.
endlocal