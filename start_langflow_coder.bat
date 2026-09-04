@echo off
echo Starting ULTRON Langflow Coder...
start http://localhost:8003/chat.html
cd game
python -m http.server 8003
