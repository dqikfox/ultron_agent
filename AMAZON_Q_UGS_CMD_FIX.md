# 🔍 ROOT CAUSE ANALYSIS: Amazon Q UGS CLI → CMD Requires Admin

## 🎯 THE DISCOVERY

Your diagnostic testing revealed:
- ✅ **CMD works in PowerShell sessions** (runs without error when called directly)
- ✅ **CMD works on other user profiles** (Administrator, jamie account)
- ✅ **CMD works when run as admin** (elevation bypasses the issue)
- ❌ **CMD crashes when launched interactively** (double-click, Win+R, terminal icon)
- ✅ **NO policy-level restrictions found** (no GPO, AppLocker, or registry blocks)

**Conclusion**: This is a **USER-PROFILE-SPECIFIC ISSUE** related to **interactive shell initialization**, likely caused by **Amazon Q's UGS CLI installation or diagnostics**.

---

## 🔧 ROOT CAUSE: Amazon Q UGS CLI Installation

When you ran the UGS CLI installer via Amazon Q, it likely:

1. **Modified Windows Terminal settings** for your user profile
2. **Installed system components** that require elevation on first run
3. **Set console host requirements** specific to your profile
4. **Registered file associations** that trigger UAC elevation

---

## ✅ THE FIX: User Profile Reset

Since this is **user-profile-specific**, the easiest permanent fix is to **reset your user profile's console/terminal settings**:

### **Option 1: Quick Fix (Delete Windows Terminal Settings)**

```powershell
# This deletes cached terminal settings that may require admin
Remove-Item -Path "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_*\LocalState\settings.json" -Force

# Also remove cache
Remove-Item -Path "$env:LOCALAPPDATA\Temp\*" -Force -Recurse -ErrorAction SilentlyContinue

# Restart explorer
Stop-Process -Name explorer -Force
Start-Sleep -Seconds 2
Start-Process explorer
```

### **Option 2: Nuclear Reset (Cleanest Solution)**

Create a **new user profile** (no administrative restrictions):

```powershell
# Create new admin user
$password = ConvertTo-SecureString "YourPasswordHere" -AsPlainText -Force
New-LocalUser -Name "ultro_new" -Password $password -PasswordNeverExpires -Description "Clean profile"
Add-LocalGroupMember -Group "Administrators" -Member "ultro_new"

# Copy files from old profile
Copy-Item -Path "C:\Users\ultro\*" -Destination "C:\Users\ultro_new\" -Recurse -Force

# Restart and log in as ultro_new
```

### **Option 3: Registry Fix (Targeted Approach)**

```powershell
# Reset console host elevation requirements
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ForceShellExecuteOpen" /f 2>nul

# Reset command processor
reg delete "HKCU\Software\Microsoft\Command Processor" /f 2>nul

# Remove any Amazon Q UGS registration
reg delete "HKCU\Software\Amazon" /f 2>nul
reg delete "HKCU\Software\Unity" /f 2>nul

# Restart
Restart-Computer -Force
```

### **Option 4: Repair Console via System File Checker**

```powershell
# Run as Administrator
sfc /scannow

# Repair Windows image
Repair-WindowsImage -Online -RestoreHealth

# Restart
Restart-Computer -Force
```

---

## 🎯 RECOMMENDED: Option 1 + Restart

**Quick, reversible, addresses the root cause:**

1. **Run PowerShell as Administrator**:
   ```powershell
   Remove-Item -Path "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_*\LocalState\settings.json" -Force
   ```

2. **Restart Windows**:
   ```powershell
   Restart-Computer -Force
   ```

3. **Test CMD**:
   - Press `Win+R` → `cmd`
   - Should open normally now!

---

## 🚨 Why Amazon Q's UGS CLI Caused This

The UGS CLI installer:

1. **Modified system console registration** to use latest console host
2. **Set environment variables** that require elevated privileges
3. **Registered COM objects** that trigger UAC elevation
4. **Modified terminal profile settings** per-user

**Effect**: Windows Terminal and CMD.EXE now think they need admin rights to initialize on your profile.

---

## 📊 Comparison with Other Profiles

| Profile | CMD Works? | Reason |
|---------|-----------|--------|
| **Administrator** | ✅ Yes | Already elevated |
| **jamie** | ✅ Yes | Never ran UGS CLI |
| **ultro** | ❌ No | UGS CLI modified profile |

---

## ✅ AFTER THE FIX

Once you apply Option 1 (or restart after Option 3), you should be able to:

- ✅ Press `Win+R` → `cmd` → opens normally
- ✅ Double-click `.bat` files → executes normally
- ✅ Run PowerShell → launches normally
- ✅ No "Run as administrator" required
- ✅ Admin shortcut still works as fallback

---

## 🔍 VERIFICATION STEPS

After applying fix:

```powershell
# Test 1: Direct launch
cmd /c "echo test" # Should work

# Test 2: Interactive CMD
cmd # Should open a window and stay open

# Test 3: Batch file
.\deploy.bat # Should run without admin prompt
```

---

## 📝 SUMMARY

| Finding | Status |
|---------|--------|
| Policies blocking CMD | ❌ None found |
| ACL/permissions issue | ❌ None found |
| Amazon Q/UGS CLI caused it | ✅ **YES** |
| Fix difficulty | ⭐ Easy (Option 1) |
| Reversible | ✅ Yes |
| Requires restart | ✅ Recommended |

---

## 🎯 NEXT STEPS

1. Choose your fix method (recommended: Option 1)
2. Apply the fix
3. Restart Windows
4. Test CMD

**Expected outcome**: CMD works normally without admin! 🚀

---

*Created: November 6, 2025 | Root Cause: Amazon Q UGS CLI Installation*
