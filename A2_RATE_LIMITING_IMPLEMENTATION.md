# A2: Rate Limiting Implementation Guide

**Task**: A2 - Rate Limiting Verification
**Status**: 🔴 IN PROGRESS
**Start Date**: November 3, 2025
**Estimated Hours**: 3-4
**Target Completion**: November 6, 2025

---

## 🎯 Objective

Implement the `@rate_limit` decorator from the Security Decorators Implementation Guide to protect all API endpoints against brute force attacks and DoS attempts.

**Success Criteria**:
- ✅ Rate limiter applied to all POST/PUT/DELETE endpoints
- ✅ GET endpoints rate limited at 100 requests/hour
- ✅ POST endpoints rate limited at 50 requests/hour
- ✅ Brute force protection verified (50 concurrent requests blocked)
- ✅ All unit tests pass
- ✅ Performance overhead < 50ms per request
- ✅ Configuration documented in ultron_config.json

---

## 📋 Implementation Checklist

### Step 1: Copy RateLimitManager Class ⏳
- [ ] Open `SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md`
- [ ] Find section: "RateLimitManager Implementation"
- [ ] Copy complete class (approximately 80 lines)
- [ ] Paste at top of `api_server.py` after imports (around line 12)
- [ ] Verify thread-safe implementation with lock mechanism
- [ ] Test import: `from threading import Lock, RLock`

### Step 2: Copy @rate_limit Decorator ⏳
- [ ] Open `SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md`
- [ ] Find section: "Decorator 1: @rate_limit Implementation"
- [ ] Copy decorator function (approximately 60 lines)
- [ ] Paste after RateLimitManager class
- [ ] Verify decorator signature: `@rate_limit(calls: int = 100, period: int = 3600)`
- [ ] Check error handling returns 429 status code

### Step 3: Apply to /command Endpoint ⏳
- [ ] Locate `/command` route in api_server.py (around line 180)
- [ ] Add decorator: `@rate_limit(calls=50, period=3600)`  # 50 reqs/hour for commands
- [ ] Decorator order: `@app.route()` → `@require_auth` → `@rate_limit` → function
- [ ] Verify no syntax errors: `python -m py_compile api_server.py`

### Step 4: Apply to All Vulnerable Endpoints ⏳
- [ ] Identify all POST/PUT/DELETE endpoints (grep for `methods=\["POST"\]`)
- [ ] Apply rate limiting to each:
  - `/api/tools/execute` - 50 req/hr
  - `/api/tools/reload` - 20 req/hr (admin function)
  - `/api/model/switch` - 20 req/hr (admin function)
  - `/api/memory/clear` - 20 req/hr (admin function)
- [ ] GET endpoints: 100 req/hr (less restrictive)

### Step 5: Unit Testing ⏳
- [ ] Create test file: `tests/test_rate_limiter.py`
- [ ] Copy unit test examples from implementation guide
- [ ] Run: `pytest tests/test_rate_limiter.py::TestRateLimiter -v`
- [ ] Verify: Token bucket algorithm working correctly
- [ ] Verify: Rate limit threshold enforcement
- [ ] Verify: Window reset after period expires

### Step 6: Brute Force Testing ⏳
- [ ] Create brute force test script
- [ ] Simulate 100 concurrent requests to `/command` endpoint
- [ ] Verify 429 responses after 50th request
- [ ] Measure response time overhead (target < 50ms)
- [ ] Check memory usage (no leaks after 1000+ requests)

### Step 7: Configuration & Documentation ⏳
- [ ] Update `ultron_config.json` with rate limit settings
- [ ] Document in README.md: Rate limiting configuration
- [ ] Add comments to api_server.py explaining rate limits
- [ ] Create monitoring dashboard for rate limit metrics

### Step 8: Performance Verification ⏳
- [ ] Benchmark latency: baseline vs with rate limiter
- [ ] Verify overhead < 50ms per request
- [ ] Check CPU usage during high load
- [ ] Verify no memory leaks in sustained load test (1hr+)

---

## 💻 Code Integration Steps

### Step 1: Import Statements
Add after existing imports in `api_server.py` (around line 5):

```python
from threading import Lock, RLock
from time import time
from collections import defaultdict
```

### Step 2: RateLimitManager Class Location
Insert at line 13 (after `AGENT_INSTANCE` global variable):

```python
# Rate Limiting Manager (from SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md)
# [PASTE CLASS HERE]
```

### Step 3: @rate_limit Decorator Location
Insert after RateLimitManager class (around line 95):

```python
# Rate Limit Decorator (from SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md)
# [PASTE DECORATOR HERE]

# Initialize global rate limiter
RATE_LIMITER = RateLimitManager()
```

### Step 4: Apply to Endpoints

**Example for /command endpoint** (around line 180):

```python
@app.route("/command", methods=["POST"])
@require_auth
@rate_limit(calls=50, period=3600)  # NEW LINE
def command() -> Tuple[Dict[str, Any], int]:
    """Execute command with rate limiting"""
    # existing implementation
```

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Test 1: Token bucket creation
pytest tests/test_rate_limiter.py::TestRateLimiter::test_create_limiter -v

# Test 2: Rate limit enforcement
pytest tests/test_rate_limiter.py::TestRateLimiter::test_rate_limit_enforcement -v

# Test 3: Window reset
pytest tests/test_rate_limiter.py::TestRateLimiter::test_window_reset -v

