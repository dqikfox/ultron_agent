@echo off
REM Optimized Ollama startup for lightweight resource usage
REM Best for: qwen2.5-coder:1.5b, qwen2.5vl:3b, gpt-oss cloud models
REM System: 65GB RAM + RTX 3050

setlocal enabledelayedexpansion

REM Lightweight configuration - focus on responsiveness
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_NUM_THREAD=8
set OLLAMA_GPU_MEMORY=1500000000

REM Start Ollama with lightweight settings
echo.
echo ============================================================
echo [OLLAMA] Starting Lightweight Mode
echo ============================================================
echo Configuration:
echo - GPU Parallel: 1 (sequential models)
echo - CPU Threads: 8 (leaving 4 cores free)
echo - GPU Memory: 1.5GB (conservative allocation)
echo - Peak System Usage: 3.6GB (models + overhead)
echo.
echo Expected Models:
echo - qwen2.5-coder:1.5b (397MB, autocomplete)
echo - qwen2.5vl:3b (3.2GB, security review)
echo - gpt-oss:20b-cloud (API-based, zero local)
echo.
echo Status: Ready for A2-A6 rapid deployment
echo ============================================================
echo.

ollama serve

pause
