# Configure Cursor MCP for Langflow workflows
# Run after creating flows in Langflow UI

Write-Host "🔧 Cursor MCP Configuration Script" -ForegroundColor Cyan
Write-Host ""

# Get flow IDs from user
Write-Host "Enter your Langflow Flow IDs:" -ForegroundColor Yellow
Write-Host "(Find these in Langflow UI URL after creating each flow)" -ForegroundColor Gray
Write-Host ""

$flowIds = @{}
$flowNames = @(
    "code_assistant",
    "python_type_hints", 
    "game_logic",
    "unity_csharp",
    "documentation_generator",
    "debug_assistant"
)

foreach ($name in $flowNames) {
    $id = Read-Host "Flow ID for $name"
    $flowIds[$name] = $id
}

# Create MCP config
$mcpConfig = @{
    mcpServers = @{
        "code-assistant" = @{
            command = "uvx"
            args = @("langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", $flowIds["code_assistant"])
            disabled = $false
        }
        "python-types" = @{
            command = "uvx"
            args = @("langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", $flowIds["python_type_hints"])
            disabled = $false
        }
        "game-logic" = @{
            command = "uvx"
            args = @("langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", $flowIds["game_logic"])
            disabled = $false
        }
        "unity-csharp" = @{
            command = "uvx"
            args = @("langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", $flowIds["unity_csharp"])
            disabled = $false
        }
        "docs-generator" = @{
            command = "uvx"
            args = @("langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", $flowIds["documentation_generator"])
            disabled = $false
        }
        "debug-assistant" = @{
            command = "uvx"
            args = @("langflow-mcp", "--base-url", "http://127.0.0.1:7861", "--flow-id", $flowIds["debug_assistant"])
            disabled = $false
        }
    }
}

# Save to file
$configJson = $mcpConfig | ConvertTo-Json -Depth 10
$configJson | Out-File "cursor_mcp_config.json" -Encoding UTF8

Write-Host ""
Write-Host "✅ Configuration saved to: cursor_mcp_config.json" -ForegroundColor Green

# Copy to Cursor location
$cursorConfigPath = "$env:APPDATA\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings"

if (Test-Path $cursorConfigPath) {
    Copy-Item "cursor_mcp_config.json" "$cursorConfigPath\cline_mcp_settings.json" -Force
    Write-Host "✅ Copied to Cursor settings" -ForegroundColor Green
} else {
    Write-Host "⚠️  Cursor settings path not found" -ForegroundColor Yellow
    Write-Host "   Manual copy required to: $cursorConfigPath" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart Cursor" -ForegroundColor White
Write-Host "2. Open Command Palette (Ctrl+Shift+P)" -ForegroundColor White
Write-Host "3. Run: 'MCP: Refresh Servers'" -ForegroundColor White
Write-Host "4. Test: 'Use code-assistant to format: def hello(): print(\"hi\")'" -ForegroundColor White
Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
