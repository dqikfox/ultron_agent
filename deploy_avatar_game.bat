@echo off
echo ========================================
echo ULTRON AVATAR GAME - DEPLOYMENT
echo ========================================
echo.

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo.
echo [2/5] Installing dependencies...
pip install flask flask-cors flask-socketio python-socketio --quiet

echo.
echo [3/5] Starting Avatar Game Server...
start "ULTRON Avatar Server" cmd /k "python avatar_game_server.py"
timeout /t 3 /nobreak >nul

echo.
echo [4/5] Starting Web GUI Server...
start "ULTRON Web GUI" cmd /k "python web_gui_server.py"
timeout /t 3 /nobreak >nul

echo.
echo [5/5] Opening game in browser...
timeout /t 2 /nobreak >nul
start http://localhost:8082

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Avatar Game Server: http://localhost:8082
echo Web GUI Server: http://localhost:8080
echo.
echo Press any key to view status...
pause >nul

echo.
echo Testing connections...
curl -s http://localhost:8082/api/tools/test -X POST -H "Content-Type: application/json" -d "{\"tool\":\"all\"}"

echo.
echo.
echo ========================================
echo CONTROLS:
echo ========================================
echo SPACE - Spawn Avatar
echo V - Voice Control
echo B - Start Battle
echo I - Integrate ULTRON
echo.
echo Press any key to exit...
pause >nul
