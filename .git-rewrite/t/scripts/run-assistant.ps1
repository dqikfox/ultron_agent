#!/usr/bin/env pwsh
# AI Assistant Web Application Runner
# Usage: .\scripts\run-assistant.ps1 [dev|build|preview]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "build", "preview", "install")]
    [string]$Command = "dev"
)

$AssistantPath = Join-Path $PSScriptRoot ".." "assistant" "ai-assistant"

if (-not (Test-Path $AssistantPath)) {
    Write-Error "AI Assistant directory not found: $AssistantPath"
    exit 1
}

Write-Host "🤖 Ultron Agent 2 - AI Assistant" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Push-Location $AssistantPath

try {
    switch ($Command) {
        "install" {
            Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
            npm install
        }
        "dev" {
            Write-Host "🚀 Starting development server..." -ForegroundColor Green
            Write-Host "URL: http://localhost:5173" -ForegroundColor Blue
            npm run dev
        }
        "build" {
            Write-Host "🏗️ Building for production..." -ForegroundColor Yellow
            npm run build
        }
        "preview" {
            Write-Host "👀 Starting preview server..." -ForegroundColor Magenta
            npm run preview
        }
    }
} catch {
    Write-Error "Failed to run command: $Command"
    Write-Error $_.Exception.Message
    exit 1
} finally {
    Pop-Location
}

Write-Host "`n✅ Command completed successfully!" -ForegroundColor Green