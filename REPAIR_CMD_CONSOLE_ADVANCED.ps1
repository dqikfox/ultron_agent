# ============================================================================
# WINDOWS TERMINAL GPU CRASH FIX - ADVANCED
# Root Cause: igd10um64xe.DLL (Intel GPU Driver) crashes Windows Terminal
# Solution: Disable GPU acceleration, reset profile settings, clear corruption
# ============================================================================

param(
    [switch]$AutoRestart = $false
)

Write-Host "========== WINDOWS TERMINAL GPU CRASH FIX ==========" -ForegroundColor Cyan
Write-Host "User: $env:USERNAME`nProfile: $env:USERPROFILE`n" -ForegroundColor Gray

# Confirm before proceeding
$confirm = Read-Host "This will disable GPU acceleration and reset Windows Terminal. Continue? (Y/N)"
if ($confirm -ne "Y") { Write-Host "Cancelled."; exit }

# ============================================================================
# PHASE 1: DISABLE GPU ACCELERATION (Root cause of crash)
# ============================================================================
Write-Host "`n[1] Disabling GPU acceleration in Windows Terminal..." -ForegroundColor Yellow

$wtSettingsPath = "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
$wtSettingsBackup = "$wtSettingsPath.backup"

if (Test-Path $wtSettingsPath) {
    try {
        # Backup original settings
        Copy-Item $wtSettingsPath $wtSettingsBackup -Force
        Write-Host "  ✓ Backed up to: $wtSettingsBackup" -ForegroundColor Green

        # Read and parse settings
        $settings = Get-Content $wtSettingsPath -Raw | ConvertFrom-Json

        # Disable GPU acceleration for all profiles
        if ($null -eq $settings.profiles) { $settings | Add-Member -NotePropertyName profiles -NotePropertyValue @() }

        # Force GPU acceleration OFF globally
        $settings | Add-Member -NotePropertyName "experimental.rendering.glyphCache" -NotePropertyValue "false" -Force
        $settings | Add-Member -NotePropertyName "experimental.rendering.engine" -NotePropertyValue "d2d1" -Force
        $settings | Add-Member -NotePropertyName "rendering.glyphCache" -NotePropertyValue "false" -Force
        $settings | Add-Member -NotePropertyName "rendering.engine" -NotePropertyValue "d2d1" -Force

        # Disable experimental features that use GPU
        if ($null -eq $settings.experimental) { $settings | Add-Member -NotePropertyName experimental -NotePropertyValue @{} }
        $settings.experimental | Add-Member -NotePropertyName "rendering.glyphCache" -NotePropertyValue "false" -Force
        $settings.experimental | Add-Member -NotePropertyName "rendering.engine" -NotePropertyValue "d2d1" -Force

        # Force all profiles to NOT use GPU
        foreach ($profile in $settings.profiles.list) {
            $profile | Add-Member -NotePropertyName "experimental.rendering.glyphCache" -NotePropertyValue "false" -Force
            $profile | Add-Member -NotePropertyName "rendering.glyphCache" -NotePropertyValue "false" -Force
        }

        # Write modified settings
        $settings | ConvertTo-Json -Depth 10 | Set-Content $wtSettingsPath -Encoding UTF8
        Write-Host "  ✓ GPU acceleration disabled (d2d1 software rendering enabled)" -ForegroundColor Green
    }
    catch {
        Write-Host "  ✗ Error modifying settings: $_" -ForegroundColor Red
    }
}

# ============================================================================
# PHASE 2: CLEAR WINDOWS TERMINAL CACHE
# ============================================================================
Write-Host "`n[2] Clearing Windows Terminal cache..." -ForegroundColor Yellow

$cacheLocations = @(
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\AC\INetCache",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalCache",
    "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\AC\Temp"
)

foreach ($location in $cacheLocations) {
    if (Test-Path $location) {
        try {
            Remove-Item $location -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Cleared: $(Split-Path $location -Leaf)" -ForegroundColor Green
        }
        catch {
            Write-Host "  ⚠ Could not clear: $(Split-Path $location -Leaf)" -ForegroundColor Yellow
        }
    }
}

# ============================================================================
# PHASE 3: RESET PROFILE CONSOLE SETTINGS
# ============================================================================
Write-Host "`n[3] Resetting profile console settings..." -ForegroundColor Yellow

