@echo off
echo ═══════════════════════════════════════════════════════════
echo   ULTRON GUI HEALTH CHECK
echo ═══════════════════════════════════════════════════════════
echo.

echo [1] FILE SIZES:
echo ───────────────────────────────────────────────────────────
for %%f in (gui\ultron_enhanced\web\index.html gui\ultron_enhanced\web\app.js gui\ultron_enhanced\web\styles.css) do (
    if exist "%%f" (
        for %%s in ("%%f") do echo   %%~nxf: %%~zs bytes
    ) else (
        echo   %%~nxf: MISSING!
    )
)
echo.

echo [2] FILE ATTRIBUTES:
echo ───────────────────────────────────────────────────────────
attrib gui\ultron_enhanced\web\index.html 2>nul || echo   index.html: NOT FOUND
attrib gui\ultron_enhanced\web\app.js 2>nul || echo   app.js: NOT FOUND
attrib gui\ultron_enhanced\web\styles.css 2>nul || echo   styles.css: NOT FOUND
echo.

echo [3] RECENT BACKUPS:
echo ───────────────────────────────────────────────────────────
if exist "gui\ultron_enhanced\web\backups" (
    dir /b /od "gui\ultron_enhanced\web\backups" 2>nul | findstr /r "^20" || echo   No backups found
) else (
    echo   Backup directory not found
)
echo.

echo [4] GIT STATUS:
echo ───────────────────────────────────────────────────────────
git status --short gui/ultron_enhanced/web/ 2>nul || echo   Git not available
echo.

echo [5] INTEGRITY CHECK:
echo ───────────────────────────────────────────────────────────
python monitor_gui.py 2>nul || echo   Run: python monitor_gui.py --save
echo.

echo ═══════════════════════════════════════════════════════════
echo   Health check complete
echo ═══════════════════════════════════════════════════════════
echo.
pause
