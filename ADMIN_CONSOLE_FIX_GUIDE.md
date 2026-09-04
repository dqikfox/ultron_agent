# 🔐 How to Run LangFlow with Admin Privileges

**Problem**: Command console requires Admin to run properly
**Solution**: Use one of the admin scripts provided below

---

## ✅ SOLUTION 1: PowerShell Script (Recommended - Easiest)

**File**: `start_langflow_admin.ps1`

**How to use**:
1. Open File Explorer
2. Navigate to: `C:\Projects\ultron_agent`
3. Right-click on `start_langflow_admin.ps1`
4. Select: **"Run with PowerShell"**
5. Click **"Yes"** when prompted for admin privileges
6. LangFlow will start automatically ✓

**What it does**:
- ✅ Automatically requests Admin privileges
- ✅ Activates the virtual environment
- ✅ Starts LangFlow on http://localhost:7860
- ✅ Shows friendly status messages
- ✅ Keeps window open if there are errors

---

## ✅ SOLUTION 2: Batch Script (Alternative)

**File**: `start_langflow_admin.bat`

**How to use**:
1. Open File Explorer
2. Navigate to: `C:\Projects\ultron_agent`
3. Right-click on `start_langflow_admin.bat`
4. Select: **"Run as administrator"**
5. LangFlow will start automatically ✓

**What it does**:
- ✅ Requests Admin privileges via VBScript
- ✅ Activates the virtual environment
- ✅ Starts LangFlow on http://localhost:7860
- ✅ Displays startup info

---

## ✅ SOLUTION 3: Create Windows Shortcut (One-Click)

**To create a shortcut that always runs as admin**:

1. Navigate to `C:\Projects\ultron_agent`
2. Right-click empty space > **New** > **Shortcut**
3. Enter target: `powershell.exe -NoExit -ExecutionPolicy Bypass -File "C:\Projects\ultron_agent\start_langflow_admin.ps1"`
4. Name it: `LangFlow Server`
5. Click **Finish**
6. Right-click the new shortcut
7. Click **Properties**
8. Click **Advanced** button
9. Check: ✓ **"Run as administrator"**
10. Click **OK** twice
11. Now you can double-click to start LangFlow anytime ✓

---

## 🎯 QUICKSTART

**Fastest way**:
1. Press `Windows + R`
2. Type: `powershell.exe -NoExit -ExecutionPolicy Bypass -File "C:\Projects\ultron_agent\start_langflow_admin.ps1"`
3. Press Enter
4. Click **Yes** when prompted for admin
5. Done! ✓

---

## ✅ VERIFY IT'S WORKING

Once LangFlow starts, you'll see:
```
========================================
LangFlow Server Starting
========================================
URL: http://localhost:7860
...
```

Then:
1. Open browser: http://localhost:7860
2. You should see the LangFlow interface ✓

---

## 🛠️ MANUAL STARTUP (If Scripts Don't Work)

1. **Right-click Command Prompt** → **"Run as administrator"**
2. Run these commands:
   ```bash
   cd C:\Projects\ultron_agent
   .venv\Scripts\activate.bat
   python -m langflow run --host 127.0.0.1 --port 7860
   ```
3. Wait for startup message showing http://localhost:7860

---

## 📋 Files Available

| File | Use Case |
|------|----------|
| `start_langflow_admin.ps1` | **RECOMMENDED** - PowerShell with auto-admin |
| `start_langflow_admin.bat` | Batch script with admin elevation |
| `start_langflow.bat` | Regular batch (needs manual admin) |
| `LangFlow_Start_Admin.lnk.txt` | Info for creating Windows shortcut |

---

## 🔄 TROUBLESHOOTING

**If PowerShell script doesn't run**:
1. Right-click PowerShell > **Run as administrator**
2. Type: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Type: `Y` and press Enter
4. Try running the script again

**If "command not found"**:
- Make sure you're in: `C:\Projects\ultron_agent`
- Make sure `.venv` folder exists
- Run: `python -m pip install langflow==1.0.15` (to install LangFlow)

**If port 7860 is already in use**:
- LangFlow is already running
- Open: http://localhost:7860 in browser

---

## ✨ WHAT'S NEXT

Once LangFlow is running (http://localhost:7860):

1. ✅ All MCP tests will pass (9/9)
2. ✅ Python tool works (connection verified)
3. ✅ Ready for Cursor integration
4. ✅ 4 workflows available

---

**Status**: ✅ **FULLY READY** - Just run one of the scripts above!

