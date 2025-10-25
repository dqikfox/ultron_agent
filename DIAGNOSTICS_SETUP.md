# ULTRON Diagnostics System - Complete Setup

## Overview

ULTRON now has Unity Cloud-style diagnostics with:
- **Real-time crash reporting** (like Unity's crash analytics)
- **Performance telemetry** (CPU, memory, service health)
- **Web dashboard** (live monitoring at http://localhost:5001)
- **AWS CloudWatch integration** (sync to oasis_app)
- **Automatic error tracking** (decorator-based)

## Quick Start

### 1. Update Configuration

Your `ultron_config.json` has been updated with:
```json
{
  "diagnostics_enabled": true,
  "diagnostics_dashboard_port": 5001,
  "diagnostics_auto_export": true,
  "diagnostics_export_interval_hours": 24,
  "aws": {
    "region": "us-west-2",
    "account_id": "941284019015",
    "oasis_app": {
      "name": "oasis_app",
      "region": "us-west-2",
      "resource_group_arn": "arn:aws:resource-groups:us-west-2:941284019015:group/oasis_app/06685rwrf3sclyi4jebduohwkd"
    }
  }
}
```

### 2. Start Diagnostics Dashboard

```powershell
# Run diagnostics dashboard
python -m diagnostics.diagnostics_dashboard

# Or integrate into run.bat
```

Access dashboard at: **http://localhost:5001**

### 3. View Live Diagnostics

Dashboard shows:
- ✅ Session uptime
- 🔥 Crash reports (last hour & total)
- 📊 System health (CPU, memory, disk)
- 🖥️ Service status (Ollama, API, GUI)
- ⚡ Auto-refresh every 5 seconds

## Features

### 1. Automatic Crash Reporting

Wrap any function to auto-report crashes:

```python
from diagnostics import diagnostic_wrapper

@diagnostic_wrapper("brain", track_performance=True)
async def process_command(cmd: str):
    # Any exception here is automatically:
    # - Captured with full stack trace
    # - Logged to diagnostics/data/
    # - Shown in dashboard
    # - Sent to CloudWatch (if enabled)
    result = await complex_operation(cmd)
    return result
```

### 2. Manual Crash Reporting

```python
from diagnostics import report_crash

try:
    risky_operation()
except Exception as e:
    crash_id = report_crash("tool_executor", e, severity="critical")
    # Continue or re-raise
```

### 3. Performance Metrics

```python
from diagnostics import track_metric

# Track tokens processed
track_metric("brain", "tokens_processed", 1024, "tokens")

# Track API response time
track_metric("api_server", "response_time", 0.45, "seconds")

# Track tool executions
track_metric("tool_executor", "executions", 1, "count")
```

### 4. System Health Monitoring

Diagnostics automatically tracks:
- CPU usage
- Memory usage
- Disk usage
- Service availability (ports 5000, 8080, 11434, etc.)
- Thread counts

### 5. AWS CloudWatch Integration

Sync diagnostics to AWS for centralized monitoring:

```python
from diagnostics.cloudwatch_integration import run_cloudwatch_sync, setup_default_alarms
import asyncio

# In your main startup:
config = load_config()

# Setup alarms (once)
await setup_default_alarms(config)

# Start background sync (every 5 minutes)
asyncio.create_task(run_cloudwatch_sync(config, interval_minutes=5))
```

**CloudWatch Metrics Sent**:
- `ULTRON/Diagnostics/TotalCrashes`
- `ULTRON/Diagnostics/CrashesLastHour`
- `ULTRON/Diagnostics/UnresolvedIssues`
- `ULTRON/Diagnostics/CPUUtilization`
- `ULTRON/Diagnostics/MemoryUtilization`
- `ULTRON/Diagnostics/DiskUtilization`

**CloudWatch Logs**:
- Log Group: `/ultron/oasis_app/diagnostics`
- Log Stream: `diagnostics-YYYY-MM-DD`
- Contains: Full crash reports with stack traces

**Default Alarms**:
- HighCrashRate: Triggers if >10 crashes/hour
- HighCPU: Triggers if CPU >90%
- HighMemory: Triggers if memory >85%

## API Endpoints

### GET /
Dashboard UI

### GET /api/diagnostics/summary
```json
{
  "session": {
    "start_time": "2025-10-25T20:00:00",
    "uptime_seconds": 3600,
    "uptime_formatted": "1:00:00"
  },
  "crashes": {
    "total": 5,
    "last_hour": 2,
    "by_component": {"brain": 3, "tool_executor": 2},
    "unresolved": 1
  },
  "performance": {
    "total_metrics": 1000,
    "latest_health": {...}
  },
  "services": {...}
}
```

### GET /api/diagnostics/crashes
List all crash reports

### GET /api/diagnostics/crash/<crash_id>
Detailed crash report with stack trace

### GET /api/diagnostics/health
Current system health snapshot

### GET /api/diagnostics/export
Export all diagnostics to JSON file

## Integration with ULTRON

### Update agent_core.py

```python
from diagnostics import diagnostic_wrapper, get_diagnostics
from diagnostics.cloudwatch_integration import run_cloudwatch_sync, setup_default_alarms

class UltronAgent:
    def __init__(self, config):
        # Existing init...

        # Initialize diagnostics
        self.diagnostics = get_diagnostics(config)

    @diagnostic_wrapper("agent_core", track_performance=True)
    async def process_command(self, command: str):
        # Existing logic - now with auto crash reporting
        return await self.brain.process(command)

    async def startup(self):
        # Existing startup...

        # Setup AWS diagnostics
        if self.config.get("diagnostics_enabled"):
            await setup_default_alarms(self.config)
            asyncio.create_task(run_cloudwatch_sync(self.config))
```

### Update brain.py

```python
from diagnostics import diagnostic_wrapper, track_metric

class Brain:
    @diagnostic_wrapper("brain", track_performance=True)
    async def generate_response(self, prompt: str):
        response = await self.llm.generate(prompt)

        # Track tokens
        track_metric("brain", "tokens_generated", len(response.split()), "tokens")

        return response
```

### Update tools

```python
from diagnostics import diagnostic_wrapper

class WebScrapingTool(ToolInterface):
    @diagnostic_wrapper("web_scraping_tool", track_performance=True)
    def execute(self, command: str, **kwargs) -> str:
        # Automatic crash reporting and performance tracking
        return self.scrape(url)
```

## Oasis App Integration

Since you have `oasis_app` in AWS (us-west-2), diagnostics automatically:

1. **Sends metrics to CloudWatch** in us-west-2
2. **Creates log group**: `/ultron/oasis_app/diagnostics`
3. **Sets up alarms** for crash/health monitoring
4. **Tags resources** with `awsApplication` tag

### View in AWS Console

```powershell
# View metrics
aws cloudwatch list-metrics --namespace "ULTRON/Diagnostics" --region us-west-2

# View logs
aws logs tail "/ultron/oasis_app/diagnostics" --follow --region us-west-2

# View alarms
aws cloudwatch describe-alarms --alarm-name-prefix "ULTRON-oasis_app" --region us-west-2
```

## File Structure

```
diagnostics/
├── __init__.py              # Decorators and helpers
├── diagnostics_core.py      # Core crash/metric tracking
├── diagnostics_dashboard.py # Web dashboard (port 5001)
├── cloudwatch_integration.py # AWS sync
└── data/                    # Crash reports and exports
    ├── crash_*.json
    └── ultron_diagnostics_*.json
```

## Next Steps

1. **Start Dashboard**:
   ```powershell
   python -m diagnostics.diagnostics_dashboard
   ```

2. **Add to run.bat**:
   ```batch
   start "ULTRON Diagnostics" cmd /k python -m diagnostics.diagnostics_dashboard
   ```

3. **Test Crash Reporting**:
   ```python
   from diagnostics import report_crash

   try:
       raise ValueError("Test crash")
   except Exception as e:
       crash_id = report_crash("test", e)
       print(f"Crash ID: {crash_id}")
   ```

4. **View Dashboard**: http://localhost:5001

5. **Check AWS CloudWatch** (if configured)

## Benefits

✅ **Proactive Monitoring**: Catch crashes before users report them
✅ **Performance Insights**: Track which components are slowest
✅ **System Health**: Know when resources are constrained
✅ **AWS Integration**: Centralized monitoring with oasis_app
✅ **Historical Data**: Export and analyze crash patterns
✅ **Auto-Resolution**: Track which issues are resolved

## Troubleshooting

### Dashboard won't start
```powershell
# Check if port 5001 is available
netstat -ano | findstr :5001

# Try different port
python -m diagnostics.diagnostics_dashboard --port 5002
```

### CloudWatch not syncing
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Check region
echo $env:AWS_REGION  # Should be us-west-2

# Test manually
python -c "from diagnostics.cloudwatch_integration import CloudWatchIntegration; import json; config = json.load(open('ultron_config.json')); cw = CloudWatchIntegration(config); print('Enabled:', cw.enabled)"
```

### No crashes showing
- Crashes only captured with `@diagnostic_wrapper` decorator or manual `report_crash()`
- Check `diagnostics/data/` for JSON files
- Verify `diagnostics_enabled: true` in config

---

**Unity-style diagnostics for ULTRON Agent** ✅
**AWS oasis_app integration ready** ✅
**Real-time monitoring dashboard** ✅
