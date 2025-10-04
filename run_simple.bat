@echo off
echo ULTRON Agent 3.0 - Simple Launcher
echo ====================================

:: Check if Ollama is running
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama is already running
) else (
    echo Starting Ollama service...
    start "Ollama Service" "%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe" serve
    echo Waiting for Ollama to start...
    timeout /t 10 /nobreak >nul

    :: Verify Ollama started
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Failed to start Ollama
        pause
        exit /b 1
    )
    echo ✅ Ollama service started successfully
)

:: Check for qwen3-coder:480b-cloud model
echo Checking for qwen3-coder:480b-cloud model...
"%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe" list | findstr "qwen3-coder:480b-cloud" >nul
if %errorlevel% neq 0 (
    echo Model not found. Pulling qwen3-coder:480b-cloud...
    "%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe" pull qwen3-coder:480b-cloud
)

:: Start the web GUI server
echo Starting ULTRON Web GUI Server...
start "ULTRON Web GUI" python web_gui_server.py

echo.
echo ✅ ULTRON Agent is starting!
echo 🌐 Web Interface: http://localhost:8080
echo 🧠 AI Model: qwen3-coder:480b-cloud
echo.
echo Press any key to exit...
pause >nul
