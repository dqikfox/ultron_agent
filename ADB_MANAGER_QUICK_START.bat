@echo off
REM ========================================================================
REM ADB MANAGER QUICK START GUIDE
REM ========================================================================
REM This script provides step-by-step instructions for running ADB Manager
REM Location: c:\Projects\ultron_agent\run.bat
REM ========================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           ADB MANAGER - QUICK START GUIDE                     ║
echo ║          Integrated with ULTRON Agent 3.0                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo STEP 1: VERIFY DEVICE CONNECTION
echo ───────────────────────────────────
echo.
echo Run in PowerShell:
echo   adb devices
echo.
echo You should see your device listed:
echo   192.168.1.115:46385     device
echo.

echo STEP 2: START ALL SERVICES
echo ────────────────────────────
echo.
echo Run from c:\Projects\ultron_agent:
echo   run.bat
echo.
echo This will automatically start:
echo   ✓ Ollama LLM backend (port 11434)
echo   ✓ ADB Backend server (port 5003)
echo   ✓ ADB Frontend server (port 8080)
echo   ✓ ULTRON Web GUI (port 8080)
echo   ✓ And other services...
echo.

echo STEP 3: ACCESS ADB MANAGER
echo ────────────────────────────
echo.
echo Open in your browser:
echo   http://localhost:8080/adb.html
echo.
echo Or click the browser window that auto-opens
echo.

echo STEP 4: SELECT YOUR DEVICE
echo ────────────────────────────
echo.
echo In the ADB Manager interface:
echo   1. Dropdown menu will auto-detect your device
echo   2. Select: 192.168.1.115:46385
echo   3. Click "Connect" or "Select Device"
echo.

echo STEP 5: USE THE 7 TABS
echo ───────────────────────
echo.
echo Status Tab
echo   - View device info, battery, storage
echo   - See system properties
echo   - Monitor real-time metrics
echo.
echo Apps Tab
echo   - Browse installed applications
echo   - Search for specific apps
echo   - Install/uninstall apps
echo.
echo Shell Tab
echo   - Execute ADB shell commands
echo   - View command history
echo   - Get output in real-time
echo.
echo Screen Tab
echo   - Tap, swipe, input text
echo   - Press hardware buttons
echo   - Control media playback
echo.
echo Files Tab
echo   - Browse device files
echo   - Transfer files to/from device
echo   - Manage directories
echo.
echo Debug Tab
echo   - View system logs
echo   - Filter by level (ERROR, WARN, INFO)
echo   - Diagnose issues
echo.
echo Settings Tab
echo   - Change display size/density
echo   - Manage permissions
echo   - Configure options
echo.

echo TROUBLESHOOTING
echo ────────────────
echo.
echo Q: Device not showing in dropdown?
echo A: 1. Run: adb connect 192.168.1.115:46385
echo    2. Verify: adb devices
echo    3. Refresh browser
echo.
echo Q: "Backend unavailable" error?
echo A: 1. Check run.bat started ADB Backend
echo    2. Verify: curl http://localhost:5003/health
echo    3. Restart run.bat
echo.
echo Q: Frontend not loading?
echo A: 1. Check browser console (F12)
echo    2. Verify port 8080 is open
echo    3. Try: http://localhost:8080/adb.html directly
echo.
echo Q: Commands not executing?
echo A: 1. Verify device is connected
echo    2. Enable USB debugging on device
echo    3. Grant ADB permissions when prompted
echo.

echo IMPORTANT REMINDERS
echo ────────────────────
echo.
echo ✓ ALWAYS START WITH: run.bat
echo   This launches all required services
echo.
echo ✓ DEVICE CONNECTION:
echo   Use: adb connect 192.168.1.115:46385
echo   Device: Samsung Galaxy S24 (S3SM)
echo.
echo ✓ BROWSER ACCESS:
echo   Main UI: http://localhost:8080/adb.html
echo   ULTRON: http://localhost:8080 (main GUI)
echo.
echo ✓ BACKEND SERVICES:
echo   ADB Backend: http://localhost:5003
echo   Health check: http://localhost:5003/health
echo.

echo DOCUMENTATION
echo ───────────────
echo.
echo Read these for more info:
echo   - ADB_MANAGER_README.md
echo   - ADB_IMPLEMENTATION_COMPLETE.md
echo   - ADB_HTML_FEATURES_GUIDE.md
echo   - TESTING_ENHANCED_ADB.md
echo   - CORE_FUNCTION_TEST_RESULTS.md
echo.

echo ═══════════════════════════════════════════════════════════════════
echo Ready to start? Open PowerShell and run:
echo   cd c:\Projects\ultron_agent
echo   run.bat
echo ═══════════════════════════════════════════════════════════════════
echo.

pause
