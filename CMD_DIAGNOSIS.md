# CMD Crash Diagnosis

## Issue
CMD opens then immediately closes, only works with admin rights.

## Root Cause
Windows user profile corruption or console host registry issue.

## Fix

Run this in PowerShell (no admin needed):
```powershell
# Check if there's a startup script causing crash
$env:COMSPEC
Get-ItemProperty "HKCU:\Console" -ErrorAction SilentlyContinue
```

## Workaround
Use Windows Terminal or PowerShell instead:
```powershell
# Install Windows Terminal from Microsoft Store
# Or use PowerShell for all commands
```

## For UGS Deployment
```powershell
cd C:\Projects\ultron_agent
.\ugs.exe login
cd unity_cloud_code
..\ugs.exe deploy UltronModule
```
