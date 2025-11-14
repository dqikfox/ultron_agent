# Check AWS CodeWhisperer Customization Status
# Usage: .\scripts\check_codewhisperer_status.ps1

$customizationArn = "arn:aws:codewhisperer:us-east-1:941284019015:customization/7UY44NRR97Q4"

Write-Host "🔍 Checking CodeWhisperer Customization Status..." -ForegroundColor Cyan
Write-Host ""

try {
    # Get customization details
    $result = aws codewhisperer get-customization `
        --customization-arn $customizationArn `
        --output json 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error retrieving customization:" -ForegroundColor Red
        Write-Host $result -ForegroundColor DarkRed
        exit 1
    }

    $customization = $result | ConvertFrom-Json

    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ULTRON CodeWhisperer Customization" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Name: " -NoNewline
    Write-Host $customization.name -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Status: " -NoNewline

    switch ($customization.status) {
        "CREATING" { Write-Host "⏳ Creating" -ForegroundColor Yellow }
        "AVAILABLE" { Write-Host "✅ Available" -ForegroundColor Green }
        "DELETING" { Write-Host "🗑️ Deleting" -ForegroundColor Magenta }
        "FAILED" { Write-Host "❌ Failed" -ForegroundColor Red }
        default { Write-Host $customization.status -ForegroundColor Gray }
    }

    Write-Host ""
    Write-Host "Version: " -NoNewline
    Write-Host $customization.version -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Created: " -NoNewline
    Write-Host $customization.createdTime -ForegroundColor Gray
    Write-Host ""
    Write-Host "Last Updated: " -NoNewline
    Write-Host $customization.lastUpdatedTime -ForegroundColor Gray
    Write-Host ""

    if ($customization.status -eq "AVAILABLE") {
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "✅ Customization Ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor White
        Write-Host "  1. Activate customization in AWS Console" -ForegroundColor Cyan
        Write-Host "  2. Install AWS Toolkit extension in VS Code" -ForegroundColor Cyan
        Write-Host "  3. Configure CodeWhisperer in VS Code settings" -ForegroundColor Cyan
        Write-Host "  4. Test suggestions with ULTRON code" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "VS Code Settings:" -ForegroundColor White
        Write-Host '  "aws.codeWhisperer.customization": "' -NoNewline -ForegroundColor DarkGray
        Write-Host $customizationArn -NoNewline -ForegroundColor Yellow
        Write-Host '"' -ForegroundColor DarkGray
    } elseif ($customization.status -eq "CREATING") {
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "⏳ Still Creating..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Typical creation time: 30-60 minutes" -ForegroundColor White
        Write-Host "Check again in 10-15 minutes" -ForegroundColor Gray
    } elseif ($customization.status -eq "FAILED") {
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "❌ Creation Failed" -ForegroundColor Red
        Write-Host ""
        if ($customization.failureReason) {
            Write-Host "Reason: " -NoNewline -ForegroundColor White
            Write-Host $customization.failureReason -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Try:" -ForegroundColor White
        Write-Host "  1. Check repository connection" -ForegroundColor Cyan
        Write-Host "  2. Verify CodeStar connection is active" -ForegroundColor Cyan
        Write-Host "  3. Check CloudWatch logs for details" -ForegroundColor Cyan
    }

    Write-Host ""

} catch {
    Write-Host "❌ Error checking customization status: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you have:" -ForegroundColor Yellow
    Write-Host "  - AWS CLI installed and configured" -ForegroundColor White
    Write-Host "  - CodeWhisperer permissions" -ForegroundColor White
    Write-Host "  - Correct region (us-east-1)" -ForegroundColor White
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
