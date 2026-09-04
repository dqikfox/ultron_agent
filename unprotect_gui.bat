@echo off
echo ═══════════════════════════════════════════════════════════
echo   ULTRON GUI PROTECTION - DISABLE
echo ═══════════════════════════════════════════════════════════
echo.
echo Making GUI files EDITABLE...
echo.

attrib -r "gui\ultron_enhanced\web\index.html" 2>nul && echo ✓ Unprotected: index.html || echo ✗ Failed: index.html
attrib -r "gui\ultron_enhanced\web\app.js" 2>nul && echo ✓ Unprotected: app.js || echo ✗ Failed: app.js
attrib -r "gui\ultron_enhanced\web\styles.css" 2>nul && echo ✓ Unprotected: styles.css || echo ✗ Failed: styles.css

echo.
echo ═══════════════════════════════════════════════════════════
echo   GUI files are now EDITABLE
echo   ⚠ REMEMBER: Run protect_gui.bat after editing!
echo ═══════════════════════════════════════════════════════════
echo.
