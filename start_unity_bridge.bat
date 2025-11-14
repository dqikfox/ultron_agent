@echo off
echo Starting Unity AI Bridge...
echo.
echo Bridge will connect:
echo - Unity AI Assistant/Generators/Inference (port 8765)
echo - ULTRON Ollama Backend (port 11434)
echo.

python unity_bridge.py

pause
