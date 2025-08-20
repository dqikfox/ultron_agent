@echo off
echo 🔧 Rebuilding Ultron Agent Command Center with all fixes...
echo.

cd /d "%~dp0"

echo 📦 Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ❌ npm install failed
    pause
    exit /b 1
)

echo 🏗️ Building application...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo 📱 Packaging for Windows...
call npm run dist:win
if %errorlevel% neq 0 (
    echo ❌ Packaging failed
    pause
    exit /b 1
)

echo.
echo ✅ Build complete!
echo 📁 Executable location: release\win-unpacked\Ultron Agent Command Center.exe
echo.
echo 🧪 Testing Ollama connection...
echo Opening test interface...
start test_chat.html

echo.
echo 🚀 Ready to test!
echo 1. Test Ollama connection in the browser window that opened
echo 2. If Ollama works, run the main app from release\win-unpacked\
echo.
pause