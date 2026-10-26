@echo off
echo 🚀 Starting ULTRON Agent 3.0 with Pokedex Interface...
echo.

python run_pokedex_ultron.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Error occurred. Check ultron_pokedex.log for details.
    pause
)
