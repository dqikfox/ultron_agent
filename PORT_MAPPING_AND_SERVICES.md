# 🔌 ULTRON AGENT 3.0 - PORT MAPPING & CRITICAL SAFEGUARDS

**CRITICAL**: This document defines all ports, services, and safeguards. **DO NOT MODIFY WITHOUT DOCUMENTATION**.

---

## ⚠️ CRITICAL RULES

```
RULE 1: All ports defined here are LOCKED and MANDATORY
  └─ Changing a port requires updating ALL these files:
     • ultron_config.json
     • run.bat
     • web_gui_server.py
     • api_server.py
     • ALL affected documentation

RULE 2: Port conflicts will cause complete system failure
  └─ Symptoms: "ERR_CONNECTION_REFUSED", services not starting
  └─ Solution: Check Port Conflict Resolution section below

RULE 3: Before making ANY change:
  1. Check this document
  2. Search for port number in ALL .py files
  3. Update run.bat
  4. Update ultron_config.json
  5. Update this documentation
  6. Create CHANGELOG entry

RULE 4: NO HARDCODED PORTS in Python files
  └─ All ports MUST read from ultron_config.json or environment variables
```

---

## 📊 OFFICIAL PORT ALLOCATION

| Port | Service | Status | Config File | Purpose | Dependencies |
|------|---------|--------|-------------|---------|--------------|
| **11434** | Ollama LLM Backend | ✅ PRIMARY | ultron_config.json | Local AI inference (llava:7b) | Core AI reasoning |
| **8080** | Web GUI Server | ✅ PRIMARY | run.bat | Pokédex UI interface | Frontend |
| **5000** | REST API Server | ✅ CRITICAL | ultron_config.json | Command/tool execution | API routes |
| **7861** | LangFlow Backend | ⚠️ OPTIONAL | ultron_config.json | Workflow automation | Disabled by default |
| **8081** | AutoGen Studio | ⚠️ OPTIONAL | ultron_config.json | Multi-agent orchestration | Disabled by default |
| **5001** | Diagnostics API | ⚠️ OPTIONAL | ultron_config.json | Performance monitoring | Disabled by default |
| **5003** | ADB Backend | ⚠️ OPTIONAL | run.bat | Android device control | Disabled by default |
| **5175** | Frontend Server | ⚠️ OPTIONAL | N/A | Development frontend | Disabled by default |

### 🟢 ACTIVE SERVICES (Currently Running)
- ✅ **Ollama (11434)** - Always starts with run.bat
- ✅ **Web GUI (8080)** - Always starts with run.bat
- ✅ **API Server (5000)** - Must start manually: `python api_server.py`

### 🟡 OPTIONAL SERVICES (May Be Enabled)
- ⚠️ LangFlow (7861) - Set `"langflow_enabled": true` in config
- ⚠️ AutoGen (8081) - Set `"autogen_studio_enabled": true` in config
- ⚠️ Diagnostics (5001) - Starts if diagnostics enabled
- ⚠️ ADB Backend (5003) - Disabled by default

### 🔴 DO NOT USE THESE PORTS
```
3306 - MySQL (if ever needed)
5432 - PostgreSQL (if ever needed)
6379 - Redis (if ever needed)
27017 - MongoDB (if ever needed)
8000 - Reserved for future services
9000 - Reserved for future services
```

---

## 🔍 PORT CONFLICT DETECTION

### Check If a Port Is Available
```powershell
# PowerShell command to check port availability:
$port = 8080
$connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
if ($connection.TcpTestSucceeded) {
    Write-Host "Port $port is IN USE"
} else {
    Write-Host "Port $port is AVAILABLE"
}
```

### Find What's Using a Port
```powershell
# Find process using port 8080:
netstat -ano | findstr :8080
```

### Kill Process on Port
```powershell
# DANGEROUS - Only if you know what you're doing:
Stop-Process -Id 1234 -Force  # Replace 1234 with PID from above
```

---

## 📝 SERVICE STARTUP SEQUENCE (run.bat)

