@echo off
REM Fix CMD/PowerShell Admin Requirement
REM This script removes admin requirements from console shortcuts

echo Fixing command console access...
echo.

REM Create new CMD shortcut without admin requirement
echo [+] Creating new CMD shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$link = $ws.CreateShortcut('%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\Command Prompt.lnk'); " ^
  "$link.TargetPath = 'C:\Windows\System32\cmd.exe'; " ^
  "$link.WorkingDirectory = '%%USERPROFILE%%'; " ^
  "$link.Save()"

REM Create new PowerShell shortcut without admin requirement
echo [+] Creating new PowerShell shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$link = $ws.CreateShortcut('%%ProgramData%%\Microsoft\Windows\Start Menu\Programs\Windows PowerShell.lnk'); " ^
  "$link.TargetPath = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'; " ^
  "$link.WorkingDirectory = '%%USERPROFILE%%'; " ^
  "$link.Save()"

echo.
echo [✓] Command console shortcuts fixed!
echo [*] Please close and reopen Windows Terminal/CMD/PowerShell
echo.
pause
