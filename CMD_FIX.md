# CMD Console Crash Fix

## Issue
CMD opens then immediately closes when launched interactively.

## Root Cause
Windows Console Host or Terminal configuration issue.

## Solutions

### Option 1: Use PowerShell (Recommended)
```powershell
# Open PowerShell instead
start powershell

# Or run commands directly
powershell -NoExit -Command "cd C:\Projects\ultron_agent"
```

### Option 2: Reset Windows Terminal
```powershell
# Reset Windows Terminal settings
Get-AppxPackage *WindowsTerminal* | Reset-AppxPackage
```

### Option 3: Use CMD with /K flag
```batch
# Keep CMD open after execution
cmd /k "cd C:\Projects\ultron_agent"
```

### Option 4: Check Windows Console Host
```powershell
# Repair system files
sfc /scannow
```

## For UGS Deployment
Use PowerShell instead:
```powershell
cd C:\Projects\ultron_agent
.\ugs.exe login
cd unity_cloud_code
..\ugs.exe deploy UltronModule
```
