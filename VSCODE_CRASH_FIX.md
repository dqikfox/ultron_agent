# VS Code Crash Prevention System

## Overview

This system prevents Visual Studio Code crashes when working with the ULTRON Agent project by:

1. **GUI Threading Fixes**: Eliminates thousands of "main thread is not in main loop" errors
2. **Resource Monitoring**: Prevents system overload that causes crashes
3. **Extension Optimization**: Reduces conflicts between AI extensions
4. **Memory Management**: Automatic cleanup and garbage collection
5. **Circuit Breaker Protection**: Pauses heavy operations when system is overloaded

## Quick Start

### Windows
```batch
# Launch VS Code safely with crash prevention
launch_vscode_safe.bat
```

### Linux/Mac
```bash
# Start crash prevention system
python3 vscode_crash_prevention.py --launch-vscode

# Or just run monitoring without launching VS Code
python3 vscode_crash_prevention.py
```

## What Was Fixed

### 1. GUI Threading Issues ✅
- **Problem**: Thousands of "GUI monitoring error: main thread is not in main loop" errors
- **Solution**: Fixed `gui_ultimate.py` to use proper thread-safe GUI updates with `root.after()`

### 2. AI Extension Conflicts ✅
- **Problem**: Multiple AI extensions (Sixth AI, Amazon Q, GitHub Copilot, AI Toolkit) running simultaneously
- **Solution**: Optimized `.vscode/settings.json` to use only GitHub Copilot, disabled conflicting extensions

### 3. Resource Exhaustion ✅
- **Problem**: Maverick engine causing continuous error loops, high CPU/memory usage
- **Solution**: Added circuit breaker pattern and resource limits to `maverick_engine.py`

### 4. File Watcher Overload ✅
- **Problem**: VS Code watching too many files (logs, cache, screenshots, large directories)
- **Solution**: Added extensive file exclusions in workspace settings

### 5. Memory Issues ✅
- **Problem**: High memory usage from multiple language servers and extensions
- **Solution**: Added memory limits and reduced analysis scope

## System Requirements

- **Minimum RAM**: 4GB (8GB recommended)
- **Available Disk Space**: 1GB+
- **Python**: 3.8+ with `psutil` module
- **VS Code**: Latest version

## Features

### Resource Monitor
- **CPU Monitoring**: Alerts at 80% usage, emergency measures at sustained high usage
- **Memory Monitoring**: Alerts at 85% usage, automatic garbage collection
- **Circuit Breaker**: Pauses heavy operations when system is overloaded

### Crash Prevention
- **Environment Optimization**: Sets optimal environment variables
- **Temporary File Cleanup**: Removes VS Code cache and Python bytecode files
- **Process Priority Management**: Reduces priority when resources are low

### VS Code Optimizations
- **Extension Management**: Only essential extensions enabled
- **File Watching**: Excludes resource-intensive directories
- **Language Servers**: Reduced memory usage and analysis scope
- **Autocomplete**: Optimized for performance over features

## Configuration

### Resource Limits (resource_monitor.py)
```python
ResourceMonitor(
    cpu_limit=80.0,      # CPU usage threshold (%)
    memory_limit=85.0,   # Memory usage threshold (%)
    check_interval=5.0   # Check frequency (seconds)
)
```

### VS Code Settings
Key optimizations in `.vscode/settings.json`:
- `"typescript.tsserver.maxTsServerMemory": 2048`
- `"python.analysis.diagnosticMode": "openFilesOnly"`
- `"editor.minimap.enabled": false`
- Extensive file exclusions

## Monitoring

### Log Files
- `logs/crash_prevention.log` - System monitoring and crash prevention
- `logs/ultron.jsonl` - ULTRON Agent logs (should show fewer errors)

### Real-time Status
```bash
# Check current resource usage
python3 -c "from resource_monitor import get_resource_monitor; print(get_resource_monitor().get_current_usage())"
```

## Troubleshooting

### VS Code Still Crashing?
1. **Check System Resources**: Ensure you have enough RAM and close other applications
2. **Update VS Code**: Make sure you're running the latest version
3. **Disable More Extensions**: Temporarily disable all non-essential extensions
4. **Restart System**: Sometimes a fresh start helps

### High Resource Usage?
1. **Check the logs**: Look at `logs/crash_prevention.log` for warnings
2. **Adjust limits**: Lower the CPU/memory thresholds in `resource_monitor.py`
3. **Close background apps**: Especially other IDEs, browsers with many tabs

### Python Errors?
1. **Install dependencies**: `pip install psutil`
2. **Check Python version**: Must be 3.8 or higher
3. **Run as administrator**: Some system monitoring requires elevated privileges

## Advanced Usage

### Custom Resource Callbacks
```python
from resource_monitor import get_resource_monitor

def my_cpu_callback(cpu_percent):
    print(f"CPU usage high: {cpu_percent}%")

monitor = get_resource_monitor()
monitor.set_cpu_callback(my_cpu_callback)
monitor.start_monitoring()
```

### Integration with ULTRON Agent
The resource monitor automatically integrates with ULTRON Agent's main loop and can pause heavy operations when needed.

## Files Modified

- `gui_ultimate.py` - Fixed GUI threading issues
- `.vscode/settings.json` - Optimized VS Code configuration
- `ultron-agent.code-workspace` - Workspace-level optimizations
- `maverick_engine.py` - Added circuit breaker and error handling

## Files Added

- `resource_monitor.py` - System resource monitoring
- `vscode_crash_prevention.py` - Crash prevention system
- `launch_vscode_safe.bat` - Safe launch script for Windows
- `VSCODE_CRASH_FIX.md` - This documentation

## Success Metrics

After implementing these fixes, you should see:
- ✅ No more "main thread is not in main loop" errors
- ✅ Stable VS Code operation without crashes
- ✅ Lower CPU and memory usage
- ✅ Faster VS Code startup and operation
- ✅ Reduced extension conflicts

## Support

If you continue to experience crashes after applying these fixes:
1. Check the logs for specific error patterns
2. Adjust resource limits based on your system
3. Consider upgrading hardware (more RAM helps significantly)
4. Report specific error messages for further troubleshooting