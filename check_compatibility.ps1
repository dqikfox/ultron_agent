# Unity & VS Code Compatibility Checker

Write-Host "`n=== ULTRON Unity Compatibility Check ===" -ForegroundColor Cyan
Write-Host ""

# VS Code
try {
    $vscode = code --version | Select-Object -First 1
    Write-Host "[VS Code]    $vscode" -ForegroundColor Green
    
    $major = [int]($vscode -split '\.')[0]
    $minor = [int]($vscode -split '\.')[1]
    
    if ($major -ge 1 -and $minor -ge 75) {
        Write-Host "             ✅ Compatible with Unity 2022.3+" -ForegroundColor Green
    } else {
        Write-Host "             ⚠️ Update to 1.75.0+ recommended" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[VS Code]    ❌ Not found" -ForegroundColor Red
}

Write-Host ""

# .NET SDK
try {
    $dotnet = dotnet --version
    Write-Host "[.NET SDK]   $dotnet" -ForegroundColor Green
    
    $major = [int]($dotnet -split '\.')[0]
    
    if ($major -ge 8) {
        Write-Host "             ✅ Compatible with Unity 6 / 2023+" -ForegroundColor Green
    } elseif ($major -ge 6) {
        Write-Host "             ✅ Compatible with Unity 2022.3+" -ForegroundColor Green
    } else {
        Write-Host "             ⚠️ Update to .NET 6.0+ recommended" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[.NET SDK]   ❌ Not found - Install from https://dotnet.microsoft.com/download" -ForegroundColor Red
}

Write-Host ""

# Python
try {
    $python = python --version
    Write-Host "[Python]     $python" -ForegroundColor Green
} catch {
    Write-Host "[Python]     ❌ Not found" -ForegroundColor Red
}

Write-Host ""

# Ollama
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -TimeoutSec 2
    Write-Host "[Ollama]     Running (version $($ollama.version))" -ForegroundColor Green
} catch {
    Write-Host "[Ollama]     ⚠️ Not running - Start with: ollama serve" -ForegroundColor Yellow
}

Write-Host ""

# Unity Bridge
try {
    $bridge = Invoke-RestMethod -Uri "http://localhost:8765/api/assistant" -Method POST -Body '{"query":"test"}' -ContentType "application/json" -TimeoutSec 2
    Write-Host "[Unity Bridge] ✅ Running on port 8765" -ForegroundColor Green
} catch {
    Write-Host "[Unity Bridge] ⚠️ Not running - Start with: .\start_unity_bridge.bat" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Recommendations ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "For Unity 2022.3 LTS:" -ForegroundColor White
Write-Host "  - VS Code 1.75.0+" -ForegroundColor Gray
Write-Host "  - .NET SDK 6.0+" -ForegroundColor Gray
Write-Host ""
Write-Host "For Unity 2023.1+:" -ForegroundColor White
Write-Host "  - VS Code 1.80.0+" -ForegroundColor Gray
Write-Host "  - .NET SDK 7.0+" -ForegroundColor Gray
Write-Host ""
Write-Host "For Unity 6 (Latest):" -ForegroundColor White
Write-Host "  - VS Code 1.85.0+" -ForegroundColor Gray
Write-Host "  - .NET SDK 8.0+" -ForegroundColor Gray
Write-Host ""
Write-Host "Download .NET SDK: https://dotnet.microsoft.com/download" -ForegroundColor Cyan
Write-Host ""
