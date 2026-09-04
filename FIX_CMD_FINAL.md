# CMD Requires Admin - Final Fix

Your Windows installation has cmd.exe requiring elevation. This is a Windows system corruption.

## Quick Fix
Win+R → Type: `%windir%\System32\cmd.exe`

## Permanent Fix
1. Download: https://www.microsoft.com/en-us/software-download/windows10
2. Run "Update now" to repair Windows system files
3. Or use: `DISM /Online /Cleanup-Image /RestoreHealth`

## Workaround
Use PowerShell instead - it works fine.
Win+R → Type: `powershell`
