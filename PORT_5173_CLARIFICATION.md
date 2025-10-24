# PORT 5173 vs 5175 - CLARIFICATION

## ⚠️ IMPORTANT: Port 5173 is NOT used by ULTRON Agent

### The Confusion
Port **5173** is the **default port for Vite** (a frontend build tool), but **ULTRON Agent does NOT use Vite**.

### Correct Ports
ULTRON Agent uses **port 5175** for the Frontend UI server.

## ULTRON Agent Ports

| Service | Port | URL | Status |
|---------|------|-----|--------|
| **Web GUI (ATLAS)** | 8080 | http://localhost:8080 | ✅ PRIMARY GUI |
| **Frontend UI** | 5175 | http://localhost:5175 | ✅ ACTIVE |
| **NVIDIA Chat** | 8002 | http://localhost:8002 | ✅ ACTIVE |
| **API Server** | 5000 | http://localhost:5000 | ✅ ACTIVE |
| **Ollama LLM** | 11434 | http://localhost:11434 | ✅ BACKEND |

## Why Port 5173 Doesn't Work

1. **Port 5173 is NOT configured** in ULTRON Agent
2. **No service is running** on port 5173
3. **ULTRON uses port 5175** for the Frontend UI

## Correct Usage

### ❌ WRONG (will fail)
```
http://localhost:5173  → Connection refused
```

### ✅ CORRECT
```
http://localhost:5175  → Frontend UI works
http://localhost:8080  → Web GUI works (recommended)
```

## How to Access ULTRON

1. **Start all services**:
   ```cmd
   run.bat
   ```

2. **Open browser to PRIMARY GUI**:
   ```
   http://localhost:8080
   ```
   This is the main ATLAS Neural Core interface with all features.

3. **Alternative Frontend** (optional):
   ```
   http://localhost:5175
   ```
   This is the secondary Pokédex interface.

## Remote Access

### Local Network
- Web GUI: http://192.168.1.131:8080
- Frontend: http://192.168.1.131:5175
- NVIDIA: http://192.168.1.131:8002

### Internet (after port forwarding)
- Web GUI: http://YOUR_PUBLIC_IP:8080
- Frontend: http://YOUR_PUBLIC_IP:5175
- NVIDIA: http://YOUR_PUBLIC_IP:8002

## Configuration Files

The ports are defined in:
- `run.bat` - Launches frontend_server.py on port 5175
- `frontend_server.py` - Configured for port 5175
- `web_gui_server.py` - Configured for port 8080
- `nvidia_enhanced_ultron.py` - Configured for port 8002

## If You Need Port 5173

If you specifically need port 5173 for another application (like a Vite project), that's fine - it won't conflict with ULTRON since ULTRON doesn't use it.

## Summary

**Remember**:
- ✅ Use http://localhost:8080 (main GUI)
- ✅ Use http://localhost:5175 (frontend UI)
- ❌ Do NOT use http://localhost:5173 (not configured)

---

**Updated**: October 24, 2025
**ULTRON Agent Version**: 3.0
