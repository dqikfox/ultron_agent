@echo off
echo Starting Langflow server...
echo.

REM Start Langflow in background
start "Langflow Server" cmd /c "langflow run --host 127.0.0.1 --port 7861"

echo Waiting for Langflow to start (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo Creating flows...
python create_flows_now.py

echo.
echo Done! Check langflow_flow_ids.json for your flow IDs
pause