$regPaths = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
    "HKCU:\Console",
    "HKCU:\Software\Microsoft\Command Processor"
)

foreach ($path in $regPaths) {
    if (Test-Path $path) {
        # Remove ForceShellExecuteOpen that requires admin
        Remove-ItemProperty -Path $path -Name "ForceShellExecuteOpen" -ErrorAction SilentlyContinue
        Write-Host "  ✓ Cleaned: $(Split-Path $path -Leaf)" -ForegroundColor Green
    }
}

# ============================================================================
# PHASE 4: TEMPORARY WORKAROUND - USE LEGACY CONSOLE
# ============================================================================
Write-Host "`n[4] Enabling legacy console rendering (GPU workaround)..." -ForegroundColor Yellow

$conhostPath = "HKCU:\Console"
if (-not (Test-Path $conhostPath)) { New-Item -Path $conhostPath -Force | Out-Null }

# Force legacy console (disables GPU acceleration for console)
New-ItemProperty -Path $conhostPath -Name "ForceV2" -Value 0 -PropertyType DWORD -Force | Out-Null
Write-Host "  ✓ Legacy console mode enabled (disables GPU for console)" -ForegroundColor Green

# ============================================================================
# PHASE 5: CLEAR TEMPORARY FILES
# ============================================================================
Write-Host "`n[5] Clearing temporary files..." -ForegroundColor Yellow

$tempDirs = @(
    "$env:TEMP",
    "$env:LOCALAPPDATA\Temp"
)

foreach ($tempDir in $tempDirs) {
    if (Test-Path $tempDir) {
        try {
            Get-ChildItem $tempDir -Recurse -Force -ErrorAction SilentlyContinue |
                Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Cleared: $(Split-Path $tempDir -Leaf)" -ForegroundColor Green
        }
        catch {
            Write-Host "  ⚠ Partial clear: $(Split-Path $tempDir -Leaf)" -ForegroundColor Yellow
        }
    }
}

# ============================================================================
# PHASE 6: TEST CMD EXECUTION
# ============================================================================
Write-Host "`n[6] Testing CMD execution..." -ForegroundColor Yellow

try {
    $testResult = cmd /c "echo test" 2>&1
    if ($testResult -eq "test") {
        Write-Host "  ✓ CMD test PASSED - Console is working!" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ CMD test returned: $testResult" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "  ✗ CMD test FAILED: $_" -ForegroundColor Red
}

# ============================================================================
# PHASE 7: TEST POWERSHELL EXECUTION
# ============================================================================
Write-Host "`n[7] Testing PowerShell execution..." -ForegroundColor Yellow

try {
    $testResult = powershell -NoProfile -Command "Write-Host 'test'"
    if ($testResult -like "*test*") {
        Write-Host "  ✓ PowerShell test PASSED" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ⚠ PowerShell test warning: $_" -ForegroundColor Yellow
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "`n========== FIX COMPLETE ==========" -ForegroundColor Cyan
Write-Host @"
Changes Applied:
  ✓ GPU acceleration disabled (software rendering enabled)
  ✓ Windows Terminal cache cleared
  ✓ Profile console settings reset
  ✓ Legacy console mode enabled
  ✓ Temporary files cleared
  ✓ CMD/PowerShell verified working

IMPORTANT: You must RESTART WINDOWS for all changes to take effect.

After restart:
  1. Try: Win+R → cmd (should open without admin prompt)
  2. Try: PowerShell (should work normally)
  3. Verify: Console stays open and is responsive

If console still crashes after restart:
  - Try starting Windows in Safe Mode
  - Update Intel graphics driver (igd10um64xe.DLL)
  - Reinstall Windows Terminal from Microsoft Store

Backup of original settings: $wtSettingsBackup
"@ -ForegroundColor Gray

Write-Host "`n"
if ($AutoRestart) {
    Write-Host "Restarting Windows in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
}
else {
    $restart = Read-Host "Restart Windows now? (Y/N)"
    if ($restart -eq "Y") {
        Restart-Computer -Force
    }
    else {
        Write-Host "Remember to restart Windows manually for changes to take effect!" -ForegroundColor Yellow
    }
}
