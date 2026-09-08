@echo off
echo 🔧 ULTRON DEBUG TOOLKIT MENU
echo ═══════════════════════════════════════
echo.
echo Available Debug Tools:
echo.
echo  1. 🚀 Launch ULTRON in Debug Mode       (run_debug.bat)
echo  2. 🔍 Run Diagnostic Test Suite         (debug_test.py)
echo  3. 📊 Start Real-time Monitor           (debug_monitor.py)
echo  4. 🌐 Open Debug Dashboard              (debug_dashboard.html)
echo  5. 🧪 Quick System Check                (debug_test.py quick)
echo  6. 📝 View Debug Logs                   (File Explorer)
echo  7. 🔄 Normal ULTRON Launch              (run.bat)
echo  8. ❌ Exit
echo.

set /p choice="Select option (1-8): "

if "%choice%"=="1" goto debug_launch
if "%choice%"=="2" goto diagnostic
if "%choice%"=="3" goto monitor
if "%choice%"=="4" goto dashboard
if "%choice%"=="5" goto quick_check
if "%choice%"=="6" goto view_logs
if "%choice%"=="7" goto normal_launch
if "%choice%"=="8" goto exit

echo Invalid choice, please try again.
pause
goto start

:debug_launch
echo.
echo 🚀 Launching ULTRON in Debug Mode...
call run_debug.bat
goto end

:diagnostic
echo.
echo 🔍 Running Diagnostic Test Suite...
python debug_test.py
pause
goto start

:monitor
echo.
echo 📊 Starting Real-time Monitor...
echo Choose monitoring type:
echo   1. Single check
echo   2. Continuous monitoring (10s)
echo   3. Check log files
set /p monitor_choice="Select (1-3): "

if "%monitor_choice%"=="1" python debug_monitor.py single
if "%monitor_choice%"=="2" python debug_monitor.py continuous 10
if "%monitor_choice%"=="3" python debug_monitor.py logs

pause
goto start

:dashboard
echo.
echo 🌐 Opening Debug Dashboard...
start debug_dashboard.html
echo Dashboard opened in your default browser
pause
goto start

:quick_check
echo.
echo 🧪 Running Quick System Check...
python debug_test.py quick
pause
goto start

:view_logs
echo.
echo 📝 Opening Debug Logs Directory...
if exist "debug_logs" (
    start explorer "debug_logs"
) else (
    echo No debug logs directory found. Run debug mode first.
)
pause
goto start

:normal_launch
echo.
echo 🔄 Launching ULTRON in Normal Mode...
call run.bat
goto end

:start
cls
goto menu

:menu
echo 🔧 ULTRON DEBUG TOOLKIT MENU
echo ═══════════════════════════════════════
echo.
echo Available Debug Tools:
echo.
echo  1. 🚀 Launch ULTRON in Debug Mode       (run_debug.bat)
echo  2. 🔍 Run Diagnostic Test Suite         (debug_test.py)
echo  3. 📊 Start Real-time Monitor           (debug_monitor.py)
echo  4. 🌐 Open Debug Dashboard              (debug_dashboard.html)
echo  5. 🧪 Quick System Check                (debug_test.py quick)
echo  6. 📝 View Debug Logs                   (File Explorer)
echo  7. 🔄 Normal ULTRON Launch              (run.bat)
echo  8. ❌ Exit
echo.

set /p choice="Select option (1-8): "

if "%choice%"=="1" goto debug_launch
if "%choice%"=="2" goto diagnostic
if "%choice%"=="3" goto monitor
if "%choice%"=="4" goto dashboard
if "%choice%"=="5" goto quick_check
if "%choice%"=="6" goto view_logs
if "%choice%"=="7" goto normal_launch
if "%choice%"=="8" goto exit

echo Invalid choice, please try again.
pause
goto start

:exit
echo.
echo 👋 Exiting ULTRON Debug Toolkit
exit /b 0

:end
