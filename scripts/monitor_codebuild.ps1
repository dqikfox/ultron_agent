# Monitor AWS CodeBuild - ULTRON Agent
# Usage: .\scripts\monitor_codebuild.ps1

$buildId = "runner:f9aedd7c-a0f1-4321-b83f-92379522f90d"

Write-Host "🔍 Monitoring CodeBuild: $buildId" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring`n" -ForegroundColor Yellow

while ($true) {
    try {
        # Get build status
        $build = aws codebuild batch-get-builds --ids $buildId --output json | ConvertFrom-Json

        if ($build.builds.Count -eq 0) {
            Write-Host "❌ Build not found" -ForegroundColor Red
            break
        }

        $buildInfo = $build.builds[0]
        $status = $buildInfo.buildStatus
        $phase = $buildInfo.currentPhase

        Clear-Host
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "  ULTRON Agent - CodeBuild Monitor" -ForegroundColor Green
        Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Build ID: " -NoNewline
        Write-Host $buildId -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Status: " -NoNewline

        switch ($status) {
            "IN_PROGRESS" { Write-Host "⏳ In Progress" -ForegroundColor Yellow }
            "SUCCEEDED" { Write-Host "✅ Succeeded" -ForegroundColor Green }
            "FAILED" { Write-Host "❌ Failed" -ForegroundColor Red }
            "STOPPED" { Write-Host "⛔ Stopped" -ForegroundColor Magenta }
            default { Write-Host $status -ForegroundColor Gray }
        }

        Write-Host "Current Phase: " -NoNewline
        Write-Host $phase -ForegroundColor Cyan
        Write-Host ""

        # Show phases
        Write-Host "Build Phases:" -ForegroundColor White
        Write-Host "─────────────" -ForegroundColor Gray

        foreach ($phaseItem in $buildInfo.phases) {
            $phaseName = $phaseItem.phaseType
            $phaseStatus = $phaseItem.phaseStatus

            $icon = switch ($phaseStatus) {
                "SUCCEEDED" { "✅" }
                "FAILED" { "❌" }
                "IN_PROGRESS" { "⏳" }
                default { "⏸️" }
            }

            $color = switch ($phaseStatus) {
                "SUCCEEDED" { "Green" }
                "FAILED" { "Red" }
                "IN_PROGRESS" { "Yellow" }
                default { "Gray" }
            }

            Write-Host "  $icon $phaseName" -NoNewline
            Write-Host " - $phaseStatus" -ForegroundColor $color

            if ($phaseItem.contexts) {
                foreach ($context in $phaseItem.contexts) {
                    Write-Host "     $($context.message)" -ForegroundColor DarkGray
                }
            }
        }

        Write-Host ""
        Write-Host "Last Updated: " -NoNewline
        Write-Host (Get-Date).ToString("HH:mm:ss") -ForegroundColor Gray

        # Check if build is complete
        if ($status -ne "IN_PROGRESS") {
            Write-Host ""
            Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
            Write-Host "Build Complete!" -ForegroundColor Green
            Write-Host ""

            if ($status -eq "SUCCEEDED") {
                Write-Host "✅ Next Steps:" -ForegroundColor Green
                Write-Host "   1. Check CodeWhisperer customization status" -ForegroundColor White
                Write-Host "   2. Activate the customization in AWS Console" -ForegroundColor White
                Write-Host "   3. Test CodeWhisperer with ULTRON-specific code" -ForegroundColor White
            } else {
                Write-Host "❌ Build failed. Check logs:" -ForegroundColor Red
                Write-Host "   aws codebuild batch-get-builds --ids $buildId" -ForegroundColor White
            }

            break
        }

        Start-Sleep -Seconds 10

    } catch {
        Write-Host "❌ Error monitoring build: $_" -ForegroundColor Red
        break
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
