@echo off
echo ========================================
echo ULTRON Agent - Integrated System Launch
echo ========================================

echo.
echo [1/5] Starting API Integration Server...
start "ULTRON API Server" cmd /k "cd /d %~dp0 && python api_integration_server.py"
timeout /t 3 /nobreak >nul

echo [2/5] Starting OpenAI Computer Use...
start "Computer Use Test" cmd /k "cd /d %~dp0 && python test_openai_computer_use.py"
timeout /t 2 /nobreak >nul

echo [3/5] Starting Unity Integration Server...
start "Unity Server" cmd /k "cd /d %~dp0 && python unity_integration.py"
timeout /t 2 /nobreak >nul

echo [4/5] Starting Avatar Game Server...
start "Avatar Control API" cmd /k "cd /d %~dp0 && python avatar_control_api.py"
timeout /t 2 /nobreak >nul

echo [5/5] Opening ULTRON GUI...
start "ULTRON GUI" "http://localhost:8080"
timeout /t 1 /nobreak >nul

echo.
echo ========================================
echo ULTRON INTEGRATED SYSTEM ONLINE
echo ========================================
echo.
echo Services Running:
echo - API Server: http://localhost:5002
echo - Unity Server: http://localhost:5001  
echo - Avatar API: http://localhost:8003
echo - ULTRON GUI: http://localhost:8080
echo - Computer Use: Active
echo.
echo Press any key to exit...
pause >nul