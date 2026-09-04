@echo off
echo ═══════════════════════════════════════════════════════════
echo   ULTRON GUI PROTECTION - ENABLE
echo ═══════════════════════════════════════════════════════════
echo.
echo Making GUI files READ-ONLY...
echo.

attrib +r "gui\ultron_enhanced\web\index.html" 2>nul && echo ✓ Protected: index.html || echo ✗ Failed: index.html
attrib +r "gui\ultron_enhanced\web\app.js" 2>nul && echo ✓ Protected: app.js || echo ✗ Failed: app.js
attrib +r "gui\ultron_enhanced\web\styles.css" 2>nul && echo ✓ Protected: styles.css || echo ✗ Failed: styles.css

echo.
echo ═══════════════════════════════════════════════════════════
echo   GUI files are now PROTECTED from accidental modification
echo   To edit: Run unprotect_gui.bat first
echo ═══════════════════════════════════════════════════════════
echo.
