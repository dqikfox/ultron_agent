# AMAZON Q UGS CLI - CMD FIX
# Removes Windows Terminal settings that require admin

Write-Host "`n========== AMAZON Q UGS CLI - CMD FIX ==========" -ForegroundColor Cyan
Write-Host "Current User: $(whoami)" -ForegroundColor Yellow
Write-Host "Profile: $env:USERPROFILE`n" -ForegroundColor Yellow

Write-Host "This script will reset Windows Terminal settings" -ForegroundColor White
Write-Host "that are causing CMD/PowerShell to require admin.`n" -ForegroundColor White

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit
}

Write-Host "`n[1] Removing Windows Terminal cached settings..." -ForegroundColor Magenta
$wtPaths = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "Microsoft.WindowsTerminal_*" -ErrorAction SilentlyContinue
if ($wtPaths) {
    foreach ($path in $wtPaths) {
        $settingsFile = Join-Path $path.FullName "LocalState\settings.json"
        if (Test-Path $settingsFile) {
            Write-Host "  Deleting: $settingsFile" -ForegroundColor Yellow
            Remove-Item -Path $settingsFile -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "`n[2] Clearing temporary files..." -ForegroundColor Magenta
try {
    $tempItems = Get-ChildItem "$env:LOCALAPPDATA\Temp" -ErrorAction SilentlyContinue
    if ($tempItems) {
        $tempItems | ForEach-Object {
            Remove-Item -Path $_.FullName -Force -Recurse -ErrorAction SilentlyContinue
        }
    }
    Write-Host "  Temp directory cleared" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not clear temp directory" -ForegroundColor Yellow
}

Write-Host "`n[3] Resetting console registry entries..." -ForegroundColor Magenta
$regPaths = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
    "HKCU:\Software\Microsoft\Command Processor"
)

foreach ($regPath in $regPaths) {
    if (Test-Path $regPath) {
        Write-Host "  Checking: $regPath" -ForegroundColor Cyan
        Remove-ItemProperty -Path $regPath -Name "ForceShellExecuteOpen" -ErrorAction SilentlyContinue -Force
    }
}

Write-Host "`n[4] Removing Amazon Q/UGS settings..." -ForegroundColor Magenta
$paths = @("HKCU:\Software\Amazon", "HKCU:\Software\Unity")
foreach ($p in $paths) {
    if (Test-Path $p) {
        Write-Host "  Removing: $p" -ForegroundColor Yellow
        Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n[5] Testing CMD..." -ForegroundColor Magenta
try {
    $result = cmd /c "echo test" 2>&1
    if ($result -eq "test") {
        Write-Host "  [OK] CMD test passed!" -ForegroundColor Green
    } else {
        Write-Host "  [!] CMD test inconclusive: $result" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] CMD test failed" -ForegroundColor Red
}

Write-Host "`n========== FIX COMPLETE ==========" -ForegroundColor Cyan
Write-Host "`nNEXT: Restart Windows and test CMD" -ForegroundColor Yellow
Write-Host "`nRestart now? (Y/N): " -ForegroundColor Yellow -NoNewline
$restart = Read-Host
if ($restart -eq "Y" -or $restart -eq "y") {
    Write-Host "`nRestarting in 10 seconds..." -ForegroundColor Red
    Start-Sleep -Seconds 10
    Restart-Computer -Force
} else {
    Write-Host "`nRemember to restart later!" -ForegroundColor Yellow
}
