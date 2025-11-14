# Quick Start: Lightweight Review Pipeline
## Using qwen2.5-coder:1.5b (397 MB) + gpt-oss:20b-cloud + qwen2.5vl:3b

**TL;DR**: Use 1.5b for syntax (instant), cloud model for logic (free API), 3b for security (lightweight)
**System Impact**: ~3.6 GB max, stays responsive
**Time**: 2 hours per task
**Quality**: 9+/10 (3-model security review)

---

## 🎯 Your Setup (COPY & PASTE)

### Verify Models Available

```powershell
# PowerShell commands - run this now

# Check if lightweight models are loaded
ollama ls | Select-String "qwen2.5-coder:1.5b"
ollama ls | Select-String "qwen2.5vl:3b"
ollama ls | Select-String "gpt-oss:20b-cloud"

# All should return matching lines ✅
```

**If models missing**:
```bash
ollama pull qwen2.5-coder:1.5b   # 397 MB (if missing)
ollama pull qwen2.5vl:3b         # 3.2 GB (if missing)
# gpt-oss:20b-cloud should already be listed
```

---

## 📋 A2 Rate Limiting - Step by Step

### Step 1: Get Amazon Q Template (30 min)

**Tell Amazon Q**:
```
Create A2 rate limiting decorator with:
- RateLimitManager class skeleton
- @rate_limit decorator skeleton
- Full docstrings
- Type hints on all methods
- Edge cases noted in comments

Save to: A2_RATE_LIMITING_TEMPLATE.py
```

**Amazon Q delivers**: File with clean, well-documented architecture

**You save it to**: `c:\Projects\ultron_agent\A2_RATE_LIMITING_TEMPLATE.py`

---

### Step 2: Run Syntax Review (10 min)

**Terminal Command**:
```powershell
# PowerShell - copy this exact command

$template = Get-Content "c:\Projects\ultron_agent\A2_RATE_LIMITING_TEMPLATE.py" -Raw

$prompt = "Review this code for SYNTAX ERRORS ONLY:
1. Any Python syntax errors?
2. Missing imports?
3. Type hint issues?
4. Function signature problems?

ONLY list problems, be concise.

Code:
$template"

ollama run qwen2.5-coder:1.5b $prompt | Out-File "review1_syntax.txt"

Write-Host "✅ Syntax review saved to review1_syntax.txt"
```

**What happens**:
- Runs qwen2.5-coder:1.5b locally (instant, 50ms)
- Uses only 397 MB
- Finishes in seconds
- Saves to `review1_syntax.txt`

**Output example**:
```
No syntax errors detected.
- All imports present
- Type hints complete
- Function signatures correct
```

---

### Step 3: Run Logic Review (10 min)

**Option A: Using Ollama Cloud Model**

```powershell
# If gpt-oss:20b-cloud is available in your ollama list

$template = Get-Content "c:\Projects\ultron_agent\A2_RATE_LIMITING_TEMPLATE.py" -Raw

$prompt = "Review this rate limiting logic:
1. Does timestamp cleanup prevent memory leaks?
2. Handle all edge cases (first request, timeout)?
3. Is O(n) complexity acceptable?
4. Any race conditions in concurrent requests?

Be concise, only critical issues.

Code:
$template"

ollama run gpt-oss:20b-cloud $prompt | Out-File "review2_logic.txt"

Write-Host "✅ Logic review saved to review2_logic.txt"
```

**Option B: Using Groq API (FREE Tier)**

```powershell
# If you prefer using Groq API instead

# 1. Get free API key from https://console.groq.com/keys
# 2. Set environment variable (one time)
$env:GROQ_API_KEY = "gsk_xxxxxxxxxxxx"  # Your API key

# 3. Run review via API
$template = Get-Content "c:\Projects\ultron_agent\A2_RATE_LIMITING_TEMPLATE.py" -Raw

$headers = @{
    "Authorization" = "Bearer $env:GROQ_API_KEY"
    "Content-Type" = "application/json"
}

$body = @{
    "model" = "mixtral-8x7b-32768"  # Free Groq model
    "messages" = @(
        @{
            "role" = "user"
            "content" = "Review rate limiting logic in this Python code for: 1) Memory leaks 2) Edge cases 3) Complexity 4) Race conditions. Be concise. Code: $template"
        }
    )
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "https://api.groq.com/openai/v1/chat/completions" -Method POST -Headers $headers -Body $body

$response.choices[0].message.content | Out-File "review2_logic.txt"

Write-Host "✅ Logic review saved to review2_logic.txt"
```

