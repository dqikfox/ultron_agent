# Intel Graphics Driver Crash Fix

## Problem
Windows Terminal crashes due to corrupted Intel driver: `igd10um64xe.DLL`
Exception: 0xc0000005 (Access Violation)

## Fix Options

### Option 1: Update Intel Driver (Recommended)
1. Go to: https://www.intel.com/content/www/us/en/download-center/home.html
2. Download latest Intel Graphics Driver
3. Install and restart

### Option 2: Use Device Manager
1. Win+X → Device Manager
2. Display adapters → Intel Graphics
3. Right-click → Update driver → Search automatically

### Option 3: Rollback Driver
1. Win+X → Device Manager
2. Display adapters → Intel Graphics
3. Right-click → Properties → Driver tab → Roll Back Driver

### Temporary Workaround
Use legacy console (already working in admin mode):
- Right-click CMD shortcut → Properties → Uncheck "Use Windows Terminal"
