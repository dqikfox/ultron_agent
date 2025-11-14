# Phase 2 Integration Checklist
## Quick Reference for web_gui_server.py Integration

**Estimated Time**: 30-45 minutes
**Difficulty**: Easy (copy/paste, follow template)
**Files to Modify**: 1 (web_gui_server.py)
**New Dependencies**: None (already have phase2_realtime_profiling.py)

---

## 📋 Pre-Integration Checklist

- [ ] Read PHASE2_DOCUMENTATION.md (Section: Integration Guide)
- [ ] Read PHASE2_INTEGRATION_GUIDE.md
- [ ] Verify phase2_realtime_profiling.py exists in project root
- [ ] Run test_phase2.py to verify all tests pass (5/5)
- [ ] Create backup of web_gui_server.py (git or manual copy)

---

## 🔧 Integration Steps

### Step 1: Add Imports (2-3 lines)
**Location**: web_gui_server.py, near top after existing imports

```python
from phase2_realtime_profiling import (
    profiler,
    metrics_buffer,
    metrics_collector,
    ws_handler,
    start_phase2_services,
    stop_phase2_services
)
```

**Checklist**:
- [ ] Imports added to web_gui_server.py
- [ ] Placed after existing imports
- [ ] No syntax errors

---

### Step 2: Add 5 Handler Methods (30-40 lines)
**Location**: Inside `UltronWebHandler` class

```python
def _get_performance_stats(self):
    """GET /api/performance/stats handler"""
    return {"status": "success", "stats": profiler.get_stats()}

def _get_performance_bottlenecks(self):
    """GET /api/performance/bottlenecks handler"""
    top_n = int(self.get_query_param("top_n", 5))
    return {"status": "success", "bottlenecks": profiler.get_bottlenecks(top_n)}

def _get_metrics_stream(self):
    """GET /api/metrics/stream handler"""
    latest = metrics_buffer.get_latest(20)
    return {"status": "success", "metrics": latest, "count": len(latest)}

def _get_function_history(self, func_name):
    """GET /api/performance/function-history/{func_name} handler"""
    limit = int(self.get_query_param("limit", 100))
    history = profiler.get_history(func_name, limit)
    return {"status": "success", "function": func_name, "history": history, "count": len(history)}

def _get_phase2_status(self):
    """GET /api/phase2/status handler"""
    return {
        "status": "success",
        "phase2_status": {
            "profiler_active": True,
            "metrics_collection_active": metrics_collector.is_running(),
            "metrics_buffer_size": len(metrics_buffer.buffer),
            "websocket_clients": len(ws_handler.connections),
            "functions_tracked": len(profiler.metrics),
            "timestamp": time.time()
        }
    }
```

**Checklist**:
- [ ] 5 handler methods added to UltronWebHandler class
- [ ] Methods placed together (e.g., after existing handlers)
- [ ] All methods return JSON-compatible dicts
- [ ] No syntax errors
- [ ] Indentation correct (class method level)

---

### Step 3: Register GET Routes (5 lines)
**Location**: Inside `_handle_api_get()` method, add before final else

```python
# In _handle_api_get method, add these conditions:
elif path == "/api/performance/stats":
    return self._get_performance_stats()
elif path == "/api/performance/bottlenecks":
    return self._get_performance_bottlenecks()
elif path == "/api/metrics/stream":
    return self._get_metrics_stream()
elif path == "/api/phase2/status":
    return self._get_phase2_status()
elif path.startswith("/api/performance/function-history/"):
    func_name = path.split("/")[-1]
    return self._get_function_history(func_name)
```

**Checklist**:
- [ ] 5 new elif conditions added to _handle_api_get()
- [ ] Routes added before final else clause
- [ ] Path strings match exactly
- [ ] Method names match handlers created in Step 2
- [ ] No syntax errors

---

### Step 4: Register POST Routes (3 lines)
**Location**: Inside `_handle_api_post()` method, add before final else

