@echo off
:: ULTRON Agent 3.0 - Remote Access Setup
:: Configures Windows Firewall for remote access
:: Run as Administrator

title ULTRON Remote Access Setup

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          ULTRON Agent 3.0 - Remote Access Setup             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges!
    echo Right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [INFO] Setting up Windows Firewall rules...
echo.

:: Add firewall rules for ULTRON services
echo [1/4] Adding rule for Web GUI (Port 8080)...
netsh advfirewall firewall add rule name="ULTRON Web GUI" dir=in action=allow protocol=TCP localport=8080 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web GUI firewall rule added
) else (
    echo ⚠️  Web GUI rule may already exist
)

echo [2/4] Adding rule for Frontend UI (Port 5175)...
netsh advfirewall firewall add rule name="ULTRON Frontend UI" dir=in action=allow protocol=TCP localport=5175 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend UI firewall rule added
) else (
    echo ⚠️  Frontend UI rule may already exist
)

echo [3/4] Adding rule for NVIDIA Chat (Port 8002)...
netsh advfirewall firewall add rule name="ULTRON NVIDIA Chat" dir=in action=allow protocol=TCP localport=8002 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ NVIDIA Chat firewall rule added
) else (
    echo ⚠️  NVIDIA Chat rule may already exist
)

echo [4/4] Adding rule for API Server (Port 5000)...
netsh advfirewall firewall add rule name="ULTRON API Server" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API Server firewall rule added
) else (
    echo ⚠️  API Server rule may already exist
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  SETUP COMPLETE!                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Your ULTRON Agent is now accessible remotely!
echo.
echo 🌐 LOCAL ACCESS:
echo    http://localhost:8080      - Web GUI (ATLAS Neural Core)
echo    http://localhost:5175      - Frontend UI (Pokédex)
echo    http://localhost:8002      - NVIDIA Chat
echo.
echo 🌍 REMOTE ACCESS (Same Network):
echo    http://192.168.1.131:8080  - Web GUI (ATLAS Neural Core)
echo    http://192.168.1.131:5175  - Frontend UI (Pokédex)
echo    http://192.168.1.131:8002  - NVIDIA Chat
echo.
echo 📱 MOBILE ACCESS:
echo    Use the URLs above on your phone/tablet browser
echo.
echo 🔒 SECURITY NOTES:
echo    - Firewall rules allow access from your local network
echo    - For internet access, configure router port forwarding
echo    - Consider using VPN for secure remote access
echo.
echo Press any key to exit...
pause >nul
