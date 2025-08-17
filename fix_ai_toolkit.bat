@echo off
echo Fixing AI Toolkit Configuration...

REM Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo ERROR: OPENAI_API_KEY environment variable not set
    echo Please set it with: setx OPENAI_API_KEY "your-api-key-here"
    pause
    exit /b 1
)

echo API Key found: %OPENAI_API_KEY:~0,8%...
echo Restarting VS Code...
taskkill /f /im Code.exe 2>nul
timeout /t 2 /nobreak >nul
code .
echo Done!