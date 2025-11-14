#!/usr/bin/env pwsh
<#
.SYNOPSIS
Docker DNS Resolution Troubleshooting and Fix Script
.DESCRIPTION
Diagnoses and fixes Docker DNS resolution issues on Windows/Mac
.PARAMETER Fix
Apply fixes automatically
.PARAMETER Verbose
Show detailed diagnostic output
.EXAMPLE
./fix_docker_dns.ps1 -Fix -Verbose
#>

param(
    [switch]$Fix,
    [switch]$Verbose
)

$ErrorActionPreference = "SilentlyContinue"

# Color output
$colors = @{
    Success = "Green"
    Error   = "Red"
    Warning = "Yellow"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-Diagnostic {
    param([string]$Message, [string]$Type = "Info")
    $prefix = switch ($Type) {
        "Success" { "[OK]" }
        "Error"   { "[FAIL]" }
        "Warning" { "[WARN]" }
        "Info"    { "[INFO]" }
        default   { "[-]" }
    }
    Write-Host "$prefix $Message" -ForegroundColor $colors[$Type]
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor $colors["Header"]
    Write-Host $Title -ForegroundColor $colors["Header"]
    Write-Host "=" * 60 -ForegroundColor $colors["Header"]
}

# Main diagnostics
Write-Section "Docker DNS Resolution Diagnostic"

# 1. Check Docker service
Write-Diagnostic "Checking Docker service status..." -Type Info
$dockerService = Get-Service Docker -ErrorAction SilentlyContinue
if ($dockerService) {
    if ($dockerService.Status -eq "Running") {
        Write-Diagnostic "Docker service is running" -Type Success
    } else {
        Write-Diagnostic "Docker service is NOT running (Status: $($dockerService.Status))" -Type Error
        if ($Fix) {
            Write-Diagnostic "Starting Docker service..." -Type Info
            Start-Service Docker -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 3
            Write-Diagnostic "Docker service started" -Type Success
        }
    }
} else {
    Write-Diagnostic "Docker service not found - Docker Desktop may not be installed" -Type Error
}

# 2. Test Docker daemon connectivity
Write-Section "Docker Daemon Connectivity"
Write-Diagnostic "Testing Docker daemon..." -Type Info
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Diagnostic "Docker daemon is responsive" -Type Success
    if ($Verbose) {
        Write-Host $dockerInfo | head -20
    }
} else {
    Write-Diagnostic "Docker daemon is NOT responsive" -Type Error
    if ($Verbose) {
        Write-Host "Error: $dockerInfo"
    }
    if ($Fix) {
        Write-Diagnostic "Attempting to restart Docker Desktop..." -Type Info
        Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Write-Diagnostic "Restarting Docker Desktop (wait 30 seconds)..." -Type Warning
    }
}

# 3. Check DNS in container
Write-Section "Container DNS Resolution"
Write-Diagnostic "Testing DNS resolution inside container..." -Type Info
$dnsTest = docker run --rm busybox nslookup google.com 2>&1
if ($dnsTest -like "*Address*") {
    Write-Diagnostic "DNS resolution working in container" -Type Success
    if ($Verbose) {
        Write-Host $dnsTest
    }
} else {
    Write-Diagnostic "DNS resolution FAILING in container" -Type Error
    if ($Verbose) {
        Write-Host "Output: $dnsTest"
    }
}

# 4. Check host.docker.internal
Write-Section "Docker Host Communication"
Write-Diagnostic "Testing host.docker.internal resolution..." -Type Info
$hostTest = docker run --rm busybox nslookup host.docker.internal 2>&1
if ($hostTest -like "*Address*") {
    Write-Diagnostic "host.docker.internal is reachable" -Type Success
} else {
    Write-Diagnostic "host.docker.internal is NOT reachable" -Type Warning
    Write-Diagnostic "This may prevent containers from accessing host services" -Type Warning
}

# 5. List networks
Write-Section "Docker Networks"
Write-Diagnostic "Available networks:" -Type Info
$networks = docker network ls 2>&1 | Select-Object -Skip 1
if ($networks) {
    Write-Host $networks
} else {
    Write-Diagnostic "Could not list networks" -Type Error
}

