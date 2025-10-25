# ULTRON Diagnostics - Quick Reference

## 🚀 Start Dashboard
```powershell
.\scripts\start_diagnostics.ps1
```
**URL**: http://localhost:5001

## 💻 Code Integration

### Automatic Crash Tracking
```python
from diagnostics import diagnostic_wrapper

@diagnostic_wrapper("component_name", track_performance=True)
async def my_function():
    # All exceptions auto-reported
    pass
```

### Manual Crash Report
```python
from diagnostics import report_crash

try:
    risky_operation()
except Exception as e:
    crash_id = report_crash("tool", e, severity="critical")
```

### Track Metrics
```python
from diagnostics import track_metric

track_metric("brain", "tokens", 1024, "tokens")
track_metric("api", "duration", 0.25, "seconds")
```

## 📊 Dashboard Features
- Session uptime
- Total crashes / Last hour / Unresolved
- CPU / Memory / Disk usage
- Service status (5 ports)
- Auto-refresh (5s)

## ☁️ AWS CloudWatch (oasis_app)
**Region**: us-west-2
**Metrics**: `ULTRON/Diagnostics/*`
**Logs**: `/ultron/oasis_app/diagnostics`
**Alarms**: HighCrashRate, HighCPU, HighMemory

### Enable Sync
```python
from diagnostics.cloudwatch_integration import run_cloudwatch_sync
asyncio.create_task(run_cloudwatch_sync(config, interval_minutes=5))
```

## 📁 Files
- `diagnostics/diagnostics_core.py` - Core logic
- `diagnostics/diagnostics_dashboard.py` - Web UI
- `diagnostics/cloudwatch_integration.py` - AWS sync
- `diagnostics/__init__.py` - Decorators
- `diagnostics/data/` - Crash JSON files

## 🔌 API Endpoints
- `GET /` - Dashboard UI
- `GET /api/diagnostics/summary` - Stats
- `GET /api/diagnostics/crashes` - All crashes
- `GET /api/diagnostics/crash/<id>` - Details
- `GET /api/diagnostics/health` - System health
- `GET /api/diagnostics/export` - Export JSON

## 📚 Full Docs
- `DIAGNOSTICS_SETUP.md` - Complete guide
- `DIAGNOSTICS_IMPLEMENTATION_SUMMARY.md` - What was built
- `.aws/ultron_aws_config.md` - AWS setup
