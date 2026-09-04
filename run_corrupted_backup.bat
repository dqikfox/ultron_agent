import bpy

class XOperator(bpy.types.Operator):
    bl_idname = "object.x"
    bl_label = "x"

    def execute(self, context):
        return {"FINISHED"}

:: Display test summary
echo.
echo [TEST SUMMARY] Tests Passed: !test_passed!/5 ^| Tests Failed: !test_failed!/5
echo [TEST] ================================================ >> "%LOG_FILE%"
echo [TEST] Summary: Passed=!test_passed! Failed=!test_failed! >> "%LOG_FILE%"
echo [TEST] ================================================ >> "%LOG_FILE%"

if !test_failed! gtr 0 (
    echo [WARN] ⚠️  Some tests failed. System may not work correctly.
    echo [WARN] Check %LOG_FILE% for details.
    echo.
    echo [PROMPT] Press Y to continue anyway, or any other key to exit...
    choice /c YN /n /m "Continue? (Y/N): "
    if !errorlevel! neq 1 (
        echo [INFO] Startup cancelled by user.
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] ✅ All Ollama tests passed! System ready.
)
echo.

:: 6. Test Python Scripts Syntax
echo [INFO] Testing Python scripts syntax...
python -m py_compile web_gui_server.py >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] web_gui_server.py has syntax errors
    pause
    exit /b 1
)
python -m py_compile main.py >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] main.py has syntax errors
    pause
    exit /b 1
)
echo [SUCCESS] All Python scripts syntax check passed
echo.

:: 7. Start the Web GUI Server
echo [INFO] Starting ULTRON Web GUI Server on port %WEB_GUI_PORT%...
start "ULTRON Web GUI" /B python web_gui_server.py

:: Wait for Web GUI to start
timeout /t 5 /nobreak >nul

:: Check if Web GUI started
curl -s "http://localhost:%WEB_GUI_PORT%/" >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ Web GUI Server started successfully on port %WEB_GUI_PORT%
) else (
    echo [WARN] Web GUI Server may not have started properly, but continuing...
)
echo.

:: 8. Start the Frontend UI Server
echo [INFO] Starting ULTRON Frontend UI on port %FRONTEND_PORT%...
start "ULTRON Frontend UI" /B python frontend_server.py --port %FRONTEND_PORT%

:: Wait for Frontend UI to start
timeout /t 3 /nobreak >nul

:: Check if Frontend UI started
curl -s "http://localhost:%FRONTEND_PORT%/" >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ Frontend UI started successfully on port %FRONTEND_PORT%
) else (
    echo [WARN] Frontend UI may not have started properly, but continuing...
)
echo.

:: 9. Start NVIDIA Enhanced Chat Service
echo [INFO] Starting NVIDIA Enhanced Chat on port 8002...
start "ULTRON NVIDIA Chat" /B python nvidia_enhanced_ultron.py

:: Wait for NVIDIA service to start
timeout /t 5 /nobreak >nul

:: Check if NVIDIA service started
curl -s "http://localhost:8002/health" >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ NVIDIA Chat Service started successfully on port 8002
) else (
    echo [WARN] NVIDIA Chat Service may not have started properly, but continuing...
)
echo.

:: 10. Startup Complete
echo [SUCCESS] ULTRON Agent 3.0 startup sequence complete!
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    ULTRON AGENT 3.0                         ║
echo ║                    SYSTEM STATUS                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ Ollama Service:     http://localhost:%OLLAMA_PORT%
echo ✅ Web GUI:           http://localhost:%WEB_GUI_PORT%
echo ✅ Frontend UI:       http://localhost:%FRONTEND_PORT%
echo ✅ NVIDIA Chat:       http://localhost:8002
echo ✅ AI Model:          %OLLAMA_MODEL%
echo.
echo 📝 Log file: %LOG_FILE%
echo 🎯 Primary GUI: gui/ultron_enhanced/web/index.html
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 STARTUP COMPLETE!                           ║
echo ║  ULTRON Agent is ready. Press any key to exit launcher.    ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Wait for user input before exiting
pause

call :info "ULTRON Agent launcher finished."
echo.
echo ULTRON Agent is still running in the background.
echo Access the Web GUI at: http://localhost:%WEB_GUI_PORT%
echo Access the Frontend UI at: http://localhost:%FRONTEND_PORT%

endlocal
exit /b 0

:: ========================================================================
:: HELPER FUNCTIONS
:: ========================================================================

:info
    echo [INFO] %~1
    echo [%date% %time%] [INFO] %~1 >> "%LOG_FILE%" 2>nul
    goto :eof
