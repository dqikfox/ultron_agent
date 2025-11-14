@echo off
REM Start LangFlow server on port 7860

cd /d C:\Projects\ultron_agent

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start LangFlow
echo Starting LangFlow server on http://localhost:7860
python -m langflow run --host 127.0.0.1 --port 7860

REM Keep window open if error
pause
