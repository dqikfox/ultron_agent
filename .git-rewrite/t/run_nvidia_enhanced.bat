

@echo off
title ULTRON NVIDIA Enhanced Assistant

echo.
echo 🤖 ULTRON NVIDIA Enhanced Assistant
echo ====================================
echo.

echo 📋 Checking requirements...
python -m pip install fastapi uvicorn python-socketio requests openai

echo.
echo 🔑 NVIDIA API Status:
echo   Key 1: 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
echo   Key 2: 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
echo   Expiration: 02/08/2026
echo.

echo 🤖 Available NVIDIA Models:
echo   1. Llama 4 Maverick 17B 128E (Advanced reasoning)
echo   2. GPT-OSS 120B (Large-scale processing)  
echo   3. Llama 3.3 70B (Balanced performance)
echo.

echo 🚀 Starting NVIDIA Enhanced ULTRON...
echo 🌐 Web UI will be available at: http://localhost:8000
echo 📡 WebSocket support: ACTIVE
echo 🔄 Real-time streaming: ENABLED
echo.

echo Press Ctrl+C to stop the server
echo.

python nvidia_enhanced_ultron.py

pause
