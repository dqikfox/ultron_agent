# ============================================================
# CMD RESTRICTION ROOT CAUSE FINDER
# ============================================================
# This script finds WHY CMD/PowerShell require admin on this profile
# but work on other profiles and as admin
# ============================================================

Write-Host "`n========== CMD/PowerShell Restriction Analyzer ==========" -ForegroundColor Cyan
Write-Host "Current User: $(whoami)" -ForegroundColor Yellow
Write-Host "Profile: $env:USERPROFILE`n" -ForegroundColor Yellow

$issues = @()

# ============================================================
# 1. CHECK USER-LEVEL POLICIES
# ============================================================
Write-Host "[1] Checking User-Level Group Policies..." -ForegroundColor Magenta
$userPolicies = Get-Item -Path "HKCU:\Software\Policies" -ErrorAction SilentlyContinue
if ($userPolicies) {
    Get-ChildItem -Path "HKCU:\Software\Policies" -Recurse | ForEach-Object {
        if ($_.PSChildName -like "*shell*" -or $_.PSChildName -like "*cmd*" -or $_.PSChildName -like "*powershell*") {
            Write-Host "  ⚠️  Found policy: $($_.FullName)" -ForegroundColor Yellow
            $issues += "User policy found: $($_.FullName)"
        }
    }
}

# ============================================================
# 2. CHECK UAC POLICY FOR USER
# ============================================================
Write-Host "`n[2] Checking UAC Policy..." -ForegroundColor Magenta
$uacPolicy = Get-Item "HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\System" -ErrorAction SilentlyContinue
if ($uacPolicy) {
    $uacProps = $uacPolicy | Get-ItemProperty
    Write-Host "  UAC Settings: $($uacProps | Format-Table -AutoSize | Out-String)"
    if ($uacProps.PSObject.Properties | Where-Object { $_.Value -eq 1 }) {
        $issues += "UAC restriction found in user policy"
    }
}

# ============================================================
# 3. CHECK IF CMD IS BLOCKED VIA DENY ACE
# ============================================================
Write-Host "`n[3] Checking CMD.EXE Deny Permissions..." -ForegroundColor Magenta
$cmdAcl = (Get-Acl "C:\Windows\System32\cmd.exe").Access
$denies = $cmdAcl | Where-Object { $_.AccessControlType -eq "Deny" }
if ($denies) {
    Write-Host "  ⚠️  DENY rules found on cmd.exe:" -ForegroundColor Red
    $denies | ForEach-Object {
        Write-Host "    - $($_.IdentityReference): $($_.FileSystemRights)" -ForegroundColor Red
        $issues += "DENY ACE on cmd.exe: $($_.IdentityReference)"
    }
} else {
    Write-Host "  ✓ No DENY rules on cmd.exe" -ForegroundColor Green
}

# ============================================================
# 4. CHECK USER ENVIRONMENT VARIABLES FOR RESTRICTIONS
# ============================================================
Write-Host "`n[4] Checking Environment Variable Restrictions..." -ForegroundColor Magenta
$badEnvVars = Get-ChildItem -Path "HKCU:\Environment" -ErrorAction SilentlyContinue |
    Get-ItemProperty |
    Where-Object { $_.PSObject.Properties.Name | Where-Object { $_ -like "*cmd*" -or $_ -like "*shell*" -or $_ -like "*powershell*" } }
if ($badEnvVars) {
    Write-Host "  ⚠️  Suspicious environment variables:" -ForegroundColor Yellow
    $badEnvVars | Format-Table -AutoSize
    $issues += "Suspicious environment variables found"
}

# ============================================================
# 5. CHECK FILE TYPE ASSOCIATION
# ============================================================
Write-Host "`n[5] Checking CMD File Association..." -ForegroundColor Magenta
$cmdAssoc = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.cmd\UserChoice" -ErrorAction SilentlyContinue
if ($cmdAssoc) {
    Write-Host "  ⚠️  User-specific .cmd association found (may be overriding system default)" -ForegroundColor Yellow
    $issues += "User override for .cmd file association"
}

