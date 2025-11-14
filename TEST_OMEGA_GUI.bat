@echo off
echo Testing OMEGA GUI...
start python web_gui_server.py
timeout /t 3 /nobreak >nul
start http://localhost:8080
echo.
echo GUI launched at http://localhost:8080
echo.
echo Test these features:
echo - Ctrl+N: Quick Notes
echo - Click 🎥: Screen Recorder
echo - Click 💻: Code Snippets
echo - Click 🌙: Dark Mode
echo - Type in search bar at top
echo.
pause
