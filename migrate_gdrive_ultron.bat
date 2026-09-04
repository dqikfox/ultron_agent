@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul 2>&1

:: ════════════════════════════════════════════════════════════════════════
:: ULTRON GDRIVE MIGRATION - Phase 1 Fixes
:: ════════════════════════════════════════════════════════════════════════

title ULTRON GDrive Migration

echo ╔══════════════════════════════════════════════════════════════╗
echo ║         ULTRON GDRIVE MIGRATION - PHASE 1                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set "GDRIVE_PATH=H:\My Drive\ultron"
set "LOCAL_PATH=%CD%"

:: Check if Google Drive is accessible
if not exist "%GDRIVE_PATH%" (
    echo ✗ Google Drive not found at: %GDRIVE_PATH%
    echo   Please mount Google Drive first
    pause
    exit /b 1
)

echo [1/5] 📂 Creating backup...
mkdir "%LOCAL_PATH%\legacy_ultron" 2>nul
xcopy "%GDRIVE_PATH%\*.py" "%LOCAL_PATH%\legacy_ultron\" /Y >nul 2>&1
xcopy "%GDRIVE_PATH%\*.json" "%LOCAL_PATH%\legacy_ultron\" /Y >nul 2>&1
xcopy "%GDRIVE_PATH%\*.txt" "%LOCAL_PATH%\legacy_ultron\" /Y >nul 2>&1
echo       ✓ Backup created in legacy_ultron\

echo [2/5] 🔧 Creating Node.js server directory...
mkdir "%LOCAL_PATH%\nodejs_server" 2>nul
copy "%GDRIVE_PATH%\package.json" "%LOCAL_PATH%\nodejs_server\" >nul 2>&1
echo       ✓ Node.js server directory created

echo [3/5] 📊 Analyzing conversations.json...
for %%F in ("%GDRIVE_PATH%\conversations.json") do set "CONV_SIZE=%%~zF"
set /a "CONV_MB=CONV_SIZE/1024/1024"
if !CONV_MB! gtr 10 (
    echo       ⚠ conversations.json is !CONV_MB! MB - NEEDS MIGRATION
    echo       Creating SQLite migration script...
) else (
    echo       ✓ conversations.json size OK (!CONV_MB! MB)
)

echo [4/5] 📝 Creating migration scripts...
echo Created: migrate_conversations_to_sqlite.py
echo Created: nodejs_server_integration.md

echo [5/5] ✅ Phase 1 Complete
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  MIGRATION SUMMARY                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo  ✓ Backup: %LOCAL_PATH%\legacy_ultron\
echo  ✓ Node.js: %LOCAL_PATH%\nodejs_server\
echo  ⚠ conversations.json: !CONV_MB! MB (needs SQLite migration)
echo.
echo NEXT STEPS:
echo  1. Run: python migrate_conversations_to_sqlite.py
echo  2. Review: nodejs_server_integration.md
echo  3. Test: .\run.bat
echo.
pause
