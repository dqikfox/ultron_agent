# 🔧 ULTRON Debug System

This comprehensive debug system provides advanced monitoring, testing, and diagnostic capabilities for the ULTRON Agent 3.0 system.

## 🚀 Quick Start

### Option 1: Use the Debug Menu (Easiest)
```cmd
debug_menu.bat
```

### Option 2: Direct Commands
```cmd
# Launch in debug mode
run_debug.bat

# Run diagnostics
python debug_test.py

# Monitor system
python debug_monitor.py
```

## 📋 Available Tools

### 1. 🚀 Debug Launcher (`run_debug.bat`)
- **Purpose**: Launch ULTRON with enhanced debugging features
- **Features**:
  - Real-time port monitoring
  - Enhanced error logging
  - Debug environment variables
  - Service status verification
  - Comprehensive startup diagnostics

**Usage:**
```cmd
run_debug.bat
```

**Key Features:**
- ✅ Real-time service status checking
- ✅ Enhanced logging with debug_logs/ directory
- ✅ Python unbuffered output for immediate feedback
- ✅ Port availability pre-checking
- ✅ Detailed startup sequence monitoring

---

### 2. 📊 Debug Monitor (`debug_monitor.py`)
- **Purpose**: Real-time system monitoring and health checking
- **Features**:
  - Continuous service monitoring
  - HTTP health checks
  - Port status monitoring
  - Automatic report generation

**Usage:**
```cmd
# Interactive menu
python debug_monitor.py

# Single check
python debug_monitor.py single

# Continuous monitoring (10s intervals)
python debug_monitor.py continuous 10

# Check log files
python debug_monitor.py logs
```

**Monitoring Includes:**
- ✅ Port 5000: Main Pokédx GUI Server
- ✅ Port 5173: NVIDIA Chat Engine
- ✅ Port 3000: GUI API Server
- ✅ Port 8000: Agent Core
- ✅ HTTP response time monitoring
- ✅ Error detection and reporting

---

### 3. 🧪 Debug Test Suite (`debug_test.py`)
- **Purpose**: Comprehensive system testing and validation
- **Features**:
  - Python environment validation
  - File structure verification
  - Individual service testing
  - GUI content validation

**Usage:**
```cmd
# Full diagnostic suite (interactive)
python debug_test.py

# Quick check only
python debug_test.py quick

# Test specific service
python debug_test.py main_gui
python debug_test.py chat_engine
python debug_test.py gui_api
python debug_test.py agent_core
```

**Tests Include:**
- ✅ Python version and package availability
- ✅ Required file existence and integrity
- ✅ Port availability checking
- ✅ GUI content validation
- ✅ Individual service startup testing

---

### 4. 🌐 Debug Dashboard (`debug_dashboard.html`)
- **Purpose**: Web-based real-time monitoring interface
- **Features**:
  - Real-time service status visualization
  - Port monitoring dashboard
  - System metrics and uptime
  - Log viewing and export

**Usage:**
```cmd
# Open in browser
start debug_dashboard.html
```

**Dashboard Features:**
- ✅ Real-time service status grid
- ✅ Port monitoring with visual indicators
- ✅ System uptime and error counting
- ✅ Quick action buttons for each service
- ✅ Auto-refreshing every 5 seconds
- ✅ Log export functionality

---

## 📂 Debug Output Structure

```
debug_logs/
├── main_gui_debug.log          # Main GUI Server debug output
├── frontend_debug.log          # Chat Engine debug output
├── gui_api_debug.log          # GUI API Server debug output
├── agent_core_debug.log       # Agent Core debug output
├── web_bridge_debug.log       # Web Bridge debug output
├── diagnostic_report_*.json   # Automated diagnostic reports
└── debug_report_*.json        # Monitor status reports
```

## 🔍 Service Architecture (Debug Mode)