```python
# In _handle_api_post method, add these conditions:
elif path == "/api/profiler/reset":
    profiler.reset()
    return {"status": "success", "message": "Profiler reset - all data cleared"}
elif path == "/api/metrics/collection/start":
    metrics_collector.start()
    return {"status": "success", "message": "Metrics collection started"}
elif path == "/api/metrics/collection/stop":
    metrics_collector.stop()
    return {"status": "success", "message": "Metrics collection stopped"}
```

**Checklist**:
- [ ] 3 new elif conditions added to _handle_api_post()
- [ ] Routes added before final else clause
- [ ] Path strings match exactly
- [ ] Correct methods called (reset, start, stop)
- [ ] No syntax errors

---

### Step 5: Initialize Services in main() (3-4 lines)
**Location**: In `main()` function, after agent initialization

```python
# In main() function, add after other initializations:
if AGENT_AVAILABLE:
    try:
        start_phase2_services()
        print("✅ Phase 2 Real-time & Profiling Services Initialized")
    except Exception as e:
        print(f"⚠️  Phase 2 initialization warning: {e}")
```

**Checklist**:
- [ ] Initialization code added to main()
- [ ] Inside the "if AGENT_AVAILABLE:" block
- [ ] Added after agent initialization
- [ ] Exception handling included
- [ ] No syntax errors

---

## ✅ Verification Steps (After Integration)

### Step 1: Syntax Verification
```powershell
# Check for Python syntax errors
python -m py_compile web_gui_server.py
```
- [ ] No syntax errors reported

### Step 2: Import Verification
```powershell
# Verify imports work
python -c "from web_gui_server import UltronWebHandler; print('✓ Imports OK')"
```
- [ ] No import errors

### Step 3: Service Startup
```powershell
# Start the server (should include Phase 2 initialization)
python web_gui_server.py
```
- [ ] Server starts without errors
- [ ] "Phase 2 Real-time & Profiling Services Initialized" message appears
- [ ] No exceptions in console

### Step 4: API Endpoint Testing

**Test GET endpoints**:
```powershell
# Metrics stream
curl http://localhost:8080/api/metrics/stream

# Performance stats
curl http://localhost:8080/api/performance/stats

# Bottlenecks
curl http://localhost:8080/api/performance/bottlenecks

# Phase 2 status
curl http://localhost:8080/api/phase2/status

# Function history
curl http://localhost:8080/api/performance/function-history/generate_response
```

**Test POST endpoints**:
```powershell
# Start collection
curl -X POST http://localhost:8080/api/metrics/collection/start

# Stop collection
curl -X POST http://localhost:8080/api/metrics/collection/stop

# Reset profiler
curl -X POST http://localhost:8080/api/profiler/reset
```

**Checklist**:
- [ ] All GET endpoints respond with status: "success"
- [ ] All POST endpoints respond with status: "success"
- [ ] No 404 errors
- [ ] JSON responses are valid
- [ ] Metrics appear in stream endpoint

### Step 5: Run Test Suite
```powershell
# Verify Phase 2 tests still pass after integration
python test_phase2.py
```
- [ ] 5/5 tests still passing
- [ ] 100% success rate
- [ ] No errors in output

---

## 📝 Testing Commands Reference

```bash
# Test metrics streaming
curl http://localhost:8080/api/metrics/stream | jq '.'

# Test performance stats (should be empty initially)
curl http://localhost:8080/api/performance/stats | jq '.'

# Test bottleneck detection
curl http://localhost:8080/api/performance/bottlenecks | jq '.'

# Get Phase 2 status
curl http://localhost:8080/api/phase2/status | jq '.'

# Start metrics collection
curl -X POST http://localhost:8080/api/metrics/collection/start

# Wait 2-3 seconds, then check metrics again
# (Should have new data points)

# Stop collection
curl -X POST http://localhost:8080/api/metrics/collection/stop

# Reset profiler
curl -X POST http://localhost:8080/api/profiler/reset
```

---

## 🐛 Troubleshooting Integration Issues

