@echo off
title ULTRON Project Monitoring Suite
color 0C

echo.
echo 🔴 ULTRON Project Monitoring Suite
echo ================================
echo.

echo 📊 Starting monitoring components...

REM Start monitoring dashboard
echo [1/4] Starting Monitoring Dashboard...
start "Monitor Dashboard" cmd /c "python monitoring_dashboard.py"
timeout /t 3 >nul

REM Start Copilot assistant
echo [2/4] Starting Copilot Assistant...
start "Copilot Assistant" cmd /c "python copilot_assistant.py"
timeout /t 2 >nul

REM Start progress tracking
echo [3/4] Starting Progress Tracker...
start "Progress Tracker" cmd /c "python -c \"from progress_tracker import tracker; import time; [print(tracker.get_progress_report()) or time.sleep(300) for _ in iter(int, 1)]\""
timeout /t 2 >nul

REM Start project intelligence
echo [4/4] Starting Project Intelligence...
start "Project Intelligence" cmd /c "python project_intelligence.py"
timeout /t 2 >nul

echo.
echo ✅ All monitoring components started!
echo.
echo 🌐 Access Points:
echo    📊 Dashboard:     http://localhost:9000
echo    🤖 AI Hub:        Background Service
echo    📈 Progress:      Background Service
echo    💡 Copilot:       Background Service
echo.
echo 🚀 Opening monitoring dashboard...
start http://localhost:9000

echo.
echo Keep this window open to maintain monitoring services.
pause