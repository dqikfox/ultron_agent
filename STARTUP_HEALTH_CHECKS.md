# ULTRON Agent - Startup Health Checks

**Updated**: October 24, 2025

## Overview

The `run.bat` launcher now includes **comprehensive health checks** that validate Ollama integration before starting the system. These tests ensure all critical components are working correctly at launch.

---

## Startup Sequence

### Phase 1: Cleanup
1. **Process Termination**: Kills any existing ULTRON Python processes
2. **Port Liberation**: Frees ports 8080 and 5175 from any conflicting processes
3. **Wait Period**: 2-second cooldown for clean shutdown

### Phase 2: Pre-flight Checks
1. ✅ Verify required files exist (`web_gui_server.py`, `main.py`, `ultron_config.json`)
2. ✅ Check GUI files (`gui/ultron_enhanced/web/index.html`)
3. ✅ Validate Python installation
4. ✅ Verify Python version

### Phase 3: Ollama Service
1. **Service Detection**: Check if Ollama is already running
2. **Auto-Start**: Launch Ollama if not running
3. **Retry Logic**: 5 connection attempts with 3-second intervals
4. **Validation**: Confirm service responding on port 11434

### Phase 4: Health Tests (NEW)
Comprehensive 5-test suite that validates Ollama integration:

#### Test 1: Service Availability ✅
- **Purpose**: Verify Ollama HTTP service is responding
- **Method**: GET request to `/api/tags`
- **Pass Criteria**: Successful response received
- **Log**: Test result logged to `ultron_master_startup.log`

#### Test 2: Model Availability ✅
- **Purpose**: Confirm llava model is loaded
- **Method**: Query available models
- **Pass Criteria**: Model matching `llava*` found
- **Log**: Model detection logged

#### Test 3: Text Generation ✅
- **Purpose**: Validate basic generation capability
- **Method**: POST to `/api/generate` with simple prompt
- **Timeout**: 15 seconds
- **Pass Criteria**: Response `done=true`
- **Log**: Generation result logged

#### Test 4: Chat API ✅
- **Purpose**: Verify conversational AI endpoint
- **Method**: POST to `/api/chat` with user message
- **Timeout**: 15 seconds
- **Pass Criteria**: Response `done=true` with assistant message
- **Log**: Chat result logged

#### Test 5: Context Retention ✅
- **Purpose**: Ensure multi-turn conversation memory works
- **Method**: 3-message conversation testing recall
- **Pass Criteria**: Response contains previously mentioned code "123"
- **Log**: Context test result logged

### Phase 5: Test Summary
- **Results Display**: Shows passed/failed count (X/5)
- **Log Entry**: Writes complete summary to log file
- **User Prompt**: If any test fails:
  - ⚠️ Warning displayed
  - User choice: Continue (Y) or Exit (N)
- **Auto-Continue**: All tests pass → proceeds automatically

### Phase 6: Python Validation
- **Syntax Check**: Validates `web_gui_server.py` and `main.py`
- **Error Handling**: Exits if syntax errors detected

### Phase 7: Service Startup
1. **Web GUI**: Launches on port 8080
2. **Frontend UI**: Launches on port 5175
3. **Health Checks**: Validates each service with HTTP requests

### Phase 8: Completion
- **Status Display**: Shows all service URLs and ports
- **Log Summary**: Records complete startup sequence
- **User Notification**: "Press any key to exit launcher"

---

## Log File Structure

All test results are logged to `ultron_master_startup.log`:

```
[TEST] ================================================
[TEST] Starting Ollama Health Checks
[TEST] Test 1 PASSED - Service availability
[TEST] Test 2 PASSED - Model available
[TEST] Test 3 PASSED - Generation successful
[TEST] Test 4 PASSED - Chat successful
[TEST] Test 5 PASSED - Context retained
[TEST] ================================================
[TEST] Summary: Passed=5 Failed=0
[TEST] ================================================
```

---

## Error Handling

### Test Failure Scenarios

**Scenario 1: Ollama Service Not Running**
- Test 1 fails
- Error message displayed
- User prompted to continue or exit
- **Recovery**: Start Ollama manually or let auto-start fix it

**Scenario 2: Model Not Loaded**
- Test 2 fails
- Error message displayed
- **Recovery**: Pull model with `ollama pull llava:7b`

**Scenario 3: Generation Timeout**
- Test 3 or 4 fails (15-second timeout)
- Error logged
- **Recovery**: Check system resources, restart Ollama

**Scenario 4: Context Memory Issue**
- Test 5 fails
- Context retention not working
- **Recovery**: System may still work for single-turn conversations

### User Decision Points

When tests fail, user sees:
```
[WARN] ⚠️  Some tests failed. System may not work correctly.
[WARN] Check ultron_master_startup.log for details.

[PROMPT] Press Y to continue anyway, or any other key to exit...
Continue? (Y/N):
```