### Issue: ImportError - phase2_realtime_profiling not found
**Solution**: Verify phase2_realtime_profiling.py exists in project root
```powershell
ls phase2_realtime_profiling.py
```

### Issue: AttributeError - profiler not defined
**Solution**: Check imports are placed correctly and BEFORE class definition
- Imports must be at module level (top of file)
- Must be OUTSIDE the class definition

### Issue: Routes not responding
**Solution**: Verify routes are in correct _handle_api_get() or _handle_api_post()
- Check method exists
- Check path string matches exactly
- Verify elif is inside the correct method

### Issue: Services not initializing
**Solution**: Check main() initialization code
- Must be in main() function
- Must be inside "if AGENT_AVAILABLE:" block
- Must be after agent initialization

### Issue: Tests failing after integration
**Solution**: Run diagnostics
```powershell
# Check if Phase 2 module still works
python -c "from phase2_realtime_profiling import profiler; print('OK')"

# Run test suite
python test_phase2.py
```

---

## 📋 Integration Checklist Summary

**Pre-Integration**:
- [ ] Read documentation
- [ ] Verify Phase 2 module exists
- [ ] Run tests (5/5 passing)
- [ ] Backup web_gui_server.py

**Integration**:
- [ ] Add imports (2-3 lines)
- [ ] Add 5 handler methods (30-40 lines)
- [ ] Register 5 GET routes (5 elif clauses)
- [ ] Register 3 POST routes (3 elif clauses)
- [ ] Initialize in main() (3-4 lines)

**Verification**:
- [ ] Syntax check passes
- [ ] Imports verify OK
- [ ] Server starts successfully
- [ ] All endpoints respond
- [ ] Tests still pass
- [ ] No errors in logs

**Post-Integration**:
- [ ] Server runs stably
- [ ] Metrics are collected
- [ ] Endpoints are accessible
- [ ] Performance impact negligible
- [ ] Ready for Phase 3

---

## 📈 Integration Success Criteria

✅ **All Endpoints Functional**
- GET /api/metrics/stream returns 200 with metrics
- GET /api/performance/stats returns 200 with stats
- GET /api/performance/bottlenecks returns 200 with bottlenecks
- GET /api/phase2/status returns 200 with status
- POST /api/profiler/reset returns 200
- POST /api/metrics/collection/start returns 200
- POST /api/metrics/collection/stop returns 200

✅ **Services Running**
- Metrics collection active
- Profiler tracking functions
- WebSocket handler ready
- No exceptions in logs

✅ **Tests Passing**
- test_phase2.py: 5/5 passing
- No new errors introduced
- Performance impact <1%

---

## ⏱️ Time Estimation

| Step | Time | Status |
|------|------|--------|
| Review docs | 10 min | Quick read |
| Add imports | 1 min | Copy/paste |
| Add methods | 5 min | Copy/paste |
| Register routes | 5 min | Copy/paste |
| Initialize | 2 min | Copy/paste |
| Verify syntax | 3 min | Run check |
| Test endpoints | 5 min | curl commands |
| Run test suite | 5 min | Run tests |
| **Total** | **~40 min** | **Easy** |

---

## 🎯 After Integration

**Immediate Next**: Add profiling decorators to critical functions
- brain.py: generate_response, plan
- agent_core.py: initialize_subsystems
- tools: execute methods
- Expected time: 1 hour

**Then**: Create web GUI dashboard for metrics
- Display real-time metrics
- Show performance history
- List bottlenecks
- Expected time: 2-3 hours

**Finally**: Phase 3 - AI optimization
- Analyze bottleneck patterns
- Suggest code improvements
- Predict performance issues
- Expected time: 4-6 hours

---

**Integration Ready**: ✅ YES
**Documentation Complete**: ✅ YES
**Tests Passing**: ✅ 5/5
**Estimated Completion**: ✅ 30-45 minutes

**Start Integration**: NOW ✅

---

*For detailed reference, see PHASE2_INTEGRATION_GUIDE.md*
*For complete documentation, see PHASE2_DOCUMENTATION.md*