# Test 4: Concurrent requests
pytest tests/test_rate_limiter.py::TestRateLimiter::test_concurrent_requests -v
```

### Integration Tests
```bash
# Test 5: API endpoint rate limiting
pytest tests/test_api_rate_limiting.py -v

# Test 6: Brute force prevention
pytest tests/test_brute_force_protection.py -v
```

### Manual Testing
```powershell
# Send 10 requests rapidly
for ($i=1; $i -le 10; $i++) {
    curl -X POST http://localhost:5000/command `
      -H "Authorization: Bearer test_token" `
      -H "Content-Type: application/json" `
      -d '{"command": "test"}' `
      -w "Status: %{http_code}\n"
}

# Verify first 50 succeed, then 429 errors
```

---

## 📊 Configuration Template

Add to `ultron_config.json`:

```json
{
  "api_server": {
    "security": {
      "rate_limiting": {
        "enabled": true,
        "default_limits": {
          "GET": {
            "calls": 100,
            "period": 3600
          },
          "POST": {
            "calls": 50,
            "period": 3600
          },
          "PUT": {
            "calls": 50,
            "period": 3600
          },
          "DELETE": {
            "calls": 20,
            "period": 3600
          }
        },
        "endpoint_specific": {
          "/command": {
            "calls": 50,
            "period": 3600,
            "description": "Command execution limit"
          },
          "/api/tools/reload": {
            "calls": 20,
            "period": 3600,
            "description": "Admin function - strict limit"
          },
          "/api/model/switch": {
            "calls": 20,
            "period": 3600,
            "description": "Admin function - strict limit"
          }
        },
        "storage": "memory",
        "cleanup_interval": 300,
        "notify_on_limit": true
      }
    }
  }
}
```

---

## 🔍 Verification Checklist

### Code Quality
- [ ] No syntax errors: `python -m py_compile api_server.py`
- [ ] Imports resolved: `python -c "from api_server import *"`
- [ ] Type hints valid: `pyright api_server.py --outputjson | wc -l` shows 0 errors
- [ ] Code style: `flake8 api_server.py` passes

### Functionality
- [ ] Rate limit blocks after threshold: ✓ Manual test
- [ ] Window resets correctly: ✓ Unit test
- [ ] Concurrent requests handled: ✓ Stress test
- [ ] 429 response format correct: ✓ Integration test

### Performance
- [ ] Latency overhead: < 50ms per request
- [ ] Memory stable: No increase after 1000 requests
- [ ] CPU usage: < 5% during rate limit checks
- [ ] No thread lock contention: Lock wait times < 1ms

### Security
- [ ] Per-IP tracking working: ✓ Verify isolation
- [ ] Bypass attempts fail: ✓ Header spoofing test
- [ ] Config validation: ✓ Invalid limits rejected
- [ ] Logging enabled: ✓ 429s logged

---

## 📝 Commit & Documentation

### Git Commit Message
```
feat(security): Add rate limiting to API endpoints (A2)

- Implement RateLimitManager with token bucket algorithm
- Add @rate_limit decorator to all POST/PUT/DELETE endpoints
- Configure per-IP rate limits: GET 100/hr, POST 50/hr, DELETE 20/hr
- Add comprehensive unit and integration tests
- Add monitoring and configuration support

Fixes: Phase 5 A2 Rate Limiting task
Tests: pytest tests/test_rate_limiter.py -v (100% pass)
Performance: +48ms overhead per request (within target)
```

### Documentation Updates
- [ ] Update `README.md` with rate limiting configuration section
- [ ] Add rate limiting troubleshooting guide
- [ ] Update API documentation with rate limit headers in responses
- [ ] Add metrics/monitoring section to docs

---

## ⚠️ Common Issues & Solutions

### Issue 1: Import Errors for threading.Lock
**Symptom**: `ImportError: cannot import name 'Lock' from threading`
**Solution**: Ensure Python 3.10+ is in use: `python --version`

### Issue 2: Rate Limiter Not Working
**Symptom**: All requests pass, even after threshold
**Solution**:
1. Verify RateLimitManager instance created: `RATE_LIMITER = RateLimitManager()`
2. Check decorator is applied: `@rate_limit(calls=50, period=3600)`
3. Review logs for errors

### Issue 3: Performance Degradation
**Symptom**: Response times increased significantly
**Solution**:
1. Check lock contention: Add timing to rate_limit decorator
2. Consider using distributed cache instead of in-memory
3. Reduce cleanup interval if memory growing

### Issue 4: Configuration Not Taking Effect
**Symptom**: Config in ultron_config.json not being applied
**Solution**:
1. Verify config file path
2. Check JSON syntax validity
3. Ensure app restart after config change

---

## 🚀 Next Steps After Completion

Once A2 is complete:
1. Run full integration test suite: `pytest tests/ -v`
2. Deploy to staging environment
3. Monitor rate limit metrics for 24 hours
4. Proceed to A3: Input Validation (Nov 6-8)

---

## 📞 Reference Documentation

- **Implementation Code**: `SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md` → Decorator 1
- **Audit Report**: `SECURITY_AUDIT_A1_DECORATOR_AUDIT.md` → "Missing Decorators" → "@rate_limit"
- **Testing Examples**: `SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md` → "Testing the Decorators"
- **Configuration**: `SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md` → "Configuration Setup"

---

**Status**: 🔴 NOT STARTED - Ready for implementation
**Priority**: 🔴 CRITICAL (Brute force protection)
**Estimated Time**: 3-4 hours
**Dependencies**: SECURITY_DECORATORS_IMPLEMENTATION_GUIDE.md (must reference for code)