### Order (CRITICAL)
```
1. Cleanup existing processes (prevent conflicts)
2. Pre-flight checks (files exist)
3. Python verification
4. Ollama startup (11434) ← MUST BE FIRST
5. Model verification (llava:7b)
6. Python syntax validation
7. Web GUI startup (8080) ← DEPENDS ON OLLAMA
8. Browser launch
9. Ready message
```

### Why This Order?
- Ollama must start first - it's the AI engine
- Web GUI depends on Ollama being available
- API Server can start independently
- Starting in wrong order = "Connection refused" errors

---

## 🛡️ PORT CONFLICT RESOLUTION

### Symptom 1: "ERR_CONNECTION_REFUSED on localhost:8080"
**Cause**: Web GUI failed to start
**Solution**:
```powershell
# 1. Check if port is available
netstat -ano | findstr :8080

# 2. If something's using it, check what:
tasklist | findstr python

# 3. Kill any orphaned processes:
taskkill /F /IM python.exe

# 4. Restart run.bat
.\run.bat
```

### Symptom 2: "Cannot access http://localhost:11434"
**Cause**: Ollama not running
**Solution**:
```powershell
# 1. Check if Ollama service is running:
Get-Process ollama -ErrorAction SilentlyContinue

# 2. Manually start Ollama:
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe" serve

# 3. In new terminal, verify:
curl http://localhost:11434/api/tags
```

### Symptom 3: "Port 8080 already in use by another service"
**Cause**: Another application using port 8080
**Solution**:
```powershell
# Find what's using port:
netstat -ano | findstr :8080

# Get more info:
Get-Process -Id (netstat -ano | findstr :8080 | % {$_.Split()[-1]})

# Options:
# A) Stop the conflicting service
# B) Change port in run.bat (NOT RECOMMENDED - see notes below)
# C) Use a different machine
```

### Symptom 4: "Multiple instances of web_gui_server running"
**Cause**: Previous instance didn't shut down
**Solution**:
```powershell
# Kill all Python instances:
Get-Process python | Stop-Process -Force

# Wait 5 seconds:
Start-Sleep -Seconds 5

# Restart:
.\run.bat
```

---

## 📂 WHERE EACH PORT IS CONFIGURED

### Port 11434 (Ollama)
```
Files where configured:
├── ultron_config.json
│   └─ "ollama_base_url": "http://localhost:11434"
├── run.bat (Line: set "OLLAMA_PORT=11434")
├── brain.py (searches for changes)
└── api_server.py (uses config)

To change: Edit ultron_config.json "ollama_base_url" → update all 3 files
```

### Port 8080 (Web GUI)
```
Files where configured:
├── run.bat (Line: set "WEB_GUI_PORT=8080")
├── web_gui_server.py (default port)
└── Browser URLs (hardcoded)

To change: Edit run.bat WEB_GUI_PORT → ALSO update browser URLs
WARNING: This is risky - many URLs hardcoded
```

### Port 5000 (API Server)
```
Files where configured:
├── ultron_config.json
│   └─ "api_port": 5000
├── api_server.py (reads from config)
└── Various tool files (read from config)

To change: Edit ultron_config.json "api_port" → restart api_server.py
```

### Port 7861 (LangFlow)
```
Files where configured:
├── ultron_config.json
│   ├─ "langflow_port": 7861
│   ├─ "langflow_api_url": "http://127.0.0.1:7861"
│   └─ "langflow_enabled": true/false

To change: Edit ultron_config.json both entries
WARNING: Not all components read from config
```

### Port 8081 (AutoGen)
```
Files where configured:
├── ultron_config.json
│   ├─ "autogen_studio_port": 8081
│   ├─ "autogen_studio_host": "127.0.0.1"
│   └─ "autogen_studio_enabled": true/false

To change: Edit ultron_config.json all 3 entries
```

---

## 🔧 HOW TO SAFELY CHANGE A PORT

**⚠️ NOT RECOMMENDED - Changing ports breaks many hardcoded URLs**

If you absolutely must change a port:

### Step 1: Document the old port
```
Old Port: 8080
New Port: 8888
Reason: <<explain why>>
Date: <<date>>
Changed By: <<your name>>
```

### Step 2: Update configuration
```json
// ultron_config.json
{
  "api_port": 5001,  // Old: 5000
  "langflow_port": 7862,  // Old: 7861
}
```

### Step 3: Update run.bat
```batch
set "WEB_GUI_PORT=8888"  :: Old: 8080
set "OLLAMA_PORT=11435"  :: Old: 11434
```

### Step 4: Update Python files
```powershell
# Search for old port in all files:
grep -r "8080" . --include="*.py"
grep -r "localhost:8080" . --include="*.py"
grep -r "5000" . --include="*.py"
```

### Step 5: Create CHANGELOG entry
```
## [CHANGED] Port Configuration - [Date]

REASON: [Explain why port was changed]

CHANGES:
- API Server: 5000 → 5001
- Web GUI: 8080 → 8888

AFFECTED FILES:
- ultron_config.json (api_port, web_port)
- run.bat (WEB_GUI_PORT, API_SERVER_PORT)
- api_server.py (line X: reads from config)
- web_gui_server.py (line Y: default port)

TESTING:
- [ ] Web GUI accessible at http://localhost:8888
- [ ] API Server responds at http://localhost:5001/health
- [ ] All services start without conflict
- [ ] Browser console shows no errors
```

### Step 6: Test thoroughly
```powershell
# After changes, test each port:
Test-NetConnection localhost -Port 8888 -ErrorAction SilentlyContinue
Test-NetConnection localhost -Port 5001 -ErrorAction SilentlyContinue
Test-NetConnection localhost -Port 11435 -ErrorAction SilentlyContinue

# Test from browser:
# http://localhost:8888
# http://localhost:5001/health
# http://localhost:11435/api/tags
```

---

## 📋 SERVICE DEPENDENCIES DIAGRAM

```
┌─────────────────────────────────────────────────────┐
│              ULTRON AGENT 3.0                       │
│           Service Dependency Chain                  │
└─────────────────────────────────────────────────────┘

Step 1: System Startup (run.bat)
  └─→ Cleanup existing processes
      └─→ Run pre-flight checks
          └─→ Start Ollama (port 11434) ← MUST SUCCEED
              └─→ Download/verify llava:7b model
                  └─→ Start Web GUI (port 8080) ← DEPENDS ON 11434
                      └─→ Health check Web GUI
                          └─→ Open browser to localhost:8080

Step 2: User Interactions
  ├─→ User accesses http://localhost:8080
  │   └─→ Loads Pokédex GUI (index.html)
  │       └─→ JavaScript calls API at :5000
  │           └─→ Depends on api_server.py running
  │               └─→ api_server.py calls backend services
  │
  ├─→ Voice commands (optional)
  │   └─→ Depends on elevenlabs API key
  │       └─→ Optional, falls back to pyttsx3
  │
  └─→ LLM queries
      └─→ All requests go through API server (5000)
          └─→ API server queries Ollama (11434)
              └─→ Ollama returns response

Failure Points:
  ❌ Ollama (11434) down → No AI reasoning → GUI loads but no intelligence
  ❌ Web GUI (8080) down → Can't access interface → Use API directly
  ❌ API Server (5000) down → Console/voice/tools fail → Manual API calls still work
```

---

## ✅ STARTUP VERIFICATION CHECKLIST

After starting run.bat, verify everything:

```
OLLAMA SERVICE
  □ Check: netstat -ano | findstr :11434
  □ Test: curl http://localhost:11434/api/tags
  □ Expect: JSON response with model list
  □ If fails: See "Cannot access http://localhost:11434" solution above

WEB GUI SERVER
  □ Check: netstat -ano | findstr :8080
  □ Test: curl http://localhost:8080
  □ Expect: HTML content or redirect
  □ If fails: Check logs in "ULTRON-WebGUI" window

BROWSER CONNECTION
  □ Check: Open http://localhost:8080 in browser
  □ Expect: Pokédex GUI loads completely
  □ Check browser console (F12) for errors
  □ If fails: Check Web GUI window for error messages

API SERVER (separate startup)
  □ Check: netstat -ano | findstr :5000
  □ Test: curl http://localhost:5000/health
  □ Expect: JSON response with status
  □ If fails: Start with: python api_server.py

OLLAMA MODEL
  □ Check: curl http://localhost:11434/api/tags
  □ Expect: llava:7b in response
  □ If fails: Run: ollama pull llava:7b

ALL SYSTEMS GO?
  □ Ollama: ✅ Running and responding
  □ Web GUI: ✅ Running and accessible
  □ API Server: ✅ Running (if started)
  □ Model: ✅ Downloaded and ready
  □ Browser: ✅ No console errors
  □ SYSTEM READY: ✅ YES - Ready for use
```

---

## 📚 RELATED DOCUMENTATION

```
See also:
├── .github/copilot-instructions.md
│   └─ Port configuration section (search for "Ports:")
├── SYSTEM_ARCHITECTURE.md
│   └─ Service startup sequence diagram
├── GUI_COMPLETE_PACKAGE_SUMMARY.md
│   └─ GUI fix deployment (uses port 8080)
├── ultron_config.json
│   └─ All port definitions in one place
└── run.bat
    └─ Service startup script (contains port logic)
```

---

## 🚨 EMERGENCY PROCEDURES

### If GUI is completely broken (port conflict)

```powershell
# Option 1: Kill all Python and restart
taskkill /F /IM python.exe
Start-Sleep -Seconds 3
.\run.bat

# Option 2: Check what's using ports
netstat -ano | findstr :8080
netstat -ano | findstr :5000
netstat -ano | findstr :11434

# Option 3: If Ollama stuck, restart Windows
# (Most severe - only if nothing else works)
```

### If services won't start

```powershell
# 1. Check run.bat logs:
Get-Content ultron_master_startup.log -Tail 50

# 2. Check for Python errors:
python -c "import ultron_config; print('Config OK')"

# 3. Verify Python syntax:
python -m py_compile main.py web_gui_server.py

# 4. Check Ollama manually:
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe" serve
```

---

## 📊 CONFIGURATION QUICK REFERENCE

```json
// Current ultron_config.json port settings:
{
  "api_port": 5000,                        // API Server
  "ollama_base_url": "http://localhost:11434",  // Ollama backend
  "langflow_port": 7861,                   // LangFlow (disabled)
  "langflow_api_url": "http://127.0.0.1:7861", // LangFlow URL
  "autogen_studio_port": 8081,             // AutoGen (disabled)
  "autogen_studio_host": "127.0.0.1",     // AutoGen host
  "diagnostics_dashboard_port": 5001       // Diagnostics (disabled)
}
```

```batch
:: Current run.bat port settings:
set "OLLAMA_PORT=11434"
set "WEB_GUI_PORT=8080"
set "ADB_BACKEND_PORT=5003"
set "API_SERVER_PORT=5000"
```

---

## 🎯 KEY TAKEAWAYS

1. **Ports are locked and mandatory** - Don't change without full documentation
2. **Startup order matters** - Ollama → Web GUI → API Server
3. **All conflicts must be resolved** - Failing to do so breaks the entire system
4. **Documentation is critical** - Every change must be logged
5. **Use the CHANGELOG** - Future developers need to understand history

---

## 📞 SUPPORT CHECKLIST

Before asking for help, verify:

- [ ] run.bat is running and not showing errors
- [ ] `netstat -ano | findstr :8080` shows something listening
- [ ] `curl http://localhost:8080` works (or browser shows page)
- [ ] `curl http://localhost:11434/api/tags` shows model list
- [ ] Browser F12 console shows no critical errors
- [ ] This file was read and understood

---

**Last Updated**: October 29, 2025
**Criticality**: 🔴 CRITICAL - Core system operation
**Modification**: ⚠️ EXTREMELY DANGEROUS - High risk of complete failure