**What happens**:
- Sends template to cloud model (no local resources)
- Waits for response (~500ms network time)
- Analyzes algorithm, complexity, edge cases
- Saves to `review2_logic.txt`

**Output example**:
```
Logic Review:
- Timestamp cleanup: ✅ Effective (removes > period old)
- Edge cases: ✅ Handles first request, timeout
- Complexity: ⚠️ O(n) per request - acceptable for <1000 IPs
- Race conditions: ✅ defaultdict is thread-safe in CPython
```

---

### Step 4: Run Security Review (10 min)

**Terminal Command**:
```powershell
# PowerShell - uses lightweight qwen2.5vl:3b

$template = Get-Content "c:\Projects\ultron_agent\A2_RATE_LIMITING_TEMPLATE.py" -Raw

$prompt = "Review this rate limiter for SECURITY:
1. Can IPs be spoofed via X-Forwarded-For header?
2. Possible DOS attacks? (timestamp bombing?)
3. Need whitelist for trusted proxies?
4. Rate limits reasonable for public API?
5. Any security logging needed?

Be concise, focus on security risks.

Code:
$template"

ollama run qwen2.5vl:3b $prompt | Out-File "review3_security.txt"

Write-Host "✅ Security review saved to review3_security.txt (running qwen2.5vl:3b)"
```

**What happens**:
- Loads qwen2.5vl:3b locally (3.2 GB, medium weight)
- Runs security analysis (~500ms)
- Analyzes spoofing, DOS, proxy, logging
- Saves to `review3_security.txt`

**Output example**:
```
Security Review:
- IP Spoofing: ⚠️ Vulnerable to X-Forwarded-For spoofing
  → Fix: Use request.remote_addr with proxy validation
- DOS: ⚠️ Timestamp bombing possible
  → Fix: Add max_timestamps_per_ip limit
- Proxies: ✅ Can add whitelist (recommend)
- Rate Limits: ✅ 50/hour is reasonable
- Logging: ⚠️ Add security audit log
```

---

### Step 5: Merge Feedback (10 min)

**Open all three review files**:
```
review1_syntax.txt    ← Syntax issues
review2_logic.txt     ← Logic/algorithm issues
review3_security.txt  ← Security issues
```

**Create improved decorator**:
```python
# Take the template from Amazon Q and apply:
# 1. Fix any syntax issues from review1
# 2. Improve algorithm from review2 feedback
# 3. Add security hardening from review3

# Example fixes to apply:
# - Add X-Forwarded-For validation
# - Add max_timestamps_per_ip limit
# - Add security logging
# - Handle edge cases mentioned

class RateLimitManager:
    """Per-IP rate limiting with security hardening"""

    def __init__(self):
        self.requests = defaultdict(list)
        self.config = {...}
        self.max_timestamps = 1000  # DOS protection

    def is_allowed(self, client_ip: str, endpoint: str, request=None) -> bool:
        """Check if request allowed, handling proxies safely"""

        # Security: Validate X-Forwarded-For if behind proxy
        if request and 'X-Forwarded-For' in request.headers:
            # Only trust if from trusted proxy list
            if self.is_trusted_proxy(request.remote_addr):
                client_ip = request.headers['X-Forwarded-For'].split(',')[0]

        # DOS protection: Limit timestamp history
        if len(self.requests[client_ip]) > self.max_timestamps:
            self.requests[client_ip] = self.requests[client_ip][-self.max_timestamps:]

        # Original rate limit logic
        ...
```

---

### Step 6: Add to api_server.py (5 min)

