@echo off
REM Start ULTRON ADB System (Backend + Frontend)

echo ================================================
echo ULTRON ADB Manager - System Startup
echo ================================================
echo.

REM Start backend server on port 5003
echo [1/2] Starting ADB Backend on port 5003...
start "ADB Backend" python adb_backend_enhanced.py

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start frontend server on port 8080
echo [2/2] Starting Web GUI on port 8080...
start "Web GUI Server" python web_gui_server.py

echo.
echo ================================================
echo Both servers started!
echo Frontend: http://localhost:8080/adb.html
echo Backend:  http://localhost:5003/health
echo ================================================
echo.
pause
