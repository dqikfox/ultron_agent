# ULTRON AGENT 3.0 - PRODUCTION DEPLOYMENT GUIDE

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Starting Services](#starting-services)
6. [Health Checks](#health-checks)
7. [Troubleshooting](#troubleshooting)
8. [Monitoring](#monitoring)

---

## Prerequisites

### System Requirements
- **Python**: 3.10+ (must have)
- **RAM**: Minimum 2GB (recommended 4GB+)
- **Disk Space**: Minimum 1GB (recommended 5GB+)
- **CPU Cores**: Minimum 2 (recommended 4+)
- **OS**: Windows, macOS, or Linux

### Software Requirements
- Python 3.10+
- Ollama (for local LLM inference)
- Git (optional, for repository management)

### Network Requirements
- Stable internet connection (for API services)
- Ports available: 5000, 8000, 8080, 11434
- Connection to Ollama service (localhost:11434)

---

## Installation

### Step 1: Pre-Deployment Validation

Run the pre-deployment checklist to verify system readiness:

```bash
python pre_deployment_checklist.py
```

This will check:
- Python version and executable
- System resources (RAM, disk, CPU)
- Dependencies installation
- Configuration integrity
- Port availability
- Network connectivity
- Ollama service status
- Model availability

**All checks must pass before proceeding to Step 2.**

### Step 2: Deploy ment Validator

If you need more detailed information:

```bash
python deployment_validator.py
```

This provides comprehensive validation across 7 categories with 16+ checks.

### Step 3: Prepare Environment

Ensure you have the required Python packages:

```bash
# On Windows (cmd or PowerShell)
pip install -r requirements.txt

# On macOS/Linux
pip3 install -r requirements.txt
```

Critical packages verified by deployment validator:
- pytest
- aiohttp
- flask
- psutil
- requests

---

## Configuration

### Configuration File: ultron_config.json

The main configuration file `ultron_config.json` contains all deployment settings.

#### Key Settings

**Required Settings:**
```json
{
  "llm_model": "llava:7b",
  "ollama_base_url": "http://localhost:11434",
  "api_port": 5000,
  "web_gui_port": 8080,
  "chat_port": 8000,
  "api_host": "127.0.0.1",
  "debug": false,
  "log_level": "INFO"
}
```

**Optional Settings:**
```json
{
  "voice_enabled": false,
  "vision_enabled": true,
  "memory_enabled": true,
  "tools_enabled": true,
  "offline_mode": false,
  "max_concurrent_requests": 10
}
```

### Validation

Verify configuration is valid:

```bash
# Windows
python -m json.tool ultron_config.json

# macOS/Linux
python3 -m json.tool ultron_config.json
```

If output shows no errors, configuration is valid JSON.

---

## Verification

### Step 1: Run Pre-Deployment Checklist

```bash
python pre_deployment_checklist.py
```

Expected output:
```
[PASS] Python & Environment: 2/3 checks
[PASS] System Resources: 3/3 checks
[PASS] Dependencies: 2/2 checks
[PASS] Configuration: 3/3 checks
[PASS] Network: 1/2 checks
[PASS] Services: 2/3 checks

System validation passed! Ready to proceed with deployment:
  1. Review deployment guide: DEPLOYMENT_GUIDE.md
  2. Start services: python main.py
  3. Access web GUI: http://localhost:8080
  4. Monitor logs: logs/
  5. Run health checks: curl http://localhost:5000/health
```

### Step 2: Verify All Components

Each check verifies a critical component:

| Check | Component | Status |
|-------|-----------|--------|
| Python Version | Runtime | Must be 3.10+ |
| Configuration File | Settings | Must exist and be valid JSON |
| Critical Dependencies | Packages | All must be installed |
| Port Availability | Network | Ports must not be in use |
| Ollama Service | LLM Backend | Must respond to /api/tags |
| Model Availability | AI Models | At least one model must be loaded |

---

## Starting Services

### Option 1: Quick Start (Recommended)

Run all services with auto-health checks:

```bash
# Windows
.\run.bat

# macOS/Linux
./run.sh
```

This starts:
1. Ollama service (if not running)
2. API server on port 5000
3. Web GUI on port 8080
4. Chat service on port 8000

### Option 2: Manual Startup

Start individual services:

```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Start web GUI
python web_gui_server.py

# Terminal 3: Start main agent (optional)
python main.py

# Terminal 4: Monitor logs (optional)
tail -f logs/agent_core.log
```

### Option 3: Docker (Production)

For containerized deployment:

```bash
# Build Docker image
docker build -t ultron-agent:latest .

# Run container
docker-compose up -d

# View logs
docker-compose logs -f api
```

---

## Health Checks

### API Health Check

```bash
# Check if API is responding
curl http://localhost:5000/health

# Expected response:
# {"status": "ok", "timestamp": "2025-11-03T..."}
```

### Ollama Health Check

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Expected response:
# {"models": [...]}
```

### Web GUI Health Check

```bash
# Access web GUI
start http://localhost:8080

# You should see the ULTRON Agent Pokédex interface
```

### Full Health Check Script

Run comprehensive health checks:

```bash
python pre_deployment_checklist.py
```

---

## Troubleshooting

### Issue: "Ollama not responding"

**Solution:**
1. Verify Ollama is running: `ollama serve`
2. Check Ollama port: `curl http://localhost:11434/api/tags`
3. Verify Ollama base URL in config: `ultron_config.json`

### Issue: "Port already in use"

**Solution:**
1. Identify process using port:
   - Windows: `netstat -ano | findstr :5000`
   - macOS/Linux: `lsof -i :5000`
2. Kill process: `taskkill /PID <PID> /F` (Windows) or `kill -9 <PID>` (macOS/Linux)
3. Wait 30 seconds and restart

### Issue: "API Health Check failing"

**Solution:**
1. Verify API server started: `python api_server.py`
2. Check for errors: `tail -f logs/api_server.log`
3. Verify port 5000 is available: `netstat -ano | findstr :5000`

### Issue: "Configuration Key Missing"

**Solution:**
1. Check `ultron_config.json` exists
2. Validate JSON: `python -m json.tool ultron_config.json`
3. Add missing keys (see Configuration section)

---

## Monitoring

### Logs Location

Service logs are stored in `logs/` directory:

```
logs/
├─ agent_core.log          # Main agent activity
├─ brain.log               # AI reasoning
├─ api_activities.log      # API requests/responses
├─ file_changes.log        # File operations
├─ web_gui_server.log      # Web GUI events
└─ deployment.log          # Deployment/startup events
```

### Log Monitoring

Real-time log monitoring:

```bash
# Watch API log
tail -f logs/api_activities.log

# Watch all logs
tail -f logs/*.log

# Search logs for errors
grep "ERROR" logs/*.log

# Recent errors
grep "ERROR" logs/*.log | tail -20
```

### Performance Monitoring

Monitor system resources:

```bash
# Windows
Get-Process python | Select-Object ProcessName, CPU, Memory

# macOS/Linux
ps aux | grep python | grep -v grep
```

---

## Deployment Checklist

Complete this checklist before considering deployment complete:

- [ ] Pre-deployment validation passed (`python pre_deployment_checklist.py`)
- [ ] Python version is 3.10+ (`python --version`)
- [ ] All dependencies installed (`pip list | grep -E "pytest|aiohttp|flask"`)
- [ ] Configuration file exists and is valid (`ultron_config.json`)
- [ ] Ollama service is running (`curl http://localhost:11434/api/tags`)
- [ ] All ports are available (5000, 8000, 8080, 11434)
- [ ] Sufficient system resources (2GB+ RAM, 1GB+ disk)
- [ ] API health check passes (`curl http://localhost:5000/health`)
- [ ] Web GUI is accessible (`http://localhost:8080`)
- [ ] Models are available (`curl http://localhost:11434/api/tags`)
- [ ] Logs directory exists and is writable (`logs/`)
- [ ] No critical errors in startup logs (`grep ERROR logs/*.log`)

---

## Production Considerations

### 1. Security
- Use HTTPS for web GUI (configure reverse proxy)
- Implement authentication for API endpoints
- Restrict network access to trusted sources
- Use environment variables for sensitive config

### 2. Scalability
- Run API behind load balancer
- Use message queue for async tasks
- Implement caching layer (Redis)
- Monitor concurrent request limits

### 3. Reliability
- Setup automatic restart (systemd, supervisor)
- Implement backup/restore procedures
- Setup monitoring and alerting
- Use process manager (supervisord, systemd)

### 4. Performance
- Enable response caching
- Optimize model loading times
- Use async operations where possible
- Monitor and tune database queries

---

## Support

For deployment issues:
1. Check troubleshooting section above
2. Review logs in `logs/` directory
3. Run `python pre_deployment_checklist.py` for diagnostics
4. Check GitHub issues for similar problems
5. Contact support with logs and error messages

---

## Next Steps

After successful deployment:
1. Access web GUI: `http://localhost:8080`
2. Test basic functionality (voice, commands)
3. Review logs for any warnings
4. Setup monitoring and alerts
5. Configure backup and recovery procedures
6. Document your deployment configuration

---

**Deployment Status: Ready for Production**

Version: ULTRON Agent 3.0
Date: November 2025
Last Updated: Phase 4 Part 3
