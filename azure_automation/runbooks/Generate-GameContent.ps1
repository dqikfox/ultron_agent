
param([string]$Prompt)
$body = @{model="qwen3-coder:480b-cloud"; prompt=$Prompt; stream=$false} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
Write-Output $response.response
