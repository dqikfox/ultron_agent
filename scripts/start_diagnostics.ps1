# Start ULTRON Diagnostics Dashboard
# Port: 5001
# Access: http://localhost:5001

Write-Host "🔍 Starting ULTRON Diagnostics Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Check if port is available
$portInUse = Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue

if ($portInUse) {
    Write-Host "⚠️  Port 5001 is already in use" -ForegroundColor Yellow
    Write-Host "Trying to free the port..." -ForegroundColor Yellow

    $process = Get-Process -Id $portInUse.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Stopping process: $($process.Name) (PID: $($process.Id))" -ForegroundColor Yellow
        Stop-Process -Id $process.Id -Force
        Start-Sleep -Seconds 2
    }
}

# Start diagnostics dashboard
Write-Host "✅ Starting dashboard on http://localhost:5001" -ForegroundColor Green
Write-Host ""
Write-Host "Features:" -ForegroundColor White
Write-Host "  - Real-time crash reporting" -ForegroundColor Gray
Write-Host "  - System health monitoring" -ForegroundColor Gray
Write-Host "  - Service status checks" -ForegroundColor Gray
Write-Host "  - Performance telemetry" -ForegroundColor Gray
Write-Host "  - AWS CloudWatch integration" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m diagnostics.diagnostics_dashboard
