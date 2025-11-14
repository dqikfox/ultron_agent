# Start Copilot ↔ Amazon Q Direct Bridge (NO ADMIN)
# This launches in the current user context without elevation

param(
    [string]$Mode = "--listen"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " COPILOT → AMAZON Q DIRECT BRIDGE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set window title
$host.UI.RawUI.WindowTitle = "Bridge - Copilot to Amazon Q Router"

# Navigate to script directory
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Handle parameters
if ($Mode -eq "--help") {
    Write-Host "Usage: .\start_bridge.ps1 [--demo|--listen]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --demo    Test mode with sample workflows"
    Write-Host "  --listen  Production mode (default)"
    Write-Host "  --help    Show this help message"
    exit 0
}

# Check Python
Write-Host "[+] Checking Python..." -ForegroundColor Gray
$pythonCheck = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[+] Checking aiohttp..." -ForegroundColor Gray
$aiocheck = python -c "import aiohttp" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Installing aiohttp..." -ForegroundColor Yellow
    pip install aiohttp --quiet
}

Write-Host ""
Write-Host "[✓] Starting bridge in PRODUCTION mode..." -ForegroundColor Green
Write-Host "[*] Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start bridge
python copilot_amazon_q_bridge.py $Mode

Write-Host ""
Read-Host "Press Enter to exit"
