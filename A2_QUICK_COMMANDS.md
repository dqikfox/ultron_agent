# A2: RATE LIMITING - QUICK COMMAND REFERENCE

## 🎯 COPY-PASTE READY COMMANDS

### PHASE 2: 3-MODEL REVIEWS

**Terminal 1: Syntax Check**
```powershell
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw
$prompt = "Check this Python code for syntax errors, import issues, and type hint completeness:`n`n$template`n`nReturn:`n1. Any syntax errors found`n2. Missing or incorrect imports`n3. Incomplete or wrong type hints`n4. Function signature issues`n5. Any other Python standard violations"
ollama run qwen2.5-coder:1.5b $prompt > review1_syntax.txt
Get-Content review1_syntax.txt
```

**Terminal 2: Logic Check**
```powershell
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw
$prompt = "Verify the rate limiting logic in this code. Check for:`n1. Is the token bucket algorithm correctly implemented?`n2. Will timestamp cleanup prevent memory leaks?`n3. Does it handle edge cases (clock skew, concurrent requests)?`n4. Is the IP detection reliable?`n5. What about race conditions in thread access?`n`nCode:`n$template`n`nReturn specific line numbers and issues."
ollama run gpt-oss:20b-cloud $prompt > review2_logic.txt
Get-Content review2_logic.txt
```

**Terminal 3: Security Check**
```powershell
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw
$prompt = "Security review of this rate limiting decorator. Check for:`n1. IP spoofing vulnerabilities`n2. DOS attack surface`n3. Whitelist bypass issues`n4. User ID bypass`n5. Side-channel attacks`n6. Memory exhaustion`n`nCode:`n$template`n`nReturn security concerns with severity (HIGH/MEDIUM/LOW)."
ollama run qwen2.5vl:3b $prompt > review3_security.txt
Get-Content review3_security.txt
```

### PHASE 3: REVIEW OUTPUT & TEST

**View all reviews**:
```powershell
Write-Host "=== SYNTAX ===" -ForegroundColor Yellow; Get-Content review1_syntax.txt
Write-Host "`n=== LOGIC ===" -ForegroundColor Yellow; Get-Content review2_logic.txt
Write-Host "`n=== SECURITY ===" -ForegroundColor Yellow; Get-Content review3_security.txt
```

**Test Rate Limiting** (after adding @rate_limit to api_server.py):
```powershell
# Terminal 1: Start API
python api_server.py

# Terminal 2: Hit endpoint 110 times (should get 429 on requests 101+)
for ($i = 1; $i -le 110; $i++) {
    try {
        $response = curl -s -w "`nHTTP_STATUS:%{http_code}" -X POST http://localhost:5000/api/command `
            -H "Content-Type: application/json" `
            -d '{"command":"test"}'

        if ($response -match "HTTP_STATUS:429") {
            Write-Host "✅ Request $i: 429 TOO MANY REQUESTS (rate limit working!)" -ForegroundColor Green
            break
        } else {
            Write-Host "✅ Request $i: 200 OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Request $i: Error" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 100
}
```

---

## 📊 EXPECTED OUTPUTS

### Review 1 (Syntax):
```
✓ Syntax: Valid Python 3.8+
✓ Imports: All required (threading, time, functools)
✓ Type hints: Complete on all parameters
✓ No issues found
```

### Review 2 (Logic):
```
Line 45: Consider RLock instead of Lock for reentrancy
Line 67: IP detection from X-Forwarded-For looks good
Line 89: Timestamp cleanup prevents memory leaks effectively
Line 112: Token bucket algorithm correctly refills at calculated rate
```

### Review 3 (Security):
```
MEDIUM: Validate X-Forwarded-For to prevent IP spoofing
HIGH: Add user_id validation to prevent false user claims
MEDIUM: Limit total unique IPs to prevent memory exhaustion
LOW: Timing information leaks rate limit status (not critical)
```

---

## 🎯 INTEGRATION STEPS

After reviews, in `api_server.py`:

```python
# Add import
from A2_RATE_LIMITING_TEMPLATE import rate_limit, RateLimitManager

# Add to endpoints
@app.route("/api/command", methods=["POST"])
@rate_limit(requests=100, window=60)
def handle_command():
    # existing code

@app.route("/api/tools/execute", methods=["POST"])
@rate_limit(requests=50, window=60)
def execute_tool():
    # existing code
```

---

## ⏱️ TOTAL TIME

- Phase 1 (Amazon Q): 30 min
- Phase 2 (3 reviews): 30 min
- Phase 3 (Integration): 15 min
- **Total: 2 hours** ✅

---

**READY TO START? Tell me when Amazon Q has the template ready!**
