@echo off
echo ================================================
echo ULTRON Agent - Complete Deployment
echo ================================================
echo.

echo [1/4] Running Tests...
pytest tests\test_enhancements.py -v
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some tests failed
    pause
)

echo.
echo [2/4] Validating System...
python startup_validator.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Validation failed
    pause
    exit /b 1
)

echo.
echo [3/4] Building ULTRON...
python build_ultron.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Launching ULTRON...
echo.
echo ================================================
echo ULTRON Agent Ready - Starting Now
echo ================================================
python main.py
