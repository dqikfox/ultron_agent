@echo off
REM ============================================================================
REM ULTRON Agent 3.0 - Requirements Installation & Update
REM ============================================================================
REM Run as Administrator for best results
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ===========================================================
echo ULTRON Agent 3.0 - Requirements Setup
echo ===========================================================
echo Starting at %date% %time%
echo ===========================================================
echo.

REM =========================================================================
REM AWS CLI CHECK
REM =========================================================================
echo [INFO] Checking AWS CLI installation...
aws --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%I in ('aws --version') do (
        echo [SUCCESS] AWS CLI is installed: %%I
    )
) else (
    echo [WARNING] AWS CLI not found
    echo [INFO] To install AWS CLI v2, visit:
    echo        https://awscli.amazonaws.com/AWSCLIV2.msi
)

echo.

REM =========================================================================
REM PYTHON CHECK
REM =========================================================================
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%I in ('python --version') do (
        echo [SUCCESS] Python is installed: %%I
    )
) else (
    echo [ERROR] Python not found in PATH
    echo [INFO] Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo.

REM =========================================================================
REM VIRTUAL ENVIRONMENT
REM =========================================================================
echo [INFO] Checking virtual environment...
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
    if !errorlevel! equ 0 (
        echo [SUCCESS] Virtual environment created
    ) else (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Virtual environment already exists
)

echo.

REM =========================================================================
REM ACTIVATE AND UPGRADE PIP
REM =========================================================================
echo [INFO] Activating virtual environment...
call .\.venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

echo.
echo [INFO] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if !errorlevel! equ 0 (
    echo [SUCCESS] Core tools upgraded
) else (
    echo [ERROR] Failed to upgrade pip
)

echo.

REM =========================================================================
REM INSTALL DEPENDENCIES
REM =========================================================================
echo [INFO] Installing project dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if !errorlevel! equ 0 (
        echo [SUCCESS] Dependencies installed
    ) else (
        echo [ERROR] Failed to install dependencies
    )
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

echo.

REM =========================================================================
REM VERIFICATION
REM =========================================================================
echo [INFO] Verifying critical packages...

setlocal enabledelayedexpansion
for %%p in (flask,aiohttp,openai,langchain,torch) do (
    python -c "import %%p" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] %%p is available
    ) else (
        echo [WARNING] %%p may have issues
    )
)

echo.

REM =========================================================================
REM AWS CREDENTIALS CHECK
REM =========================================================================
echo [INFO] Checking AWS configuration...
aws sts get-caller-identity >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] AWS credentials are configured
) else (
    echo [WARNING] AWS credentials not configured
    echo [INFO] Run: aws configure
)

echo.
echo ===========================================================
echo [SUCCESS] Setup Complete!
echo ===========================================================
echo.
echo Next steps:
echo   1. Configure AWS credentials: aws configure
echo   2. Start Ollama service: .\run.bat
echo   3. Launch agent: python main.py
echo.
echo ===========================================================

pause
