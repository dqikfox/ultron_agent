@echo off
echo ═══════════════════════════════════════════════════════════════════
echo   🚀 ULTRON AGENT STREAMLINING TOOL
echo ═══════════════════════════════════════════════════════════════════
echo.
echo This will audit, fix, and visualize your entire ULTRON system.
echo.
echo What it does:
echo   1. Scans all 500+ files
echo   2. Finds disconnected components
echo   3. Auto-fixes integration issues
echo   4. Creates visual architecture map
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" goto end

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   STEP 1/3: SYSTEM AUDIT
echo ═══════════════════════════════════════════════════════════════════
echo.
python SYSTEM_AUDIT_AND_FIX.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Audit failed! Check Python installation.
    pause
    goto end
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   STEP 2/3: AUTO-FIX ISSUES
echo ═══════════════════════════════════════════════════════════════════
echo.
python SYSTEM_INTEGRATION_FIX.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Some fixes may have failed. Check output above.
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   STEP 3/3: VISUALIZE ARCHITECTURE
echo ═══════════════════════════════════════════════════════════════════
echo.
python COMPONENT_MAPPER.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Visualization may have failed. Check output above.
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   ✅ STREAMLINING COMPLETE!
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Files created:
echo   📄 SYSTEM_AUDIT_REPORT.json - Detailed audit results
echo   📄 SYSTEM_ARCHITECTURE.md - Visual component diagram
echo   📄 CONNECTION_MATRIX.txt - Connection details
echo   📄 ultron_integration_layer.py - Unified integration
echo   📄 component_registry.py - Component registry
echo.
echo Next steps:
echo   1. Review SYSTEM_AUDIT_REPORT.json
echo   2. Check SYSTEM_ARCHITECTURE.md for visual map
echo   3. Test system: python main.py
echo   4. Read STREAMLINE_ULTRON.md for details
echo.
echo Open architecture diagram now? (Y/N)
set /p open="Choice: "
if /i "%open%"=="Y" notepad SYSTEM_ARCHITECTURE.md

:end
echo.
echo ═══════════════════════════════════════════════════════════════════
pause
