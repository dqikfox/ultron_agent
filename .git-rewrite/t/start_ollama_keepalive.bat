@echo off
echo 🤖 ULTRON Agent 2 - Ollama Keep-Alive Service
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Check if Ollama is running
echo 🔍 Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama server not responding. Starting Ollama...
    start "Ollama Server" ollama serve
    timeout /t 5 /nobreak >nul
)

REM Install required packages if needed
echo 📦 Installing/checking required packages...
python -m pip install requests >nul 2>&1

echo.
echo 🚀 Starting Ollama Keep-Alive Service...
echo 📋 Model: qwen2.5-coder:1.5b (Memory Optimized)
echo ⏱️  Ping interval: 4 minutes
echo 🛑 Press Ctrl+C to stop
echo.

REM Start the keep-alive service
python ollama_keepalive.py --model qwen2.5-coder:1.5b --interval 240 --daemon

pause
