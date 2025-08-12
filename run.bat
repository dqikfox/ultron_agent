@echo off
chcp 65001 > nul

:: --- Configuration ---
set "PYTHON_CMD=python"
set "VENV_DIR=venv"

:: --- Title ---
title Ultron Agent 3.0 Launcher

:: --- Functions ---

:: (Batch doesn't have functions in the same way, so we use labels and goto)

:info
    echo [INFO] %~1
    goto :eof

:warn
    echo [WARN] %~1
    goto :eof

:error
    echo [ERROR] %~1
    pause
    exit /b 1

:success
    echo [SUCCESS] %~1
    goto :eof


:: --- Main Script ---

call :info "Starting Ultron Agent 3.0..."

:: 1. Check for Python
call :info "Checking for Python..."
where %PYTHON_CMD% >nul 2>nul
if %errorlevel% neq 0 (
    call :error "%PYTHON_CMD% is not installed or not in PATH. Please install Python 3.8+."
)
call :success "Python check passed."

:: 2. Setup Virtual Environment
if not exist "%VENV_DIR%\" (
    call :info "Virtual environment not found. Creating one at '%VENV_DIR%'..."
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        call :error "Failed to create virtual environment."
    )
    call :success "Virtual environment created."
)

call :info "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"

:: 3. Install/Upgrade Dependencies
call :info "Checking and installing dependencies from requirements.txt..."
%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    call :error "Failed to install dependencies. Please check requirements.txt and your network connection."
)
call :success "Dependencies are up to date."

:: 4. Check for .env file
if not exist ".env" (
    call :warn ".env file not found. Copying from .env.example..."
    call :warn "Please update .env with your API keys for full functionality."
    copy .env.example .env > nul
)

:: 5. Run the Agent
call :info "Launching Ultron Agent 3.0..."

:: Add any command-line arguments here if needed
:: For example: %PYTHON_CMD% main.py --mode cli
%PYTHON_CMD% main.py %*


endlocal
