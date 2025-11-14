# Fix Unity Accelerator Port Conflict
# This script changes Unity Accelerator from port 8080 to 9080

$configPath = "C:\Users\ultro\AppData\Local\UnityAccelerator\unity-accelerator.cfg"

Write-Host "Stopping Unity Accelerator service..." -ForegroundColor Yellow
Stop-Service "Unity Accelerator" -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "Reading config file..." -ForegroundColor Yellow
$config = Get-Content $configPath -Raw | ConvertFrom-Json

Write-Host "Current HTTP Port: $($config.LastUsedHTTPPort)" -ForegroundColor Cyan

# Change port from 8080 to 9080
$config.LastUsedHTTPPort = 9080

Write-Host "Changing to port: 9080" -ForegroundColor Green

# Save config
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath

Write-Host "Starting Unity Accelerator service..." -ForegroundColor Yellow
Start-Service "Unity Accelerator"

Start-Sleep -Seconds 3

Write-Host "`nDone! Unity Accelerator now uses port 9080" -ForegroundColor Green
Write-Host "Port 8080 is now free for ULTRON!" -ForegroundColor Green
