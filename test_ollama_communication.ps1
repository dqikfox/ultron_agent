# ULTRON Agent - Ollama Integration Test Script
# Tests communication with Ollama backend

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "ULTRON Agent - Ollama Communication Test" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

# Test 1: Check Ollama service is running
Write-Host "[Test 1/5] Checking Ollama service availability..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get -ErrorAction Stop
    Write-Host "✅ PASSED - Ollama service is running" -ForegroundColor Green
    Write-Host "   Models available: $($response.models.Count)" -ForegroundColor Gray
    $testsPassed++
} catch {
    Write-Host "❌ FAILED - Ollama service not responding: $_" -ForegroundColor Red
    $testsFailed++
}

Start-Sleep -Seconds 1

# Test 2: Check llava:7b model is available
Write-Host "`n[Test 2/5] Checking llava:7b model availability..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get -ErrorAction Stop
    $llamaModel = $response.models | Where-Object { $_.name -like "llava*" }
    if ($llamaModel) {
        Write-Host "✅ PASSED - llava model found: $($llamaModel.name)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "❌ FAILED - llava model not found" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "❌ FAILED - Could not check models: $_" -ForegroundColor Red
    $testsFailed++
}

Start-Sleep -Seconds 1

# Test 3: Simple generation test
Write-Host "`n[Test 3/5] Testing simple text generation..." -ForegroundColor Yellow
try {
    $body = @{
        model = 'llava:7b'
        prompt = 'Say only the word "Hello"'
        stream = $false
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri 'http://localhost:11434/api/generate' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 30 -ErrorAction Stop

    if ($response.done -eq $true) {
        Write-Host "✅ PASSED - Generation successful" -ForegroundColor Green
        Write-Host "   Response: $($response.response.Trim())" -ForegroundColor Gray
        Write-Host "   Duration: $([math]::Round($response.total_duration / 1000000000, 2))s" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "❌ FAILED - Generation incomplete" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "❌ FAILED - Generation error: $_" -ForegroundColor Red
    $testsFailed++
}

Start-Sleep -Seconds 1

# Test 4: Chat API test
Write-Host "`n[Test 4/5] Testing chat API with question..." -ForegroundColor Yellow
try {
    $body = @{
        model = 'llava:7b'
        messages = @(
            @{
                role = 'user'
                content = 'What is 5+3? Answer with only the number.'
            }
        )
        stream = $false
    } | ConvertTo-Json -Depth 3

    $response = Invoke-RestMethod -Uri 'http://localhost:11434/api/chat' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 30 -ErrorAction Stop

    if ($response.done -eq $true) {
        Write-Host "✅ PASSED - Chat successful" -ForegroundColor Green
        Write-Host "   Response: $($response.message.content.Trim())" -ForegroundColor Gray
        Write-Host "   Duration: $([math]::Round($response.total_duration / 1000000000, 2))s" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "❌ FAILED - Chat incomplete" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "❌ FAILED - Chat error: $_" -ForegroundColor Red
    $testsFailed++
}

Start-Sleep -Seconds 1

# Test 5: Multi-turn conversation
Write-Host "`n[Test 5/5] Testing multi-turn conversation..." -ForegroundColor Yellow
try {
    $body = @{
        model = 'llava:7b'
        messages = @(
            @{
                role = 'user'
                content = 'My name is ULTRON.'
            },
            @{
                role = 'assistant'
                content = 'Hello ULTRON! How can I help you today?'
            },
            @{
                role = 'user'
                content = 'What is my name? Answer with just the name.'
            }
        )
        stream = $false
    } | ConvertTo-Json -Depth 3

    $response = Invoke-RestMethod -Uri 'http://localhost:11434/api/chat' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 30 -ErrorAction Stop

    if ($response.done -eq $true) {
        Write-Host "✅ PASSED - Multi-turn conversation successful" -ForegroundColor Green
        Write-Host "   Response: $($response.message.content.Trim())" -ForegroundColor Gray
        Write-Host "   Context retained: $(if($response.message.content -like '*ULTRON*') {'Yes'} else {'No'})" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "❌ FAILED - Conversation incomplete" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "❌ FAILED - Conversation error: $_" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed / 5" -ForegroundColor $(if($testsPassed -eq 5) { 'Green' } else { 'Yellow' })
Write-Host "Tests Failed: $testsFailed / 5" -ForegroundColor $(if($testsFailed -eq 0) { 'Green' } else { 'Red' })

if ($testsFailed -eq 0) {
    Write-Host "`n✅ ALL TESTS PASSED - Ollama integration working perfectly!" -ForegroundColor Green
    Write-Host "   The ULTRON Agent can communicate with Ollama successfully." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️  SOME TESTS FAILED - Check errors above" -ForegroundColor Yellow
    exit 1
}
