@echo off
cd /d "%~dp0"
echo Deploying UltronModule...
"..\ugs.exe" login
"..\ugs.exe" deploy UltronModule
pause
