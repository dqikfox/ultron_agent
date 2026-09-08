@echo off
chcp 65001 > nul
title ULTRON AGENT - MASTER CONTROL

:MENU
cls
echo.
echo  U L T R O N  A G E N T - M A S T E R  C O N T R O L
echo  ===================================================
echo.
echo  [1] Launch Complete System (Agent 3.0)
echo  [2] Launch Simple System (NVIDIA Enhanced)
echo  [3] Launch Pokedex GUI
echo  [4] Open Enhanced Web GUI (Client-Only)
echo.
echo  [5] ---
echo  [6] System Cleanup (Kill processes, delete logs)
echo.
echo  [Q] Quit
echo.

choice /C 12346Q /M "Select an option: "

if errorlevel 6 goto QUIT
if errorlevel 5 goto CLEANUP
if errorlevel 4 goto WEB_GUI
if errorlevel 3 goto POKEDEX
if errorlevel 2 goto SIMPLE_SYSTEM
if errorlevel 1 goto COMPLETE_SYSTEM

:COMPLETE_SYSTEM
echo "Launching Complete System (Agent 3.0)..."
start "ULTRON Agent 3.0" cmd /c "run_clean.bat"
goto END

:SIMPLE_SYSTEM
echo "Launching Simple System (NVIDIA Enhanced)..."
start "ULTRON NVIDIA" cmd /c "run.bat"
goto END

:POKEDEX
echo "Launching Pokedex GUI..."
start "ULTRON Pokedex" cmd /c "run_pokedex.bat"
goto END

:WEB_GUI
echo "Opening Enhanced Web GUI (Client-Only)..."
start "ULTRON Web GUI" "gui/ultron_enhanced/web/index.html"
goto END

:CLEANUP
echo "Running system cleanup..."
echo "Terminating all python processes..."
taskkill /F /IM python.exe >nul 2>&1
echo "Deleting log files..."
del /Q logs\*.log >nul 2>&1
echo "Deleting __pycache__ directories..."
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo "Removing %%d"
        rd /s /q "%%d"
    )
)
echo "Cleanup complete."
pause
goto MENU

:QUIT
exit

:END
echo.
echo "Launch command sent. Check the new window(s)."
echo "This window can be closed."
pause
