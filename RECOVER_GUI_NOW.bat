@echo off
echo ═══════════════════════════════════════════════════════════
echo   🆘 ULTRON GUI EMERGENCY RECOVERY
echo ═══════════════════════════════════════════════════════════
echo.
echo This script will help you recover your GUI if it's broken.
echo.
echo Choose recovery method:
echo.
echo [1] Restore from latest backup
echo [2] Restore from Git (last commit)
echo [3] Restore from Git (2 commits ago)
echo [4] Restore from specific backup
echo [5] Show available backups
echo [6] Cancel
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto restore_latest
if "%choice%"=="2" goto restore_git_head
if "%choice%"=="3" goto restore_git_head2
if "%choice%"=="4" goto restore_specific
if "%choice%"=="5" goto show_backups
if "%choice%"=="6" goto end

:restore_latest
echo.
echo Searching for latest backup...
for /f "delims=" %%i in ('dir /b /od "gui\ultron_enhanced\web\backups" 2^>nul') do set latest=%%i
if not defined latest (
    echo ❌ No backups found!
    goto end
)
echo Found: %latest%
echo.
set /p confirm="Restore from %latest%? (Y/N): "
if /i not "%confirm%"=="Y" goto end

echo.
echo Restoring files...
copy "gui\ultron_enhanced\web\backups\%latest%\index.html" "gui\ultron_enhanced\web\index.html" /Y >nul 2>&1 && echo ✓ Restored: index.html || echo ✗ Failed: index.html
copy "gui\ultron_enhanced\web\backups\%latest%\app.js" "gui\ultron_enhanced\web\app.js" /Y >nul 2>&1 && echo ✓ Restored: app.js || echo ✗ Failed: app.js
copy "gui\ultron_enhanced\web\backups\%latest%\styles.css" "gui\ultron_enhanced\web\styles.css" /Y >nul 2>&1 && echo ✓ Restored: styles.css || echo ✗ Failed: styles.css
echo.
echo ✓ Recovery complete!
goto verify

:restore_git_head
echo.
echo Restoring from Git (last commit)...
git checkout HEAD -- gui/ultron_enhanced/web/index.html 2>nul && echo ✓ Restored: index.html || echo ✗ Failed: index.html
git checkout HEAD -- gui/ultron_enhanced/web/app.js 2>nul && echo ✓ Restored: app.js || echo ✗ Failed: app.js
git checkout HEAD -- gui/ultron_enhanced/web/styles.css 2>nul && echo ✓ Restored: styles.css || echo ✗ Failed: styles.css
echo.
echo ✓ Recovery complete!
goto verify

:restore_git_head2
echo.
echo Restoring from Git (2 commits ago)...
git checkout HEAD~2 -- gui/ultron_enhanced/web/index.html 2>nul && echo ✓ Restored: index.html || echo ✗ Failed: index.html
git checkout HEAD~2 -- gui/ultron_enhanced/web/app.js 2>nul && echo ✓ Restored: app.js || echo ✗ Failed: app.js
git checkout HEAD~2 -- gui/ultron_enhanced/web/styles.css 2>nul && echo ✓ Restored: styles.css || echo ✗ Failed: styles.css
echo.
echo ✓ Recovery complete!
goto verify

:restore_specific
echo.
echo Available backups:
dir /b /od "gui\ultron_enhanced\web\backups" 2>nul
echo.
set /p backup="Enter backup folder name: "
if not exist "gui\ultron_enhanced\web\backups\%backup%" (
    echo ❌ Backup not found!
    goto end
)
echo.
echo Restoring from %backup%...
copy "gui\ultron_enhanced\web\backups\%backup%\index.html" "gui\ultron_enhanced\web\index.html" /Y >nul 2>&1 && echo ✓ Restored: index.html || echo ✗ Failed: index.html
copy "gui\ultron_enhanced\web\backups\%backup%\app.js" "gui\ultron_enhanced\web\app.js" /Y >nul 2>&1 && echo ✓ Restored: app.js || echo ✗ Failed: app.js
copy "gui\ultron_enhanced\web\backups\%backup%\styles.css" "gui\ultron_enhanced\web\styles.css" /Y >nul 2>&1 && echo ✓ Restored: styles.css || echo ✗ Failed: styles.css
echo.
echo ✓ Recovery complete!
goto verify

:show_backups
echo.
echo Available backups:
echo ───────────────────────────────────────────────────────────
dir /b /od "gui\ultron_enhanced\web\backups" 2>nul || echo No backups found
echo.
pause
goto end

:verify
echo.
echo ═══════════════════════════════════════════════════════════
echo   VERIFICATION
echo ═══════════════════════════════════════════════════════════
echo.
echo File sizes:
for %%f in (gui\ultron_enhanced\web\index.html gui\ultron_enhanced\web\app.js gui\ultron_enhanced\web\styles.css) do (
    for %%s in ("%%f") do echo   %%~nxf: %%~zs bytes
)
echo.
echo Next steps:
echo 1. Test in browser: http://localhost:8080
echo 2. Check console for errors (F12)
echo 3. Run: python monitor_gui.py --save
echo 4. Run: .\protect_gui.bat
echo.

:end
echo ═══════════════════════════════════════════════════════════
pause
