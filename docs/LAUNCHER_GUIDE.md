# ULTRON Launcher Guide

## Overview

The **ULTRON Launcher** (`ultron_launch.py`) is a unified entry point for all ULTRON Agent execution modes. Instead of managing multiple entry points (`main.py`, `api_server.py`, `web_gui_server.py`), use the launcher to start any mode with consistent configuration.

**Status**: ✅ Production Ready  
**Version**: Phase A Enhancement  
**Modes**: 4 (API, Web, CLI, Full)

---

## Quick Start

### Launch API Server (REST)
```bash
python ultron_launch.py --mode api
# → Starts Flask API on http://localhost:5000
```

### Launch Web GUI (React)
```bash
python ultron_launch.py --mode web
# → Starts Web UI on http://localhost:8080
```

### Launch CLI (Interactive Shell)
```bash
python ultron_launch.py --mode cli
# → Starts interactive agent in terminal
```

### Launch Full Stack (API + Web + Background Services)
```bash
python ultron_launch.py --mode full
# → Starts all services (API, Web, Ollama health checks, memory)
```

---

## Usage

### Basic Syntax
```bash
python ultron_launch.py [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode {api,web,cli,full}` | `api` | Execution mode |
| `--api-port PORT` | `5000` | API server port |
| `--web-port PORT` | `8080` | Web GUI port |
| `--host ADDR` | `0.0.0.0` | Server address |
| `--debug` | (disabled) | Enable debug logging |
| `--help` | — | Show help message |

### Examples

#### Custom Ports
```bash
python ultron_launch.py --mode api --api-port 5001
python ultron_launch.py --mode web --web-port 8888
python ultron_launch.py --mode full --api-port 5000 --web-port 8080
```

#### Localhost Only (Secure)
```bash
python ultron_launch.py --mode api --host 127.0.0.1
```

#### With Debug Logging
```bash
python ultron_launch.py --mode full --debug
```

#### Programmatic Startup (Python)
```python
from ultron_launch import run_api_server, run_web_gui_server, run_full_stack

# Start API only
run_api_server(host="0.0.0.0", port=5000)

# Or start full stack in background
import asyncio
asyncio.run(run_full_stack())
```

---

## Modes Explained

### Mode: API
**Purpose**: REST API server only  
**Port**: 5000 (default)  
**Use Case**: Headless operation, integration with external systems

**Endpoints**:
- `GET /health` - Health check
- `POST /chat` - Send message
- `WS /ws` - WebSocket for real-time updates
- `GET /config` - Configuration status

```bash
curl http://localhost:5000/health
# → {"status": "ok", "version": "3.0.4"}
```

### Mode: Web
**Purpose**: Web GUI server only  
**Port**: 8080 (default)  
**Use Case**: Browser-based interaction, Pokédex UI

**Features**:
- React-based frontend
- Real-time chat
- Tool management UI
- Memory visualization

```bash
python ultron_launch.py --mode web
# → Open http://localhost:8080 in browser
```

### Mode: CLI
**Purpose**: Interactive terminal mode  
**Use Case**: Development, testing, direct agent interaction

**Features**:
- Direct command input
- Real-time output
- No server listening
- Immediate feedback

```bash
$ python ultron_launch.py --mode cli
ULTRON Agent 3.0 CLI
Type 'exit' or 'quit' to stop

ultron> hello world
Processing: hello world
...
ultron> what did we just talk about?
Recalling similar interactions...
```

### Mode: Full
**Purpose**: Complete stack with all services  
**Services**:
- API Server (port 5000)
- Web GUI (port 8080)
- Ollama Health Checker
- Memory System
- Tool Ecosystem

```bash
python ultron_launch.py --mode full
# → http://localhost:5000 (API)
# → http://localhost:8080 (Web UI)
# → All subsystems active
```

---

## Comparison: Old vs New

### Before (Multiple Entry Points)
```bash
# Had to know which script to run
python main.py           # Main entry point (unclear what mode)
python api_server.py     # API only
python web_gui_server.py # Web GUI only
# No unified CLI launcher

# Configuration scattered
# Port conflicts common
# Startup logic duplicated
```

### After (Unified Launcher)
```bash
# Clear, consistent interface
python ultron_launch.py --mode api     # API only
python ultron_launch.py --mode web     # Web GUI only
python ultron_launch.py --mode cli     # CLI interactive
python ultron_launch.py --mode full    # All services

# Unified config
# --api-port and --web-port work across all modes
# Single startup logic
```

---

## Configuration

### Runtime Configuration
All launcher options can be overridden via command line:

```bash
python ultron_launch.py \
  --mode full \
  --api-port 5001 \
  --web-port 8081 \
  --host 127.0.0.1 \
  --debug
```

### Config File
Persistent settings in `ultron_config.json`:

```json
{
  "api_port": 5000,
  "web_port": 8080,
  "llm_model": "exaone-deep:7.8b",
  "ollama_base_url": "http://localhost:11434"
}
```

