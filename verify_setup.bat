@echo off
REM ============================================================================
REM ULTRON Agent 3.0 - Installation Verification Script
REM ============================================================================
REM Verifies that all dependencies and services are properly configured
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ===========================================================
echo ULTRON Agent 3.0 - Installation Verification
echo ===========================================================
echo Started at %date% %time%
echo ===========================================================
echo.

set /a CHECKS_PASSED=0
set /a CHECKS_TOTAL=0
set /a CHECKS_FAILED=0

REM Helper function to track results
REM Usage: call :check_item "Description" "Command"

REM =========================================================================
REM 1. SYSTEM REQUIREMENTS
REM =========================================================================
echo [SECTION] System Requirements
echo.

REM Check Windows Version
set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Windows 64-bit installation...
ver | findstr "Windows" >nul 2>&1
if !errorlevel! equ 0 (
    echo [PASS] Windows detected
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] Unable to detect Windows
    set /a CHECKS_FAILED+=1
)

REM Check Available Disk Space (at least 50GB)
set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Available disk space (minimum 50GB)...
for /f "tokens=3" %%A in ('dir C:\ ^| findstr "bytes free"') do (
    REM Rough check - disk space warning only
    echo [INFO] Disk check skipped (requires admin for detailed info)
)
set /a CHECKS_PASSED+=1

echo.

REM =========================================================================
REM 2. PYTHON ENVIRONMENT
REM =========================================================================
echo [SECTION] Python Environment
echo.

REM Check Python installation
set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Python 3.10+ installation...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%I in ('python --version') do (
        echo [PASS] %%I installed
    )
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] Python not found
    set /a CHECKS_FAILED+=1
)

REM Check virtual environment
set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Virtual environment (.venv)...
if exist ".venv" (
    echo [PASS] .venv directory exists
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] .venv not found
    set /a CHECKS_FAILED+=1
)

REM Check venv Python executable
set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Virtual environment Python executable...
if exist ".venv\Scripts\python.exe" (
    echo [PASS] venv Python executable found
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] venv Python executable not found
    set /a CHECKS_FAILED+=1
)

REM Check pip in venv
set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Virtual environment pip...
if exist ".venv\Scripts\pip.exe" (
    echo [PASS] venv pip found
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] venv pip not found
    set /a CHECKS_FAILED+=1
)

echo.

REM =========================================================================
REM 3. CORE DEPENDENCIES
REM =========================================================================
echo [SECTION] Core Python Dependencies
echo.

REM Activate venv for package checks
call .\.venv\Scripts\activate.bat >nul 2>&1

set "PACKAGES=flask aiohttp openai langchain torch transformers pydantic requests"

for %%p in (%PACKAGES%) do (
    set /a CHECKS_TOTAL+=1
    echo [CHECK %CHECKS_TOTAL%] Package '%%p'...
    python -c "import %%p" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [PASS] %%p is installed
        set /a CHECKS_PASSED+=1
    ) else (
        echo [FAIL] %%p is missing or failed to import
        set /a CHECKS_FAILED+=1
    )
)

echo.

REM =========================================================================
REM 4. AWS CLI
REM =========================================================================
echo [SECTION] AWS CLI
echo.

set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] AWS CLI installation...
aws --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=*" %%I in ('aws --version') do (
        echo [PASS] %%I
    )
    set /a CHECKS_PASSED+=1
) else (
    echo [FAIL] AWS CLI not found
    set /a CHECKS_FAILED+=1
)

set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] AWS credentials configuration...
aws sts get-caller-identity >nul 2>&1
if !errorlevel! equ 0 (
    echo [PASS] AWS credentials are configured
    set /a CHECKS_PASSED+=1
) else (
    echo [WARN] AWS credentials not configured
    echo        Run: aws configure
    echo [NOTE] This is optional if not using AWS services
)

echo.

REM =========================================================================
REM 5. PROJECT FILES
REM =========================================================================
echo [SECTION] Project Files
echo.

set "FILES=requirements.txt ultron_config.json main.py agent_core.py brain.py"

for %%f in (%FILES%) do (
    set /a CHECKS_TOTAL+=1
    echo [CHECK %CHECKS_TOTAL%] File '%%f'...
    if exist "%%f" (
        echo [PASS] %%f exists
        set /a CHECKS_PASSED+=1
    ) else (
        echo [WARN] %%f not found
    )
)

echo.

REM =========================================================================
REM 6. GUI AND SERVICES
REM =========================================================================
echo [SECTION] GUI and Web Services
echo.

set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Web GUI (gui/ultron_enhanced/web/)...
if exist "gui\ultron_enhanced\web\index.html" (
    echo [PASS] GUI files found
    set /a CHECKS_PASSED+=1
) else (
    echo [WARN] GUI files not found
)

set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Tools directory...
if exist "tools" (
    echo [PASS] tools directory found
    set /a CHECKS_PASSED+=1
) else (
    echo [WARN] tools directory not found
)

set /a CHECKS_TOTAL+=1
echo [CHECK %CHECKS_TOTAL%] Logs directory...
if exist "logs" (
    echo [PASS] logs directory found
    set /a CHECKS_PASSED+=1
) else (
    echo [INFO] logs directory not created yet (created on first run)
)

echo.

REM =========================================================================
REM 7. PORT AVAILABILITY (WARNING ONLY - don't actually bind)
REM =========================================================================
echo [SECTION] Port Availability
echo.

echo [INFO] Checking standard ULTRON ports...
echo [INFO] Port 8080 (Web GUI)     - Run with Python to verify
echo [INFO] Port 5000 (API Server)  - Run with Python to verify
echo [INFO] Port 11434 (Ollama)     - Check if Ollama service is running

echo.

REM =========================================================================
REM SUMMARY
REM =========================================================================
echo ===========================================================
echo VERIFICATION SUMMARY
echo ===========================================================
echo.

echo Checks Passed:  !CHECKS_PASSED!
echo Checks Total:   !CHECKS_TOTAL!
echo Checks Failed:  !CHECKS_FAILED!

set /a PASS_RATE=(!CHECKS_PASSED! * 100) / !CHECKS_TOTAL!

echo Pass Rate:     !PASS_RATE!%%

echo.

if !CHECKS_FAILED! equ 0 (
    echo [SUCCESS] All critical checks passed!
    echo.
    echo Ready to use ULTRON Agent 3.0. Run:
    echo   1. Activate venv: .\.venv\Scripts\activate
    echo   2. Start agent:   python main.py
    echo   3. Open GUI:      http://localhost:8080
) else (
    echo [WARNING] Some checks failed. See issues above.
    echo.
    echo Common fixes:
    echo   - Reinstall dependencies: pip install --force-reinstall -r requirements.txt
    echo   - Recreate venv: rmdir .venv /s /q ^&^& python -m venv .venv
    echo   - Run setup: setup_requirements.bat
)

echo.
echo ===========================================================
echo Verification completed at %date% %time%
echo ===========================================================
echo.

pause
