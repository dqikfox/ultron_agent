@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: --- Enhanced ULTRON Agent 3.0 Launcher ---
title ULTRON Agent 3.0 - Enhanced Launcher

:: Configuration
set "PYTHON_CMD=python"
set "VENV_DIR=venv"
set "LOG_FILE=startup_enhanced.log"
set "CONFIG_FILE=ultron_config.json"

:: Colors for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

:: Initialize log file
echo [%date% %time%] ULTRON Agent 3.0 Enhanced Startup > "%LOG_FILE%"

:: Functions
goto :main

:log_info
    echo %GREEN%[INFO]%RESET% %~1
    echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%"
    goto :eof

:log_warn
    echo %YELLOW%[WARN]%RESET% %~1
    echo [%date% %time%] [WARN] %~1 >> "%LOG_FILE%"
    goto :eof

:log_error
    echo %RED%[ERROR]%RESET% %~1
    echo [%date% %time%] [ERROR] %~1 >> "%LOG_FILE%"
    pause
    exit /b 1

:log_success
    echo %GREEN%[SUCCESS]%RESET% %~1
    echo [%date% %time%] [SUCCESS] %~1 >> "%LOG_FILE%"
    goto :eof

:check_python
    call :log_info "Checking Python installation..."
    where %PYTHON_CMD% >nul 2>nul
    if %errorlevel% neq 0 (
        call :log_error "Python is not installed or not in PATH. Please install Python 3.10+."
    )
    
    :: Check Python version
    for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
    call :log_success "Python %PYTHON_VERSION% found"
    goto :eof

:setup_venv
    if not exist "%VENV_DIR%\" (
        call :log_info "Creating virtual environment..."
        %PYTHON_CMD% -m venv "%VENV_DIR%"
        if %errorlevel% neq 0 (
            call :log_error "Failed to create virtual environment"
        )
        call :log_success "Virtual environment created"
    ) else (
        call :log_info "Virtual environment already exists"
    )
    
    call :log_info "Activating virtual environment..."
    call "%VENV_DIR%\Scripts\activate.bat"
    goto :eof

:install_dependencies
    call :log_info "Installing/updating dependencies..."
    
    :: Check if enhanced requirements exist
    if exist "requirements_enhanced.txt" (
        call :log_info "Using enhanced requirements..."
        %PYTHON_CMD% -m pip install --upgrade pip
        %PYTHON_CMD% -m pip install -r requirements_enhanced.txt
    ) else (
        call :log_info "Using standard requirements..."
        %PYTHON_CMD% -m pip install -r requirements.txt
    )
    
    if %errorlevel% neq 0 (
        call :log_error "Failed to install dependencies"
    )
    call :log_success "Dependencies installed successfully"
    goto :eof

:check_config
    call :log_info "Checking configuration..."
    
    if not exist "%CONFIG_FILE%" (
        call :log_warn "Configuration file not found"
        if exist "ultron_config.json.example" (
            call :log_info "Copying example configuration..."
            copy "ultron_config.json.example" "%CONFIG_FILE%" > nul
        )
    )
    
    if not exist ".env" (
        call :log_warn ".env file not found"
        if exist ".env.example" (
            call :log_info "Copying example .env file..."
            copy ".env.example" ".env" > nul
            call :log_warn "Please update .env with your API keys"
        )
    )
    goto :eof

:check_ollama
    call :log_info "Checking Ollama installation..."
    where ollama >nul 2>nul
    if %errorlevel% neq 0 (
        call :log_warn "Ollama not found in PATH. Please install Ollama for full functionality."
        call :log_info "Download from: https://ollama.ai"
    ) else (
        call :log_success "Ollama found"
        
        :: Check if Ollama is running
        curl -s http://localhost:11434/api/tags >nul 2>nul
        if %errorlevel% neq 0 (
            call :log_warn "Ollama service not running. Starting Ollama..."
            start /b ollama serve
            timeout /t 3 >nul
        )
    )
    goto :eof

:security_check
    call :log_info "Performing security checks..."
    
    :: Check for security utilities
    %PYTHON_CMD% -c "import security_utils; print('Security utilities available')" 2>nul
    if %errorlevel% neq 0 (
        call :log_warn "Security utilities not found - some security features may be limited"
    ) else (
        call :log_success "Security utilities loaded"
    )
    goto :eof

:performance_check
    call :log_info "Checking system performance..."
    
    :: Check available memory
    for /f "skip=1 tokens=4" %%i in ('wmic OS get TotalVisibleMemorySize /value') do (
        if not "%%i"=="" set TOTAL_MEM=%%i
    )
    
    :: Convert KB to GB (approximate)
    set /a MEM_GB=!TOTAL_MEM!/1048576
    
    if !MEM_GB! LSS 4 (
        call :log_warn "Low system memory detected: !MEM_GB!GB. Performance may be affected."
    ) else (
        call :log_success "System memory: !MEM_GB!GB"
    )
    goto :eof

:launch_agent
    call :log_info "Launching ULTRON Agent 3.0..."
    call :log_info "Starting with enhanced security and performance monitoring..."
    
    :: Set environment variables for enhanced mode
    set ULTRON_ENHANCED=1
    set ULTRON_SECURITY_MODE=1
    
    :: Launch with error handling
    %PYTHON_CMD% main.py %*
    
    set LAUNCH_RESULT=%errorlevel%
    if %LAUNCH_RESULT% neq 0 (
        call :log_error "ULTRON Agent exited with error code: %LAUNCH_RESULT%"
    ) else (
        call :log_success "ULTRON Agent shutdown normally"
    )
    goto :eof

:: Main execution
:main
call :log_info "=== ULTRON Agent 3.0 Enhanced Startup ==="
call :log_info "Timestamp: %date% %time%"

call :check_python
call :setup_venv
call :install_dependencies
call :check_config
call :check_ollama
call :security_check
call :performance_check

echo.
call :log_info "All checks completed. Launching ULTRON Agent 3.0..."
echo.

call :launch_agent

echo.
call :log_info "=== Startup Complete ==="
call :log_info "Check %LOG_FILE% for detailed logs"

endlocal
pause