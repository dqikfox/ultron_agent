# 🚀 A2: RATE LIMITING - EXECUTION GUIDE

**Status**: Ready to START NOW
**Time**: 2 hours
**Approach**: 3-model parallel review (lightweight)
**Goal**: Implement @rate_limit decorator in api_server.py

---

## 📊 THE PIPELINE

```
[Amazon Q]
   ↓ (30 min)
Create @rate_limit template
   ↓
[3 Parallel Reviews]
   ├─ qwen2.5-coder:1.5b  → Syntax check (10 min)
   ├─ gpt-oss:20b-cloud   → Logic verify (10 min)
   └─ qwen2.5vl:3b        → Security check (10 min)
   ↓
[Integration]
   ↓ (15 min)
Merge feedback → Update api_server.py → Test
   ↓
✅ A2 COMPLETE
```

---

## 🎯 PHASE 1: AMAZON Q ARCHITECTURE (30 minutes)

### Task for Amazon Q:

```
Create a @rate_limit decorator for rate limiting API endpoints.

Requirements:
1. Implement token bucket algorithm (not sliding window)
2. Support per-IP rate limiting
3. Support per-user rate limiting
4. Include IP whitelist bypass
5. Store limits in memory (not database)
6. Return 429 Too Many Requests when limit exceeded
7. Include X-RateLimit-* headers in response
8. Thread-safe implementation
9. Complete docstrings for all functions
10. Type hints on all parameters

Create a complete, production-ready template ready for code review.
Include example usage in api_server.py showing @rate_limit(requests=100, window=60).
```

### Expected Output:
Amazon Q creates file: `A2_RATE_LIMITING_TEMPLATE.py`

Contains:
- `RateLimitManager` class with token bucket
- `@rate_limit` decorator
- Helper functions (check_limit, reset_old_windows, etc.)
- Docstrings + type hints
- Example usage code

**Save this to**: `A2_RATE_LIMITING_TEMPLATE.py`

---

## 🧪 PHASE 2: 3-MODEL PARALLEL REVIEWS (30 minutes total)

### Review 1: Syntax Check (qwen2.5-coder:1.5b) - 10 min

**In PowerShell Terminal**:

```powershell
# Read the Amazon Q template
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw

# Request syntax check
$prompt = @"
Check this Python code for syntax errors, import issues, and type hint completeness:

$template

Return:
1. Any syntax errors found
2. Missing or incorrect imports
3. Incomplete or wrong type hints
4. Function signature issues
5. Any other Python standard violations
"@

ollama run qwen2.5-coder:1.5b $prompt > review1_syntax.txt

# Show output
Get-Content review1_syntax.txt
```

**Expected Output** (~2-3 lines):
```
✓ Syntax: Valid Python 3.8+
✓ Imports: All required (threading, time, functools)
✓ Type hints: Complete on all parameters and returns
✓ Signatures: Match decorator pattern correctly
```

---

### Review 2: Logic Verification (gpt-oss:20b-cloud) - 10 min

**In PowerShell Terminal** (same window):

```powershell
# Read the template again
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw

# Request logic verification
$prompt = @"
Verify the rate limiting logic in this code. Check for:

1. Is the token bucket algorithm correctly implemented?
2. Will timestamp cleanup prevent memory leaks?
3. Does it handle edge cases (clock skew, concurrent requests)?
4. Is the IP detection reliable?
5. What about race conditions in thread access?

Code to review:
$template

Return specific line numbers and issues found.
"@

ollama run gpt-oss:20b-cloud $prompt > review2_logic.txt

# Show output
Get-Content review2_logic.txt
```

**Expected Output** (~5-10 lines):
```
Line 23: Token bucket looks correct - refill rate is calculated properly
Line 45: Consider adding lock timeout to prevent deadlock
Line 67: IP detection uses X-Forwarded-For - good for proxies
Line 89: Race condition possible in concurrent requests - recommend RLock instead of Lock
Line 112: Timestamp cleanup looks effective for memory management
...
```

---

### Review 3: Security Review (qwen2.5vl:3b) - 10 min

**In PowerShell Terminal** (same window):

```powershell
# Read the template
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw

# Request security review
$prompt = @"
Security review of this rate limiting decorator. Check for:

1. IP spoofing vulnerabilities - can client send fake X-Forwarded-For?
2. DOS attack surface - is it vulnerable to header flooding?
3. Whitelist bypass - can attacker craft headers to bypass IP whitelist?
4. User ID bypass - can user manipulate user_id parameter?
5. Side-channel attacks - does timing reveal rate limit status?
6. Memory exhaustion - can attacker create new IPs to exhaust memory?

Code to review:
$template

Return security concerns with severity (HIGH/MEDIUM/LOW).
"@

ollama run qwen2.5vl:3b $prompt > review3_security.txt

# Show output
Get-Content review3_security.txt
```

