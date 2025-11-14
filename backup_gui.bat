@echo off
setlocal enabledelayedexpansion

:: Generate timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set BACKUP_DIR=gui\ultron_enhanced\web\backups\%TIMESTAMP%

echo ═══════════════════════════════════════════════════════════
echo   ULTRON GUI BACKUP SYSTEM
echo ═══════════════════════════════════════════════════════════
echo.
echo Creating backup: %TIMESTAMP%
echo.

:: Create backup directory
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: Backup files
copy "gui\ultron_enhanced\web\index.html" "%BACKUP_DIR%\index.html" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backed up: index.html
) else (
    echo ✗ Failed: index.html
)

copy "gui\ultron_enhanced\web\app.js" "%BACKUP_DIR%\app.js" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backed up: app.js
) else (
    echo ✗ Failed: app.js
)

copy "gui\ultron_enhanced\web\styles.css" "%BACKUP_DIR%\styles.css" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backed up: styles.css
) else (
    echo ✗ Failed: styles.css
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   Backup Location: %BACKUP_DIR%
echo ═══════════════════════════════════════════════════════════
echo.
