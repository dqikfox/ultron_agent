@echo off
echo Fixing Windows Terminal crash...
echo.
echo Disabling Windows Terminal as default...
reg add "HKCU\Console\%%Startup" /v DelegationConsole /t REG_SZ /d "{00000000-0000-0000-0000-000000000000}" /f
reg add "HKCU\Console\%%Startup" /v DelegationTerminal /t REG_SZ /d "{00000000-0000-0000-0000-000000000000}" /f
echo.
echo Done. CMD and PowerShell will now use legacy console.
echo Press Win+R and type "cmd" - it should work now.
pause
