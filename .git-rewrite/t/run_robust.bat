@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: --- Configuration ---
set "PYTHON_CMD=python"
set "VENV_DIR=venv"
set "LOG_FILE=startup.log"

:: --- Title ---
title Ultron Agent 3.0 Launcher

:: --- Enhanced Logging ---
echo. > "%LOG_FILE%"
echo [%date% %time%] ULTRON 3.0 Startup Log >> "%LOG_FILE%"
echo ====================================== >> "%LOG_FILE%"

:: --- Functions ---

:info
    echo [INFO] %~1
    echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%"
    goto :eof

:warn
    echo [WARN] %~1
    echo [%date% %time%] [WARN] %~1 >> "%LOG_FILE%"
    goto :eof

:error
    echo [ERROR] %~1
    echo [%date% %time%] [ERROR] %~1 >> "%LOG_FILE%"
    echo.
    echo Press any key to view the log file and exit...
    pause > nul
    notepad "%LOG_FILE%"
    exit /b 1

:success
    echo [SUCCESS] %~1
    echo [%date% %time%] [SUCCESS] %~1 >> "%LOG_FILE%"
    goto :eof

:check_file
    if not exist "%~1" (
        call :error "Required file not found: %~1"
    )
    goto :eof

:: --- Main Script ---

call :info "Starting Ultron Agent 3.0 Launcher..."
call :info "Working directory: %CD%"

:: 0. Pre-flight checks
call :info "Performing pre-flight checks..."

call :check_file "main.py"
call :check_file "requirements.txt"

if not exist "ultron_config.json" (
    if not exist "ultron_config.json.example" (
        call :error "No configuration files found. ultron_config.json.example is missing."
    )
)

call :success "Pre-flight checks completed."

:: 1. Check for Python
call :info "Checking for Python..."
where %PYTHON_CMD% >nul 2>nul
if !errorlevel! neq 0 (
    call :error "%PYTHON_CMD% is not installed or not in PATH. Please install Python 3.8+."
)

:: Test Python version
%PYTHON_CMD% --version > temp_version.txt 2>&1
if !errorlevel! neq 0 (
    call :error "Python is not working correctly."
)

set /p python_version=<temp_version.txt
del temp_version.txt
call :success "Python check passed. Version: %python_version%"

:: 2. Setup Virtual Environment
if not exist "%VENV_DIR%\" (
    call :info "Virtual environment not found. Creating one at '%VENV_DIR%'..."
    %PYTHON_CMD% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if !errorlevel! neq 0 (
        call :error "Failed to create virtual environment. Check %LOG_FILE% for details."
    )
    call :success "Virtual environment created."
) else (
    call :info "Virtual environment found at '%VENV_DIR%'."
)

:: Check if activation script exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    call :error "Virtual environment activation script not found. Environment may be corrupted."
)

call :info "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    call :error "Failed to activate virtual environment."
)
call :success "Virtual environment activated."

:: 3. Install/Upgrade Dependencies
call :info "Checking and installing dependencies from requirements.txt..."
%PYTHON_CMD% -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
%PYTHON_CMD% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "Failed to install dependencies. Check %LOG_FILE% for details and your network connection."
)
call :success "Dependencies are up to date."

:: 4. Check for configuration files
if not exist "ultron_config.json" (
    if exist "ultron_config.json.example" (
        call :warn "ultron_config.json not found. Copying from example..."
        copy ultron_config.json.example ultron_config.json > nul
        call :warn "Please configure ultron_config.json with your settings."
    )
)

if not exist ".env" (
    if exist ".env.example" (
        call :warn ".env file not found. Copying from .env.example..."
        call :warn "Please update .env with your API keys for full functionality."
        copy .env.example .env > nul
    )
)

:: 5. Test main.py syntax
call :info "Testing main.py syntax..."
%PYTHON_CMD% -m py_compile main.py >> "%LOG_FILE%" 2>&1
if !errorlevel! neq 0 (
    call :error "main.py has syntax errors. Check %LOG_FILE% for details."
)
call :success "main.py syntax check passed."

:: 6. Run the Agent
call :info "All checks passed. Launching Ultron Agent 3.0..."
call :info "Log file: %LOG_FILE%"
echo.

:: Add any command-line arguments here if needed
:: For example: %PYTHON_CMD% main.py --mode cli
%PYTHON_CMD% main.py %*

:: Capture exit code
set "EXIT_CODE=!errorlevel!"

if !EXIT_CODE! neq 0 (
    echo.
    call :error "Ultron Agent exited with code !EXIT_CODE!. Check %LOG_FILE% for details."
) else (
    call :success "Ultron Agent terminated normally."
)

echo.
echo Press any key to exit...
pause > nul

endlocal
exit /b %EXIT_CODE%