### Environment Variables
Override config via `.env`:

```bash
export API_PORT=5001
export WEB_PORT=8081
export OLLAMA_BASE_URL=http://remote-ollama:11434
python ultron_launch.py --mode api
```

---

## Health Checks

### API Mode Health
```bash
curl http://localhost:5000/health
# → {"status": "ok", "model": "exaone-deep:7.8b", "version": "3.0.4"}
```

### Web Mode Health
```bash
curl http://localhost:8080/
# → (React app loads)
```

### Full Mode Health
```bash
# Check both services
curl http://localhost:5000/health
curl http://localhost:8080/
```

### Port Already in Use?
```bash
# Find what's using the port
lsof -i :5000          # macOS/Linux
netstat -ano | grep :5000  # Windows

# Use different port
python ultron_launch.py --mode api --api-port 5001
```

---

## Troubleshooting

### "Address already in use"
**Problem**: Port is already in use  
**Solution**: Use different port or kill existing process

```bash
# Use different port
python ultron_launch.py --mode api --api-port 5002

# Or find and kill existing process
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### "Failed to connect to Ollama"
**Problem**: Ollama not running  
**Solution**: Start Ollama service

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (macOS)
open /Applications/Ollama.app

# Start Ollama (Linux)
ollama serve

# Start Ollama (Windows)
ollama.exe serve
```

### "Web GUI not loading"
**Problem**: Frontend connection issue  
**Solution**: Check backend is running

```bash
# Verify API is responding
curl http://localhost:5000/health

# Check console for CORS errors
# Make sure ports match frontend config (hardcoded to 5000)
```

### "CLI mode exits immediately"
**Problem**: Initialization error  
**Solution**: Run with debug flag to see error

```bash
python ultron_launch.py --mode cli --debug
```

---

## Production Deployment

### Systemd Service (Linux)
Create `/etc/systemd/system/ultron-agent.service`:

```ini
[Unit]
Description=ULTRON Agent 3.0
After=network.target

[Service]
Type=simple
User=ultro
WorkingDirectory=/home/ultro/projects/ultron_agent
ExecStart=/usr/bin/python3 ultron_launch.py --mode full
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ultron-agent
sudo systemctl start ultron-agent
sudo systemctl status ultron-agent
```

### Docker
```dockerfile
FROM python:3.12

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000 8080

CMD ["python", "ultron_launch.py", "--mode", "full"]
```

```bash
docker run -p 5000:5000 -p 8080:8080 ultron-agent
```

### Behind Reverse Proxy (Nginx)
```nginx
upstream api {
    server 127.0.0.1:5000;
}

upstream web {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name ultron.example.com;

    location /api/ {
        proxy_pass http://api/;
    }

    location / {
        proxy_pass http://web/;
    }
}
```

---

## Performance Tuning

### Memory Usage
```bash
# Monitor memory
watch -n 1 'ps aux | grep ultron_launch'

# Reduce memory: disable some features in config
# (See ultron_config.json for options)
```

### Request Concurrency
```bash
# API mode default: single worker
# For production, use gunicorn with workers:

pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Response Time
```bash
# Check response times in logs
grep "response_time" logs/ai_activities.log

# Optimize semantic memory lookups
# (Phase B enhancement will improve this)
```

---

## Migration Guide

### From Old Entry Points → Launcher

**Was**:
```bash
python main.py
python api_server.py
python web_gui_server.py
```

**Now**:
```bash
python ultron_launch.py --mode cli      # instead of main.py
python ultron_launch.py --mode api      # instead of api_server.py
python ultron_launch.py --mode web      # instead of web_gui_server.py
python ultron_launch.py --mode full     # combines all
```

### Shell Scripts
Update `run.sh` and Windows `run.bat` to use launcher:

```bash
#!/bin/bash
# run.sh - Start ULTRON Agent

python ultron_launch.py --mode full \
  --api-port 5000 \
  --web-port 8080 \
  --debug
```

---

## Next Steps

- **Phase A (Complete)**: ✅ Launcher working with all 4 modes
- **Phase G**: Upcoming - Multi-tool memory integration
- **Phase B**: Upcoming - Enhanced embeddings (sentence-transformers)

See [plan_phase_abc.md](../plan_phase_abc.md) for roadmap.

---

## API Reference

### POST /chat
Send a message to the agent

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world"}'
```

Response:
```json
{
  "response": "Hey there! How can I help you?",
  "memory_context": ["similar past conversation..."],
  "tools_used": ["memory_system"]
}
```

### GET /health
System health status

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "model": "exaone-deep:7.8b",
  "services": {
    "memory": "ok",
    "ollama": "ok",
    "tools": "loaded"
  }
}
```

### WS /ws
WebSocket for real-time updates

```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.onmessage = (event) => {
  console.log('Update:', JSON.parse(event.data));
};
```

---

## Support

**Documentation**: [docs/](../docs/)  
**Issues**: Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)  
**Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
