# UGS CLI Deploy Script
$ugs = "C:\Projects\ultron_agent\ugs.exe"

Write-Host "Deploying UltronModule to Unity Cloud Code..." -ForegroundColor Cyan

# Login
& $ugs login

# Deploy
& $ugs deploy UltronModule

Write-Host "Deployment complete!" -ForegroundColor Green