# 6. Check DNS configuration
Write-Section "System DNS Configuration"
Write-Diagnostic "Current system DNS servers:" -Type Info
$dnsServers = Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses
if ($dnsServers) {
    $dnsServers | ForEach-Object { Write-Host "  - $_" }
} else {
    Write-Diagnostic "Could not retrieve DNS servers" -Type Warning
}

# 7. Test specific IPs
Write-Section "DNS Server Connectivity"
Write-Diagnostic "Testing connectivity to common DNS servers..." -Type Info

$dnsServersToTest = @(
    @{Name = "Google DNS (8.8.8.8)"; IP = "8.8.8.8"}
    @{Name = "Cloudflare DNS (1.1.1.1)"; IP = "1.1.1.1"}
    @{Name = "Google DNS Secondary (8.8.4.4)"; IP = "8.8.4.4"}
)

foreach ($dns in $dnsServersToTest) {
    $testConn = Test-Connection -ComputerName $dns.IP -Count 1 -Quiet
    if ($testConn) {
        Write-Diagnostic "$($dns.Name) is reachable" -Type Success
    } else {
        Write-Diagnostic "$($dns.Name) is NOT reachable" -Type Error
    }
}

# Recommendations based on findings
Write-Section "Recommended Actions"

if ($LASTEXITCODE -ne 0) {
    Write-Diagnostic "Docker daemon not responding - try:" -Type Warning
    Write-Host "  1. Restart Docker Desktop" -ForegroundColor Cyan
    Write-Host "  2. Run: Stop-Process -Name 'Docker Desktop' -Force" -ForegroundColor Cyan
    Write-Host "  3. Wait 5 seconds and restart Docker Desktop" -ForegroundColor Cyan
}

if ($dnsTest -notlike "*Address*") {
    Write-Diagnostic "DNS not working in containers - try:" -Type Warning
    Write-Host "  1. Configure Docker DNS in Docker Desktop settings:" -ForegroundColor Cyan
    Write-Host "     - Settings > Resources > Network" -ForegroundColor Cyan
    Write-Host "     - Set DNS Server to 8.8.8.8" -ForegroundColor Cyan
    Write-Host "  2. Or edit C:\Users\<user>\AppData\Roaming\Docker\daemon.json:" -ForegroundColor Cyan
    Write-Host "     {" -ForegroundColor Cyan
    Write-Host '       "dns": ["8.8.8.8", "8.8.4.4"]' -ForegroundColor Cyan
    Write-Host "     }" -ForegroundColor Cyan
}

if ($Fix) {
    Write-Section "Applying Fixes"

    Write-Diagnostic "Fix Step 1: Flushing DNS cache..." -Type Info
    Clear-DnsClientCache
    Write-Diagnostic "DNS cache flushed" -Type Success

    Write-Diagnostic "Fix Step 2: Configuring Docker daemon DNS..." -Type Info
    $daemonJsonPath = "$env:APPDATA\Docker\daemon.json"

    if (Test-Path $daemonJsonPath) {
        $daemonConfig = Get-Content $daemonJsonPath | ConvertFrom-Json
    } else {
        $daemonConfig = @{}
    }

    $daemonConfig | Add-Member -NotePropertyName dns -NotePropertyValue @("8.8.8.8", "8.8.4.4") -Force
    $daemonConfig | ConvertTo-Json | Set-Content $daemonJsonPath
    Write-Diagnostic "Docker daemon configuration updated: $daemonJsonPath" -Type Success

    Write-Diagnostic "Fix Step 3: Restarting Docker Desktop..." -Type Info
    Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5

    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        & $dockerPath | Out-Null
        Write-Diagnostic "Docker Desktop restarting (wait 30+ seconds for full startup)..." -Type Warning
        Write-Diagnostic "Please run the diagnostic again in 30 seconds to verify fixes" -Type Info
    }
}

Write-Section "Summary"
Write-Diagnostic "Diagnostic complete. Review recommendations above." -Type Info
if (-not $Fix) {
    Write-Diagnostic "Run with -Fix parameter to apply recommended fixes automatically" -Type Info
}

Write-Host ""
