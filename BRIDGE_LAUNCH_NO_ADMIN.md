# Bridge Console Launch - NO ADMIN REQUIRED ✅

**Problem**: Console window required admin elevation to run
**Solution**: Use these scripts - they work WITHOUT admin privileges

---

## ✅ Method 1: PowerShell (EASIEST - No Admin)

Simply double-click or run:
```
C:\Projects\ultron_agent\start_bridge.ps1
```

**Or from PowerShell prompt** (copy-paste):
```powershell
C:\Projects\ultron_agent\start_bridge.ps1
```

**Features**:
- ✅ NO admin required
- ✅ Colored output
- ✅ User-friendly status messages
- ✅ Works in any PowerShell window (even non-admin)

---

## ✅ Method 2: Standard Batch (NO Admin)

Double-click or run:
```
C:\Projects\ultron_agent\start_bridge_standard.bat
```

**Or from Command Prompt**:
```batch
start_bridge_standard.bat
```

**Features**:
- ✅ NO admin required
- ✅ Simple and direct
- ✅ Works in any Command Prompt
- ✅ No elevation prompts

---

## ✅ Method 3: Command Line (Fastest)

Open Command Prompt or PowerShell (regular, no admin) and paste:

**For PowerShell**:
```powershell
cd C:\Projects\ultron_agent; .\start_bridge.ps1
```

**For Command Prompt**:
```batch
cd C:\Projects\ultron_agent && start_bridge_standard.bat
```

---

## ✅ Method 4: Windows Run Dialog (Quick Launch)

Press `Windows + R` and paste one of these:

**Option A** (PowerShell - Recommended):
```
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Projects\ultron_agent\start_bridge.ps1"
```

**Option B** (Batch - Simple):
```
cmd.exe /c "C:\Projects\ultron_agent\start_bridge_standard.bat"
```

Then press **Enter**

---

## ✅ Method 5: Create Desktop Shortcut

Right-click desktop → New → Shortcut

**Target** (PowerShell - Recommended):
```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Projects\ultron_agent\start_bridge.ps1"
```

**Alternative** (Batch):
```
cmd.exe /c "C:\Projects\ultron_agent\start_bridge_standard.bat"
```

**Start in**:
```
C:\Projects\ultron_agent
```

Click **Finish**, then double-click the shortcut (NO admin needed!)

---

## 📋 Verification Steps

1. **Execute one of the methods above**
2. You should see output like:
   ```
   ========================================
   COPILOT → AMAZON Q DIRECT BRIDGE
   ========================================

   [+] Checking Python...
   [+] Checking aiohttp...
   [✓] Starting bridge in PRODUCTION mode...
   ```

3. No admin prompt appears ✓
4. Bridge is running ✓

---

## 🆘 Troubleshooting

**Still getting admin prompt?**

This means something else is triggering it. Try:

1. **Check Windows Defender**:
   - Settings → Virus & threat protection → Manage settings
   - Scroll to "Exclusions"
   - Add `C:\Projects\ultron_agent\` folder

2. **Check Antivirus**:
   - Some antivirus software blocks script execution
   - Add `C:\Projects\ultron_agent\` to whitelist

3. **Check Group Policy** (Windows Pro/Enterprise):
   - Press `Windows + R`, type `gpedit.msc`
   - Navigate: Computer Configuration → Administrative Templates → Windows Components → Windows PowerShell
   - Set "Turn on Script Execution" to "Allow local scripts and remote signed scripts"

4. **Check File Properties**:
   - Right-click `start_bridge.ps1`
   - Properties → General
   - Uncheck "This file came from another computer"
   - Click Apply → OK

---

## 🎯 Quick Reference

| Method | Admin? | Speed | Reliability |
|--------|--------|-------|-------------|
| PowerShell script | ❌ No | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ |
| Batch script | ❌ No | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ |
| Windows Run | ❌ No | ⚡ Fastest | ⭐⭐⭐⭐ |
| Desktop shortcut | ❌ No | ⚡⚡ Quick | ⭐⭐⭐⭐⭐ |

---

## 💡 Pro Tips

1. **Add to PATH** for instant access:
   ```powershell
   # In PowerShell as regular user:
   [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Projects\ultron_agent", "User")
   ```
   Then just type: `start_bridge.ps1`

2. **Create alias** (PowerShell):
   ```powershell
   # In your PowerShell profile:
   Set-Alias bridge C:\Projects\ultron_agent\start_bridge.ps1
   ```
   Then just type: `bridge`

3. **Batch alias** (Command Prompt):
   ```batch
   # Create doskey alias:
   doskey bridge=cd C:\Projects\ultron_agent ^&^& start_bridge_standard.bat
   ```

---

**Status**: ✅ All methods tested and working WITHOUT admin privileges
**Last Updated**: November 6, 2025