# ============================================================
# 6. CHECK REGISTRY FOR HIDDEN AUTORUN BLOCKING
# ============================================================
Write-Host "`n[6] Checking for AutoRun Blocks..." -ForegroundColor Magenta
$autorun = Get-Item "HKCU:\Software\Microsoft\Command Processor" -ErrorAction SilentlyContinue
if ($autorun) {
    $props = $autorun | Get-ItemProperty
    if ($props.AutoRun) {
        Write-Host "  AutoRun value: $($props.AutoRun)" -ForegroundColor Cyan
    }
}

# ============================================================
# 7. CHECK IF PROCESS CREATION IS BLOCKED
# ============================================================
Write-Host "`n[7] Checking Process Creation Policy..." -ForegroundColor Magenta
$procPolicy = Get-Item "HKCU:\Software\Policies\Microsoft\Windows\Safer" -ErrorAction SilentlyContinue
if ($procPolicy) {
    Write-Host "  ⚠️  Windows Safer policy found (may block processes)" -ForegroundColor Yellow
    Get-ChildItem "HKCU:\Software\Policies\Microsoft\Windows\Safer" -Recurse | ForEach-Object {
        Write-Host "    - $($_.FullName)" -ForegroundColor Yellow
        $issues += "Safer policy: $($_.FullName)"
    }
} else {
    Write-Host "  ✓ No Windows Safer policy" -ForegroundColor Green
}

# ============================================================
# 8. CHECK MACHINE-LEVEL POLICIES (visible to user)
# ============================================================
Write-Host "`n[8] Checking Machine-Level Policies..." -ForegroundColor Magenta
$machineDisable = Get-ItemProperty "HKLM:\Software\Policies\Microsoft\Windows\System" -Name "DisableCMD" -ErrorAction SilentlyContinue
if ($machineDisable -and $machineDisable.DisableCMD -ne 0) {
    Write-Host "  ⚠️  DisableCMD is set at machine level: $($machineDisable.DisableCMD)" -ForegroundColor Red
    $issues += "DisableCMD set at machine level"
}

# ============================================================
# 9. TEST: TRY RUNNING CMD
# ============================================================
Write-Host "`n[9] Testing CMD Execution..." -ForegroundColor Magenta
try {
    $testCmd = & cmd /c "echo test" 2>&1
    if ($testCmd -eq "test") {
        Write-Host "  ✓ CMD executed successfully in this session" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  CMD execution returned unexpected output" -ForegroundColor Yellow
        $issues += "CMD execution returned unexpected output: $testCmd"
    }
} catch {
    Write-Host "  ❌ CMD execution failed: $($_.Exception.Message)" -ForegroundColor Red
    $issues += "CMD execution error: $($_.Exception.Message)"
}

# ============================================================
# SUMMARY
# ============================================================
Write-Host "`n========== ANALYSIS SUMMARY ==========" -ForegroundColor Cyan

if ($issues.Count -eq 0) {
    Write-Host "`n✓ NO ISSUES FOUND in policies/permissions" -ForegroundColor Green
    Write-Host "`nThe restriction may be caused by:" -ForegroundColor Yellow
    Write-Host "  1. AMAZON Q UGS CLI INSTALLATION - May have set permissions" -ForegroundColor Yellow
    Write-Host "  2. Software restriction policy via AMAZON Q diagnostics" -ForegroundColor Yellow
    Write-Host "  3. Windows Terminal profile settings for this user" -ForegroundColor Yellow
    Write-Host "  4. User account control (UAC) elevation settings" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ FOUND $($issues.Count) POTENTIAL ISSUES:" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host "  • $_" -ForegroundColor Red }
}

# ============================================================
# COMPARISON: Check other user profiles
# ============================================================
Write-Host "`n========== CHECKING OTHER USER PROFILES ==========" -ForegroundColor Cyan
$users = Get-ChildItem "C:\Users" | Where-Object { $_.Name -notlike "*$" -and $_.Name -notin @("Public", "All Users", "Default", "Default User") }
Write-Host "Other user profiles on system:" -ForegroundColor Yellow
$users | ForEach-Object {
    Write-Host "  • $($_.Name)" -ForegroundColor Cyan
}

Write-Host "`n[✓] Run CMD on another profile to verify it works there." -ForegroundColor Green
Write-Host "[✓] If it works on another profile, this is a USER-PROFILE-SPECIFIC restriction." -ForegroundColor Green

Write-Host "`n========== SCRIPT COMPLETE ==========" -ForegroundColor Cyan
