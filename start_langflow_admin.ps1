# PowerShell script to start LangFlow with Admin privileges
# Right-click and select "Run with PowerShell"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Yellow
    $scriptPath = $PSCommandPath
    $arguments = "-NoExit -Command cd '$pwd'; & '$scriptPath'"
    Start-Process PowerShell -ArgumentList $arguments -Verb RunAs
    exit
}

# If we get here, we have admin privileges
Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LangFlow Server Starting" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: http://localhost:7860" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
Set-Location C:\Projects\ultron_agent

# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Start LangFlow
Write-Host "Starting LangFlow..." -ForegroundColor Green
Write-Host ""

python -m langflow run --host 127.0.0.1 --port 7860

Write-Host ""
Write-Host "LangFlow server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to close"
