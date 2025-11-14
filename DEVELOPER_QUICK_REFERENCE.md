# ULTRON Agent - Developer Quick Reference

## 🚀 Startup

```batch
# Start entire ULTRON system (all 6 services)
.\run.bat
```

**Services Started**:
- Ollama LLM: http://localhost:11434
- Web GUI: http://localhost:8080
- Frontend UI: http://localhost:5175
- NVIDIA Chat: http://localhost:8002
- API Server: http://localhost:5000
- **Diagnostics Dashboard: http://localhost:5001** ← NEW

---

## 🔧 Adding Diagnostics to Your Code

### Automatic Crash Tracking (Recommended)

```python
from diagnostics import diagnostic_wrapper, track_metric

@diagnostic_wrapper("component_name", track_performance=True)
async def your_function(param):
    # All exceptions automatically captured
    # Performance metrics automatically tracked
    track_metric("component_name", "metric_name", value, "unit")
    return result
```

### Manual Crash Reporting

```python
from diagnostics import report_crash

try:
    risky_operation()
except Exception as e:
    crash_id = report_crash("component", e, severity="critical")
```

### Quick Metrics

```python
from diagnostics import track_metric

track_metric("brain", "tokens_generated", 1024, "tokens")
track_metric("api", "request_duration", 0.25, "seconds")
track_metric("tool", "executions", 1, "count")
```

---

## 📊 Viewing Diagnostics

### Dashboard URL
http://localhost:5001

### What You'll See
- Session uptime
- Total crashes / Last hour / Unresolved
- CPU / Memory / Disk usage
- Service status (6 services)
- Crash list with details
- Auto-refresh every 5 seconds

### API Endpoints
- `GET /api/diagnostics/summary` - Stats overview
- `GET /api/diagnostics/crashes` - All crashes
- `GET /api/diagnostics/crash/<id>` - Crash details
- `GET /api/diagnostics/health` - System health
- `GET /api/diagnostics/export` - Export JSON

---

## 🐛 GUI Fixed

**Issue**: Logs auto-downloading, dialogs auto-opening on GUI startup

**Status**: ✅ **FIXED**

**What Changed**: `userRequestedExport` flag now properly initialized

**Result**: Clean GUI startup, exports only when you click the button

---

## 📁 Key Files Modified

| File | Change | Impact |
|------|--------|--------|
| `brain.py` | Added diagnostics | AI crashes tracked |
| `agent_core.py` | Added diagnostics | Core agent monitored |
| `tools/web_scraping_tool.py` | Added diagnostics | Example for other tools |
| `tools/tool_interface.py` | Added instructions | Easy decorator usage |
| `gui/ultron_enhanced/web/app.js` | Fixed auto-download | No more annoying exports |
| `run.bat` | Added 2 services | API + Diagnostics auto-start |

---

## 🎯 Best Practices

### When to Use Diagnostics

✅ **DO** decorate:
- Core component methods (brain, agent_core, tools)
- Long-running operations
- Network calls
- File operations
- User-facing features

❌ **DON'T** decorate:
- Simple getters/setters
- Property accessors
- Internal helpers
- High-frequency loops (unless needed)

### Performance Tracking

```python
# Track execution time automatically
@diagnostic_wrapper("component", track_performance=True)
def slow_operation():
    # Performance metric auto-captured
    pass

# Track custom metrics
track_metric("api", "response_time", duration_ms, "milliseconds")
```

### Error Severity Levels

```python
report_crash("component", exception, severity="critical")  # Production down
report_crash("component", exception, severity="error")     # Feature broken
report_crash("component", exception, severity="warning")   # Degraded performance
```

---

## 🔍 Troubleshooting

### Diagnostics Not Starting

```powershell
# Check if port 5001 is in use
netstat -ano | findstr :5001

# Start manually
python -m diagnostics.diagnostics_dashboard
```

### Import Errors

```powershell
# Test diagnostics module
python -c "from diagnostics import diagnostic_wrapper; print('OK')"

# Test core modules
python -c "from brain import UltronBrain; print('OK')"
python -c "from agent_core import UltronAgent; print('OK')"
```

### Dashboard Not Loading

1. Check service status: http://localhost:5001/api/diagnostics/health
2. Check logs: `logs/diagnostics_dashboard.log`
3. Verify config: `diagnostics_enabled: true` in `ultron_config.json`

---

## 📖 Full Documentation

- **Complete Guide**: `DIAGNOSTICS_SETUP.md`
- **Implementation Summary**: `DIAGNOSTICS_IMPLEMENTATION_SUMMARY.md`
- **Recent Changes**: `ENHANCEMENTS_2025-10-25.md`
- **Quick Reference**: `DIAGNOSTICS_QUICK_REF.md`

---

## 🎉 What's New (Oct 25, 2025)

✅ GUI auto-download bug **FIXED**
✅ Diagnostics integrated in **brain.py**
✅ Diagnostics integrated in **agent_core.py**
✅ Diagnostics integrated in **web_scraping_tool** (example)
✅ Dashboard now **auto-starts** with run.bat
✅ API server now **auto-starts** with run.bat
✅ All services verified working

---

**Status**: ✅ **PRODUCTION READY**
**Date**: October 25, 2025