**Choice Y**: System continues startup (use for debugging)
**Choice N**: Startup aborted (recommended if critical tests fail)

---

## Performance Expectations

### Typical Startup Times
- **Cleanup**: ~2 seconds
- **Pre-flight checks**: <1 second
- **Ollama detection**: 3-10 seconds (if starting)
- **Health tests**: 20-40 seconds (depends on model warmup)
  - First run: ~30s (model loading)
  - Subsequent runs: ~10s (cached model)
- **Service launch**: 5-8 seconds
- **Total**: 40-60 seconds first run, 25-35 seconds cached

### Test Timeouts
- Each generation/chat test: **15 seconds max**
- Service availability tests: **Instant**
- Port checks: **<1 second**

---

## Benefits

### For Developers
✅ **Early Detection**: Catches Ollama issues before GUI loads
✅ **Detailed Logs**: Complete test results in log file
✅ **Debugging Aid**: Know exactly which component failed
✅ **Time Saving**: No need to wait for GUI to discover backend issues

### For Production
✅ **Reliability**: Validates system health before user interaction
✅ **Confidence**: All tests pass = system ready
✅ **Graceful Degradation**: Option to continue with warnings
✅ **Audit Trail**: Complete startup history in logs

---

## Troubleshooting

### Common Issues

**Issue**: "Test 1 FAILED - Ollama service not responding"
- **Cause**: Ollama service crashed or port conflict
- **Fix**: Kill Ollama processes and restart run.bat

**Issue**: "Test 3 FAILED - Text generation error"
- **Cause**: Model loading timeout or insufficient memory
- **Fix**: Wait for model to fully load, check available RAM

**Issue**: All tests timeout
- **Cause**: Network/firewall blocking localhost
- **Fix**: Check Windows Firewall, disable VPN

**Issue**: Tests pass but GUI fails
- **Cause**: Port conflict on 8080 or 5175
- **Fix**: Cleanup phase should handle this, check logs

---

## Advanced Usage

### Skip Health Checks (Not Recommended)
To bypass health checks for development:
1. Comment out lines in run.bat:
   ```batch
   :: :: 5. Run comprehensive Ollama health tests
   :: [Comment out entire test section]
   ```
2. **Warning**: May start with broken backend

### Custom Test Timeout
Change timeout in run.bat:
```batch
:: Default: -TimeoutSec 15
:: Faster: -TimeoutSec 10
:: Slower: -TimeoutSec 30
```

### Add Custom Tests
Add after Test 5 in run.bat:
```batch
:: Test 6: Your custom test
echo [TEST 6/6] Testing custom feature...
powershell -Command "your-test-command"
if !errorlevel! equ 0 (
    echo [SUCCESS] ✅ Test 6 PASSED
    set /a test_passed+=1
) else (
    echo [ERROR] ❌ Test 6 FAILED
    set /a test_failed+=1
)
```

---

## Version History

### v3.0 (October 24, 2025)
- ✅ Added comprehensive 5-test health check suite
- ✅ Integrated test results into startup log
- ✅ Added user prompt on test failures
- ✅ Improved error messages and diagnostics
- ✅ Process cleanup before startup
- ✅ Port liberation for clean start

### v2.0 (Previous)
- Basic Ollama service detection
- Simple model pull if missing
- No health validation

---

## Related Files

- **Main Script**: `run.bat`
- **Test Suite**: `test_ollama_communication.ps1` (standalone version)
- **Test Results**: `OLLAMA_TEST_RESULTS.md`
- **Startup Log**: `ultron_master_startup.log`
- **Configuration**: `ultron_config.json`

---

## Quick Reference

### Commands
```bash
# Normal startup (with tests)
.\run.bat

# View test results in log
Get-Content ultron_master_startup.log -Tail 50

# Run standalone tests
.\test_ollama_communication.ps1

# Check active services
Get-NetTCPConnection -LocalPort 8080,5175,11434
```

### Expected Output (Success)
```
[TEST 1/5] Checking Ollama service availability...
[SUCCESS] ✅ Test 1 PASSED - Ollama service responding

[TEST 2/5] Checking llava:7b model availability...
[SUCCESS] ✅ Test 2 PASSED - Model llava:7b available

[TEST 3/5] Testing text generation...
[SUCCESS] ✅ Test 3 PASSED - Text generation working

[TEST 4/5] Testing chat API...
[SUCCESS] ✅ Test 4 PASSED - Chat API working

[TEST 5/5] Testing context retention...
[SUCCESS] ✅ Test 5 PASSED - Context retention working

[TEST SUMMARY] Tests Passed: 5/5 | Tests Failed: 0/5
[SUCCESS] ✅ All Ollama tests passed! System ready.
```

---

**Document Updated**: October 24, 2025
**Author**: ULTRON Agent Development Team
**Status**: Production Ready ✅
