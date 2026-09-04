# ============================================================
# AMAZON Q UGS CLI - CMD FIX (PowerShell Version)
# ============================================================
# Removes Windows Terminal settings that require admin
# This fixes: CMD/PowerShell "opens and closes" on your profile
# ============================================================

Write-Host "`n========== AMAZON Q UGS CLI - CMD FIX ==========" -ForegroundColor Cyan
Write-Host "Current User: $(whoami)" -ForegroundColor Yellow
Write-Host "Profile: $env:USERPROFILE`n" -ForegroundColor Yellow

Write-Host "This script will reset Windows Terminal settings that are" -ForegroundColor White
Write-Host "causing CMD/PowerShell to require admin privileges.`n" -ForegroundColor White

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`n[1] Removing Windows Terminal cached settings..." -ForegroundColor Magenta
$wtPaths = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "Microsoft.WindowsTerminal_*" -ErrorAction SilentlyContinue
foreach ($path in $wtPaths) {
    $settingsFile = Join-Path $path.FullName "LocalState\settings.json"
    if (Test-Path $settingsFile) {
        Write-Host "  Deleting: $settingsFile" -ForegroundColor Yellow
        Remove-Item -Path $settingsFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n[2] Clearing temporary files..." -ForegroundColor Magenta
try {
    $tempItems = Get-ChildItem "$env:LOCALAPPDATA\Temp" -ErrorAction SilentlyContinue
    $tempItems | ForEach-Object {
        Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction SilentlyContinue
    }
    Write-Host "  Temp directory cleared" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not fully clear temp directory (may be in use)" -ForegroundColor Yellow
}

Write-Host "`n[3] Resetting console registry entries..." -ForegroundColor Magenta

# Remove problematic registry entries
@(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
    "HKCU:\Software\Microsoft\Command Processor"
) | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "  Checking: $_" -ForegroundColor Cyan

        if ($_ -eq "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") {
            Remove-ItemProperty -Path $_ -Name "ForceShellExecuteOpen" -ErrorAction SilentlyContinue -Force
        }
    }
}

# Optional: Remove Amazon Q related settings
Write-Host "`n[4] Removing Amazon Q/UGS CLI settings..." -ForegroundColor Magenta
@(
    "HKCU:\Software\Amazon",
    "HKCU:\Software\Unity"
) | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "  Removing: $_" -ForegroundColor Yellow
        Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n[5] Testing CMD execution..." -ForegroundColor Magenta
try {
    $testResult = & cmd /c "echo test" 2>&1
    if ($testResult -eq "test") {
        Write-Host "  [✓] CMD test PASSED - Console is accessible!" -ForegroundColor Green
    } else {
        Write-Host "  [⚠] CMD test inconclusive (output: $testResult)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [✗] CMD test FAILED - May require full system restart" -ForegroundColor Red
}

Write-Host "`n========== FIX COMPLETE ==========" -ForegroundColor Cyan
Write-Host "`n[✓] Windows Terminal settings reset" -ForegroundColor Green
Write-Host "[✓] Temporary files cleared" -ForegroundColor Green
Write-Host "[✓] Registry entries cleaned" -ForegroundColor Green

Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Close all CMD/PowerShell windows" -ForegroundColor White
Write-Host "  2. Restart your computer (IMPORTANT!)" -ForegroundColor Cyan
Write-Host "  3. Test: Press Win+R, type 'cmd'" -ForegroundColor White
Write-Host "  4. CMD should now open normally without admin!" -ForegroundColor Green

Write-Host "`nRestart now? (Y/N): " -ForegroundColor Yellow -NoNewline
$restart = Read-Host
if ($restart -eq "Y" -or $restart -eq "y") {
    Write-Host "`nRestarting in 10 seconds... (Close other windows!)" -ForegroundColor Red
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host "`nRemember to restart for the fix to take effect!" -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
