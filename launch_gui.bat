@echo off
echo ============================================================
echo 🤖 ULTRON Agent 3.0 - GUI Launcher
echo ============================================================
echo.

echo 🚀 Launching ULTRON Enhanced GUI...
echo 📍 Location: gui/ultron_enhanced/web/index.html
echo.

REM Check if GUI file exists
if exist "gui\ultron_enhanced\web\index.html" (
    echo ✅ GUI file found!
    echo 🌐 Opening in default browser...
    start "" "file:///%CD%/gui/ultron_enhanced/web/index.html"
    echo.
    echo ✅ ULTRON Enhanced GUI launched successfully!
    echo.
    echo 🎮 Available Features:
    echo    - 🖥️ Console Interface
    echo    - ⚙️ System Monitoring  
    echo    - 👁️ Vision System
    echo    - 📋 Task Management
    echo    - 📁 File Browser
    echo    - 🔧 Configuration
    echo    - 👤 User Profile
    echo    - 🤖 AI Chat Integration
    echo.
    echo 📖 For more info: GUI_DOCUMENTATION.md
) else (
    echo ❌ GUI file not found!
    echo 📂 Expected location: gui\ultron_enhanced\web\index.html
    echo.
    echo 🔧 Manual access:
    echo    1. Navigate to gui\ultron_enhanced\web\
    echo    2. Open index.html in your browser
)

echo.
echo ============================================================
pause