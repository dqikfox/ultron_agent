@echo off
REM UGS CLI Windows Installation Script
echo Installing Unity Gaming Services CLI for Windows...

REM Download Windows binary directly
echo Downloading UGS CLI Windows binary...
curl -L -o "%TEMP%\ugs-windows-x64.exe" "https://github.com/Unity-Technologies/unity-gaming-services-cli/releases/latest/download/ugs-windows-x64.exe"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Download failed
    exit /b 1
)

REM Create installation directory
set "INSTALL_DIR=%USERPROFILE%\.ugs"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Move binary to installation directory
move /Y "%TEMP%\ugs-windows-x64.exe" "%INSTALL_DIR%\ugs.exe"

echo.
echo SUCCESS: UGS CLI installed to %INSTALL_DIR%\ugs.exe
echo.
echo Add to PATH: %INSTALL_DIR%
echo Then run: ugs --version
echo.
pause
