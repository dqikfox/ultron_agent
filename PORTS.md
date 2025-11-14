# ULTRON Agent - Port Management

## Current Port Assignments

### Active Services (Currently Running)
| Port  | Service                    | Process | Status  | Notes                                    |
|-------|----------------------------|---------|---------|------------------------------------------|
| 8080  | Web GUI Server             | Python  | ✅ ACTIVE | web_gui_server.py - Main Pokédex GUI    |
| 11434 | Ollama LLM Backend         | Ollama  | ✅ ACTIVE | Local AI model inference                 |
| 5175  | Unknown Python Service     | Python  | ✅ ACTIVE | Needs identification                     |

### Configured Services (Not Currently Running)
| Port  | Service                    | File                        | Status      | Notes                                    |
|-------|----------------------------|-----------------------------|-------------|------------------------------------------|
| 5000  | API Server                 | api_server.py               | ⚠️ CONFIGURED | Flask REST API                           |
| 8002  | NVIDIA Enhanced Chat       | nvidia_enhanced_ultron.py   | ✅ AVAILABLE | **PORT 8002 - READY TO USE**             |
| 8001  | Mobile Web Interface       | mobile_web_interface_tool.py| ⚠️ CONFIGURED | Flask mobile UI                          |
| 5175  | Frontend Server            | frontend_server.py          | ⚠️ CONFLICT  | May conflict with active service on 5175|

## Port Status Analysis

### Port 8002 Status: ✅ **AVAILABLE FOR USE**
**Finding**: Port 8002 is NOT currently in use. The NVIDIA service (`nvidia_enhanced_ultron.py`) is configured for this port but **NOT running**.

**Configuration**: Changed from port 8000 to port 8002 to avoid potential future conflicts.

**Resolution**: Port 8000 can be safely used for nvidia_enhanced_ultron.py. The changes already made to index.html (line 665) pointing to port 8000 are **CORRECT**.

### Available Ports in 8000-9000 Range
Based on netstat scan, the following ports are **AVAILABLE**:
- 8000 ✅ (Available for other services)
- 8001 ✅ (Configured but not running)
- 8002 ✅ (Assigned to NVIDIA Enhanced Chat)
- 8003-8079 ✅ (All available)
- 8081-8999 ✅ (All available)

### Port Conflicts to Resolve
1. **Port 5175**: Currently in use by unknown Python process
   - `frontend_server.py` is configured for port 5175
   - Need to identify which service is actually using this port
   - May need to assign frontend_server.py to different port (e.g., 5176)

## Port Assignment Strategy

### Port Ranges
- **5000-5999**: API and auxiliary services
  - 5000: Primary API server
  - 5175: Frontend UI server (CONFLICT - needs resolution)
  - 5176: Available for reassignment

- **8000-8999**: AI and specialized services
  - 8002: NVIDIA Enhanced Chat ✅ **ASSIGNED**
  - 8001: Mobile interface
  - 8000, 8003+: Available for future expansion

- **11000-11999**: External integrations
  - 11434: Ollama LLM backend

## Health Check Integration

### Startup Port Checks (run.bat)
The following checks should be added to run.bat health check system:

```batch
:: Port Availability Check
echo [CHECK] Verifying port availability...

:: Check if port 8080 is free (GUI server)
netstat -ano | findstr ":8080.*LISTENING" >nul
if %errorlevel% equ 0 (
    echo [WARNING] Port 8080 already in use - GUI server may conflict
) else (
    echo [OK] Port 8080 available for GUI server
)

:: Check if port 11434 is responding (Ollama)
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Ollama service responding on port 11434
) else (
    echo [WARNING] Ollama service not responding on port 11434
)
```

## Current Configuration Files

### nvidia_enhanced_ultron.py
**Current Configuration**: Line 419
```python
uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
```
**Status**: ✅ Correct - Port 8002 is available

### index.html (GUI)
**Current Configuration**: Line 665
```javascript
onclick="window.open('http://localhost:8002', '_blank')"
```
**Status**: ✅ Correct - Points to NVIDIA service on port 8002

### api_server.py
**Current Configuration**: Default port 5000 (Flask)
**Status**: ⚠️ Not currently running

### mobile_web_interface_tool.py
**Current Configuration**: Port 8001 (Flask)
**Status**: ⚠️ Not currently running

## Troubleshooting Guide

### "Port Already in Use" Errors

1. **Check which process is using the port**:
   ```powershell
   netstat -ano | findstr ":PORT"
   tasklist | findstr "PID"
   ```

2. **Kill the process if needed**:
   ```powershell
   Stop-Process -Id PID -Force
   ```

3. **Verify port is free**:
   ```powershell
   netstat -ano | findstr ":PORT.*LISTENING"
   ```

### Starting NVIDIA Service

1. **Verify port 8002 is available**:
   ```powershell
   netstat -ano | findstr ":8002"
   # Should return empty (port free)
   ```

2. **Start the service**:
   ```bash
   python nvidia_enhanced_ultron.py
   ```

3. **Verify service is running**:
   ```bash
   curl http://localhost:8002/health
   ```

4. **Test from GUI**:
   - Click "Open NVIDIA Chat" button
   - Should open http://localhost:8002

## Next Steps

### Immediate Actions
1. ✅ **VERIFIED**: Port 8002 is available for NVIDIA service
2. ✅ **VERIFIED**: GUI link correctly points to port 8002
3. ✅ **COMPLETE**: Implemented _get_nvidia_status() method in web_gui_server.py
4. ⚠️ **TODO**: Identify what's using port 5175
5. ⚠️ **TODO**: Start NVIDIA service and test functionality

### Future Enhancements
1. Add port conflict detection to run.bat startup
2. Create dynamic port assignment system
3. Add port status to GUI dashboard
4. Implement automatic port fallback (if 8000 in use, try 8001, etc.)

## Port Management Best Practices

1. **Always check before assigning**: Use netstat to verify port availability
2. **Document all assignments**: Keep this file updated
3. **Use health checks**: Integrate port checks into run.bat
4. **Graceful fallbacks**: Services should try alternate ports if primary is taken
5. **Clear error messages**: Tell user which port is needed and what's blocking it

---

**Last Updated**: January 2025
**Status**: Port 8000 confirmed AVAILABLE for NVIDIA service ✅