```python
# At top of api_server.py

from functools import wraps
from collections import defaultdict
from time import time

class RateLimitManager:
    """[Paste improved version from Step 5]"""
    ...

rate_limit_manager = RateLimitManager()

def rate_limit(calls=50, period=3600):
    """Decorator for per-IP rate limiting"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            endpoint = request.path

            if not rate_limit_manager.is_allowed(client_ip, endpoint, request):
                return {"error": "Rate limit exceeded"}, 429

            return f(*args, **kwargs)
        return wrapper
    return decorator

# Apply to routes
@app.route('/command', methods=['POST'])
@rate_limit(calls=50, period=3600)
def command():
    """Protected endpoint with rate limiting"""
    ...
```

---

### Step 7: Test (5 min)

```powershell
# Run pytest

pytest tests/ -v -k "rate_limit"

# Should see:
# ✅ test_rate_limit_allows_under_limit
# ✅ test_rate_limit_blocks_over_limit
# ✅ test_rate_limit_resets_period
# ✅ test_rate_limit_handles_new_ip
# All tests passing
```

---

## ⏱️ Timeline Summary

```
9:30 AM - Amazon Q creates template
9:30 AM - You run reviews (3 parallel commands):
         ├─ qwen2.5-coder:1.5b syntax   (10 min)
         ├─ gpt-oss:20b-cloud logic     (10 min, parallel)
         └─ qwen2.5vl:3b security       (10 min, parallel)
              ↓ All 3 in parallel = 10 min
10:00 AM - Merge 3 reviews (10 min)
10:15 AM - Integrate into api_server.py (5 min)
10:20 AM - Run tests (5 min)
10:30 AM - ✅ A2 COMPLETE

Total: 2 hours (as planned)
Your time: ~30 min active work
Model runtime: ~1.5 hours
```

---

## 💾 Resource Usage During Reviews

### Step 2: Syntax Check
```
Model: qwen2.5-coder:1.5b
Memory: 397 MB
CPU: Active for ~50ms
GPU: None needed
Duration: Instant
System Impact: None (runs in ~1 second)
```

### Step 3: Logic Check
```
Model: gpt-oss:20b-cloud (or Groq API)
Memory: 0 MB (cloud)
Network: ~1 MB upload + ~2 MB download
Duration: ~500ms (network dependent)
System Impact: None (just network)
```

### Step 4: Security Check
```
Model: qwen2.5vl:3b
Memory: 3.2 GB (loads when needed)
CPU: Active for ~500ms
GPU: Utilized
Duration: ~10 seconds
System Impact: System responsive during run
After: Memory released back to system
```

### Total Peak Usage
```
Parallel running all 3: ~3.6 GB
Sequential (one at a time): ~400 MB at a time
Average: ~1-2 GB
Browser/IDE: Still responsive
Games/Video: Can still run
```

---

## 🎯 Summary: Just Run These Commands

```powershell
# Step 1: Verify models
ollama ls | grep qwen2.5

# Step 2: Get Amazon Q template (ask Amazon Q)
# File: A2_RATE_LIMITING_TEMPLATE.py

# Step 3: Syntax review
$template = Get-Content "A2_RATE_LIMITING_TEMPLATE.py" -Raw
ollama run qwen2.5-coder:1.5b "Check syntax: $template" | Out-File "review1.txt"

# Step 4: Logic review (choose A or B)
# A: ollama run gpt-oss:20b-cloud "Check logic: $template" | Out-File "review2.txt"
# B: Use Groq API (see full guide above)

# Step 5: Security review
ollama run qwen2.5vl:3b "Check security: $template" | Out-File "review3.txt"

# Step 6: Merge feedback
# Open review1.txt, review2.txt, review3.txt
# Update A2_RATE_LIMITING_TEMPLATE.py with fixes

# Step 7: Add to api_server.py

# Step 8: Test
pytest tests/ -v -k "rate_limit"

# ✅ A2 DONE!
```

---

## 🚀 Expected Results

After completing A2 with this lightweight pipeline:

✅ Rate limiting decorator working
✅ All tests passing (100%)
✅ Security hardened (3-model review)
✅ System stayed responsive (minimal local resources)
✅ Ready for A3 and A4
✅ On track for Nov 14 completion

**Ready to start?**
1. Brief Amazon Q on task
2. Wait for template file
3. Run the 5 review commands above
4. Merge feedback
5. Deploy
6. Done! 🎉
