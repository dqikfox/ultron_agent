@echo off
echo 🤖 ULTRON Agent 3.0 - Web GUI Launcher
echo =====================================
echo.

rem Check if web_gui folder exists
if not exist "web_gui" (
    echo ❌ Web GUI folder not found!
    echo Please ensure the web GUI files have been copied to the web_gui folder.
    echo.
    pause
    exit /b 1
)

echo 🌐 Starting ULTRON Web GUI...
echo 📂 Serving from: web_gui\
echo 🌍 Browser will open automatically
echo 🔴 Press Ctrl+C to stop
echo.

rem Start the web GUI server
python web_gui_server.py

echo.
echo 👋 ULTRON Web GUI has stopped.
pause