**Expected Output** (~5-10 lines):
```
MEDIUM: X-Forwarded-For can be spoofed - recommend IP header validation
HIGH: No user_id validation - can attacker submit false user IDs?
MEDIUM: Memory could grow unbounded with many unique IPs - add max buckets limit
LOW: Headers leak rate limit status - not a security issue but privacy concern
MEDIUM: Consider IP header validation against trusted proxy list
...
```

---

## ✅ PHASE 3: INTEGRATION & DEPLOYMENT (15 minutes)

### Step 1: Merge Feedback (5 min)

**Read all three reviews**:
```powershell
Write-Host "=== SYNTAX REVIEW ===" -ForegroundColor Yellow
Get-Content review1_syntax.txt

Write-Host "`n=== LOGIC REVIEW ===" -ForegroundColor Yellow
Get-Content review2_logic.txt

Write-Host "`n=== SECURITY REVIEW ===" -ForegroundColor Yellow
Get-Content review3_security.txt
```

### Step 2: Create Final Decorator (3 min)

**Based on feedback, refine A2_RATE_LIMITING_TEMPLATE.py**:

Key fixes to apply:
1. Use `threading.RLock()` instead of `Lock()` (from logic review)
2. Add IP header validation (from security review)
3. Add max_buckets limit to prevent memory exhaustion (from security review)
4. Validate user_id parameter (from security review)

**Updated decorator location**: `api_server.py` (add to imports and RateLimitManager class)

### Step 3: Apply to API Endpoints (5 min)

**In api_server.py**, add imports:

```python
from A2_RATE_LIMITING_TEMPLATE import rate_limit, RateLimitManager
```

**Add decorator to key endpoints**:

```python
@app.route("/api/command", methods=["POST"])
@rate_limit(requests=100, window=60)  # 100 requests per 60 seconds
def handle_command():
    # existing code
    pass

@app.route("/api/tools/execute", methods=["POST"])
@rate_limit(requests=50, window=60)  # 50 requests per 60 seconds
def execute_tool():
    # existing code
    pass

@app.route("/health", methods=["GET"])
@rate_limit(requests=1000, window=60)  # Health checks are cheap
def health_check():
    # existing code
    pass
```

### Step 4: Test Rate Limiting (2 min)

```powershell
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Simulate requests
for ($i = 1; $i -le 110; $i++) {
    $response = curl -X POST http://localhost:5000/api/command `
        -H "Content-Type: application/json" `
        -d '{"command": "test"}'

    if ($i -eq 101) {
        Write-Host "Request $i (should get 429):" -ForegroundColor Red
    } else {
        Write-Host "Request $i: OK" -ForegroundColor Green
    }

    if ($response -match "429") {
        Write-Host "✅ Rate limiting working! Got 429 Too Many Requests" -ForegroundColor Green
        break
    }
}
```

**Expected**: First 100 requests succeed, request 101+ returns `429 Too Many Requests`

### Step 5: Run Tests (Optional but recommended)

```powershell
# Create test file: tests/test_rate_limiting.py
# Run: pytest tests/test_rate_limiting.py

pytest -v tests/test_rate_limiting.py
```

---

## 📋 QUICK CHECKLIST

- [ ] **Phase 1**: Amazon Q created template (30 min)
  - [ ] Save to `A2_RATE_LIMITING_TEMPLATE.py`
  - [ ] Review file syntax (runs without errors)

- [ ] **Phase 2**: Run 3 reviews (30 min)
  - [ ] Syntax check with qwen2.5-coder:1.5b
  - [ ] Logic check with gpt-oss:20b-cloud
  - [ ] Security check with qwen2.5vl:3b
  - [ ] Save all 3 outputs (review1_syntax.txt, review2_logic.txt, review3_security.txt)

- [ ] **Phase 3**: Integration (15 min)
  - [ ] Merge feedback into decorator
  - [ ] Add @rate_limit to api_server.py endpoints
  - [ ] Test rate limiting (curl loop)
  - [ ] Verify 429 responses work
  - [ ] Run pytest (optional)

- [ ] **Final**: Mark A2 COMPLETE ✅

---

## 🎯 SUCCESS CRITERIA

✅ **A2 Rate Limiting Complete When**:
1. `A2_RATE_LIMITING_TEMPLATE.py` exists and is syntactically correct
2. 3 model reviews completed with feedback
3. `@rate_limit` decorator added to api_server.py
4. At least 2 endpoints protected (e.g., /api/command, /api/tools/execute)
5. Manual test shows 429 response on rate limit exceed
6. pytest passes all tests (optional but recommended)

---

## ⏱️ TIMELINE

```
NOW:        Phase 1 starts (Amazon Q)
+30 min:    Phase 1 done → Phase 2 starts
+60 min:    Phase 2 done → Phase 3 starts
+75 min:    Phase 3 done
✅ 2 HOURS: A2 COMPLETE
```

---

## 🚀 READY?

1. Brief Amazon Q on the task (copy task description above)
2. Wait for template
3. Run the 3 model reviews in PowerShell
4. Integrate feedback
5. Test with curl loop
6. Done! ✅

**Start with Amazon Q now!** Template should be ready in 30 minutes. 🎯
