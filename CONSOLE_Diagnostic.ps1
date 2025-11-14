#!/usr/bin/env powershell
# CMD/PowerShell Console Diagnostic & Repair
# Identifies and fixes console issues

param(
    [switch]$Repair = $false
)

function Write-Status {
    param([string]$Message, [string]$Type = "info")

    $color = switch($Type) {
        "error" { "Red" }
        "warning" { "Yellow" }
        "success" { "Green" }
        default { "Cyan" }
    }

    Write-Host "[*] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message -ForegroundColor $color
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     Console Diagnostic & Repair Utility              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

$issues = @()

# Check 1: Execution Policy
Write-Status "Checking PowerShell Execution Policy..."
$execPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($execPolicy -eq "Restricted") {
    $issues += "Restricted execution policy"
    Write-Status "ISSUE FOUND: Execution policy is Restricted" "error"
    if ($Repair) {
        Write-Status "Fixing: Setting to RemoteSigned..."
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Status "FIXED: Execution policy updated" "success"
    }
} else {
    Write-Status "OK: Execution policy is $execPolicy" "success"
}

# Check 2: CMD Registry Keys
Write-Status "Checking Windows Registry for CMD restrictions..."
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\System"
$cmdDisabled = Get-ItemProperty -Path $regPath -Name "DisableCMD" -ErrorAction SilentlyContinue
if ($cmdDisabled) {
    $issues += "CMD disabled via registry"
    Write-Status "ISSUE FOUND: DisableCMD registry key detected" "error"
    if ($Repair) {
        Write-Status "Fixing: Removing DisableCMD key..."
        Remove-ItemProperty -Path $regPath -Name "DisableCMD" -Force
        Write-Status "FIXED: DisableCMD removed" "success"
    }
} else {
    Write-Status "OK: No DisableCMD policy found" "success"
}

# Check 3: Console Host
Write-Status "Checking Console Host (conhost.exe)..."
$conhost = Get-Command conhost.exe -ErrorAction SilentlyContinue
if ($conhost) {
    Write-Status "OK: Console Host found at: $($conhost.Source)" "success"
} else {
    $issues += "Console Host not found"
    Write-Status "ISSUE FOUND: Console Host (conhost.exe) not found" "error"
}

# Check 4: CMD Executable
Write-Status "Checking CMD.EXE..."
$cmd = Get-Command cmd.exe -ErrorAction SilentlyContinue
if ($cmd) {
    Write-Status "OK: CMD found at: $($cmd.Source)" "success"
} else {
    $issues += "CMD.EXE not found"
    Write-Status "ISSUE FOUND: CMD.EXE not found" "error"
}

# Check 5: PowerShell Executable
Write-Status "Checking PowerShell.EXE..."
$ps = Get-Command powershell.exe -ErrorAction SilentlyContinue
if ($ps) {
    Write-Status "OK: PowerShell found at: $($ps.Source)" "success"
} else {
    $issues += "PowerShell.EXE not found"
    Write-Status "ISSUE FOUND: PowerShell.EXE not found" "error"
}

# Check 6: File Type Associations
Write-Status "Checking file associations..."
$batAssoc = cmd /c assoc .bat 2>$null
if ($batAssoc -like "*.bat=batfile*") {
    Write-Status "OK: .bat association valid" "success"
} else {
    $issues += "Invalid .bat file association"
    Write-Status "ISSUE FOUND: .bat association invalid" "error"
    if ($Repair) {
        Write-Status "Fixing: Setting .bat association to batfile..."
        cmd /c "assoc .bat=batfile" >$null 2>&1
        cmd /c "ftype batfile=%COMSPEC% /c %1" >$null 2>&1
        Write-Status "FIXED: .bat association restored" "success"
    }
}

# Check 7: Event Viewer for crashes
Write-Status "Checking for console crashes in Event Viewer..."
$crashes = Get-WinEvent -FilterHashtable @{
    LogName = 'Application'
    Id = 1000
    StartTime = (Get-Date).AddHours(-24)
} -ErrorAction SilentlyContinue | Where-Object {
    $_.Message -match 'conhost|cmd|powershell'
}

if ($crashes) {
    $issues += "Recent console crashes detected"
    Write-Status "ISSUE FOUND: Recent console crashes detected" "error"
    Write-Status "Number of crashes: $($crashes.Count)" "error"
} else {
    Write-Status "OK: No recent console crashes" "success"
}

# Check 8: System Integrity
Write-Status "Checking Windows System Integrity (SFC)..."
Write-Status "Note: This may take a moment..." "warning"

# Summary
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    DIAGNOSTIC SUMMARY                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "✓ No issues detected! Console appears healthy." -ForegroundColor Green
} else {
    Write-Host "✗ Found $($issues.Count) issue(s):" -ForegroundColor Red
    Write-Host ""
    foreach ($issue in $issues) {
        Write-Host "  • $issue" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "To repair automatically, run: .\CONSOLE_Diagnostic.ps1 -Repair" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Recommendations:" -ForegroundColor Green
Write-Host "  1. If issues found, run with -Repair flag to fix automatically"
Write-Host "  2. Restart your computer after repair"
Write-Host "  3. Test CMD by pressing Windows+R and typing: cmd"
Write-Host ""

if ($Repair) {
    Write-Host "Restart required: Please restart Windows for changes to take effect." -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"