```
🏠 Port 5000: Main Pokédx GUI Server
   ├── Script: main_gui_server.py
   ├── Purpose: Serves sophisticated Pokédx interface
   ├── Debug Log: debug_logs/main_gui_debug.log
   └── Health: http://localhost:5000

💬 Port 5173: NVIDIA Chat Engine
   ├── Script: frontend_server.py
   ├── Purpose: AI-powered chat interface
   ├── Debug Log: debug_logs/frontend_debug.log
   └── Health: http://localhost:5173

🔌 Port 3000: GUI API Server
   ├── Script: gui_api_server.py
   ├── Purpose: API endpoints for GUI interactions
   ├── Debug Log: debug_logs/gui_api_debug.log
   └── Health: http://localhost:3000/api/status

🤖 Port 8000: Agent Core
   ├── Script: agent_core.py
   ├── Purpose: NVIDIA AI processing backend
   ├── Debug Log: debug_logs/agent_core_debug.log
   └── Health: http://localhost:8000/health

🌉 Web Bridge (Background)
   ├── Script: web_bridge.py
   ├── Purpose: Connection manager between components
   └── Debug Log: debug_logs/web_bridge_debug.log
```

## 🛠️ Debug Environment Variables

When running in debug mode, these environment variables are automatically set:

```cmd
ULTRON_DEBUG=1              # Enables debug logging
PYTHONUNBUFFERED=1         # Immediate output (no buffering)
FLASK_ENV=development      # Flask development mode
FLASK_DEBUG=1              # Flask debug mode
```

## 🚨 Troubleshooting Guide

### Service Won't Start
1. Check debug logs in `debug_logs/` directory
2. Verify port availability: `netstat -an | findstr ":PORT"`
3. Run diagnostic: `python debug_test.py quick`
4. Check Python environment and dependencies

### Port Already in Use
```cmd
# Find process using port
netstat -ano | findstr ":5000"

# Kill process by PID
taskkill /F /PID [PID_NUMBER]
```

### GUI Not Loading
1. Verify `gui/ultron_enhanced/web/index.html` exists
2. Check main_gui_debug.log for errors
3. Test direct access: `http://localhost:5000`
4. Run GUI content test: `python debug_test.py`

### Chat Engine Issues
1. Check frontend_debug.log for NVIDIA connection errors
2. Verify NVIDIA dependencies are installed
3. Test endpoint: `http://localhost:5173`
4. Check for Unicode encoding issues in logs

## 📈 Performance Monitoring

The debug system tracks these key metrics:

- **Service Response Time**: HTTP request latency for each service
- **Port Status**: Real-time port availability monitoring
- **Error Count**: Automatic error detection and counting
- **System Uptime**: Time since debug system started
- **Log Activity**: Real-time log file monitoring

## 🔧 Advanced Usage

### Custom Monitoring Intervals
```cmd
# Monitor every 5 seconds
python debug_monitor.py continuous 5

# Monitor every 30 seconds
python debug_monitor.py continuous 30
```

### Automated Testing
```cmd
# Test all services automatically
python debug_test.py full
```

### Debug Dashboard Customization
Edit `debug_dashboard.html` to modify:
- Refresh intervals (default: 5 seconds)
- Service endpoints
- Visual styling
- Monitoring metrics

## 📝 Log Analysis

Debug logs include detailed information:
- **Timestamps**: Precise timing for all events
- **Service Status**: Startup/shutdown events
- **Error Details**: Full stack traces and error context
- **Performance Data**: Response times and resource usage
- **Configuration Info**: Environment and setup details

## 🎯 Best Practices

1. **Always run diagnostics first**: `python debug_test.py quick`
2. **Monitor continuously during development**: Use debug dashboard
3. **Check logs for errors**: Regular log file inspection
4. **Use single checks for quick status**: `python debug_monitor.py single`
5. **Export logs before major changes**: Use dashboard export feature

---

## 📞 Support

If you encounter issues:

1. Run full diagnostic: `python debug_test.py`
2. Check debug logs in `debug_logs/` directory
3. Use continuous monitoring to identify patterns
4. Export debug dashboard logs for analysis
5. Review this README for troubleshooting steps

The debug system provides comprehensive visibility into ULTRON's operation, making it easy to identify and resolve issues quickly! 🚀
