@echo off
echo Fixing Virtual Environment Issues...

REM Remove old virtual environment
if exist .venv-1 (
    echo Removing old virtual environment...
    rmdir /s /q .venv-1
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv .venv

REM Activate and install requirements
echo Activating virtual environment and installing packages...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Virtual environment fixed!
echo Please restart VS Code now.
pause