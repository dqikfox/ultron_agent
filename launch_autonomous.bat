@echo off
echo 🤖 ULTRON Agent - Autonomous Mode Launcher
echo ==========================================
echo.

echo Starting autonomous capabilities...
echo.

echo 1. Starting Web GUI with autonomous features...
start "ULTRON Web GUI" python web_gui_server.py

echo 2. Waiting for GUI to initialize...
timeout /t 3 /nobreak >nul

echo 3. Opening autonomous interface...
start "" "http://localhost:8080/#autonomous"

echo.
echo ✅ Autonomous mode launched successfully!
echo.
echo Access the autonomous controls at:
echo   http://localhost:8080 (Navigate to AUTONOMOUS section)
echo.
echo Press any key to exit...
pause >nul