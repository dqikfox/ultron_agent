
param([string]$InputData)
$body = @{input=$InputData} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8765/inference" -Method Post -Body $body -ContentType "application/json"
Write-Output $response.output
