# ULTRON Agent v3.0.4 - Service URLs & Links

Complete list of all accessible services, APIs, and interfaces for the ULTRON Agent system.

---

## 🌐 Primary Services

### Web GUI (Pokédex Interface)
**Port**: 8080
**Status**: Primary user interface
**URL**: `http://localhost:8080/`

- **Features**:
  - Retro Pokédex-style interface
  - Voice control with microphone
  - Command execution
  - Real-time feedback
  - WebSocket integration

---

### REST API Server
**Port**: 5000
**Status**: Core API endpoint
**URL**: `http://localhost:5000/`

#### API Endpoints:

**Health & Status**:
- `http://localhost:5000/health` - System health check
- `http://localhost:5000/status` - Current system status
- `http://localhost:5000/api/system-status` - Detailed system status

**Command Execution**:
- `http://localhost:5000/command` - POST: Execute commands
- `http://localhost:5000/api/execute` - POST: Execute with context
- `http://localhost:5000/api/tools/*` - Tool operations

**Model Management**:
- `http://localhost:5000/api/model/list` - GET: List available models
- `http://localhost:5000/api/model/current` - GET: Current model
- `http://localhost:5000/api/model/switch` - POST: Switch models
  ```bash
  curl -X POST http://localhost:5000/api/model/switch \
    -H "Content-Type: application/json" \
    -d '{"model": "llama3.1"}'
  ```

**Tool Operations**:
- `http://localhost:5000/api/tools/list` - List available tools
- `http://localhost:5000/api/tools/execute` - Execute tool
- `http://localhost:5000/api/tools/schema` - Get tool schema

**Voice Operations**:
- `http://localhost:5000/api/voice/start` - Start voice session
- `http://localhost:5000/api/voice/stop` - Stop voice session
- `http://localhost:5000/api/voice/status` - Voice status

---

### Diagnostics Dashboard
**Port**: 5001
**Status**: System monitoring and diagnostics
**URL**: `http://localhost:5001/`

- **Features**:
  - Real-time system metrics
  - Performance monitoring
  - Error history tracking
  - Circuit breaker status
  - Auto-export diagnostics (24-hour intervals)

---

### LangFlow Integration
**Port**: 7861
**Status**: Visual workflow builder
**URL**: `http://127.0.0.1:7861/`

- **API URL**: `http://127.0.0.1:7861/api`
- **Features**:
  - Workflow creation and management
  - Component integration
  - Flow execution and monitoring

---

### AutoGen Studio (Optional)
**Port**: 8081
**Status**: Multi-agent orchestration (disabled by default)
**URL**: `http://127.0.0.1:8081/`

- **Configuration**:
  - Host: 127.0.0.1
  - Max agents: 10
  - Session timeout: 3600 seconds
  - Default LLM: gpt-4

---

### AI Chat Server
**Port**: 8000
**Status**: Dedicated AI chat endpoint
**URL**: `http://localhost:8000/`

- **Features**:
  - Conversational AI
  - Context preservation
  - Multi-turn dialogue

---

### Frontend UI Server
**Port**: 5175
**Status**: Alternative web interface
**URL**: `http://localhost:5175/`

- **Features**:
  - Modern web-based UI
  - Alternative to port 8080 GUI

---

### Mobile Web Interface
**Port**: 8001
**Status**: Mobile-optimized interface
**URL**: `http://localhost:8001/`

- **Features**:
  - Mobile-responsive design
  - Touch-optimized controls
  - Mobile voice integration

---

## 🔌 Local AI Services

### Ollama Backend
**Port**: 11434
**Status**: Local LLM inference engine
**URL**: `http://localhost:11434/`

#### Ollama API Endpoints:

**Model Management**:
- `http://localhost:11434/api/tags` - GET: List loaded models
- `http://localhost:11434/api/pull` - POST: Pull model
  ```bash
  curl -X POST http://localhost:11434/api/pull \
    -H "Content-Type: application/json" \
    -d '{"name": "llava:7b"}'
  ```

**Generation**:
- `http://localhost:11434/api/generate` - POST: Generate text
  ```bash
  curl -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
      "model": "llava:7b",
      "prompt": "Tell me about AI",
      "stream": false
    }'
  ```

**Chat API**:
- `http://localhost:11434/api/chat` - POST: Chat endpoint
  ```bash
  curl -X POST http://localhost:11434/api/chat \
    -H "Content-Type: application/json" \
    -d '{
      "model": "llava:7b",
      "messages": [
        {"role": "user", "content": "Hello"}
      ],
      "stream": false
    }'
  ```

**Embeddings**:
- `http://localhost:11434/api/embeddings` - Generate embeddings

**Health Check**:
- `http://localhost:11434/api/health` - Server health status

---

## ☁️ Cloud Services

### AWS Bedrock Integration
**Status**: Cloud AI models
**Endpoint**: `https://your-api-endpoint.amazonaws.com/prod`
**Region**: us-east-1

**Configuration**:
- Default Model: amazon.nova-pro-v1:0
- Timeout: 30 seconds
- Status: Disabled by default (enable in config)

---

## 📊 Monitoring & Diagnostics

### Performance Metrics
- **Monitoring Interval**: 10 seconds
- **Auto-Export**: Every 24 hours
- **Dashboard**: Port 5001

### System Checks
Run diagnostics:
```bash
# Quick health check
curl http://localhost:5000/health

# Full diagnostics
curl http://localhost:5001/

# Ollama connectivity
curl http://localhost:11434/api/tags
```

---

## 🚀 Quick Access Patterns

### Development/Testing
```bash
# Start minimal agent
python main.py

# Start full system with GUI
.\run.bat

# Check GUI availability
curl http://localhost:8080/

# Check API availability
curl http://localhost:5000/health

# Check Ollama availability
curl http://localhost:11434/api/tags
```

### Model Testing
```bash
# Test current model
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llava:7b", "prompt": "test", "stream": false}'

# List available models
curl http://localhost:11434/api/tags

# Switch active model (via REST API)
curl -X POST http://localhost:5000/api/model/switch \
  -d '{"model": "deepseek-r1:14b"}' \
  -H "Content-Type: application/json"
```

### Voice Testing
```bash
# Start voice session
curl -X POST http://localhost:5000/api/voice/start

# Check voice status
curl http://localhost:5000/api/voice/status

# Stop voice session
curl -X POST http://localhost:5000/api/voice/stop
```

---

## 🔐 Security Notes

### Environment Variables Required
```bash
# Voice Service
ELEVENLABS_APIKEY=your_key

# Cloud Services
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_key

# Azure Services (Optional)
AZURE_LUIS_ENDPOINT=your_endpoint
AZURE_LUIS_KEY=your_key
AZURE_LUIS_APP_ID=your_id
AZURE_TEXT_ANALYTICS_ENDPOINT=your_endpoint
AZURE_TEXT_ANALYTICS_KEY=your_key
AZURE_SPEECH_KEY=your_key
```

### Access Control
- **GUI (Port 8080)**: Public localhost access
- **API (Port 5000)**: Public localhost access with optional auth
- **Diagnostics (Port 5001)**: Admin access (no auth by default)
- **Ollama (Port 11434)**: Local-only access

---

## 📝 Configuration Reference

All service ports defined in `ultron_config.json`:

```json
{
  "api_host": "127.0.0.1",
  "api_port": 5000,
  "diagnostics_dashboard_port": 5001,
  "autogen_studio_port": 8081,
  "langflow_port": 7861,
  "ollama_base_url": "http://localhost:11434"
}
```

---

## ✅ Service Startup Sequence

**Order of Service Initialization** (from `run.bat`):

1. **Port Check** (5000, 8080) - Verify availability
2. **Ollama** (11434) - AI backend
3. **API Server** (5000) - REST endpoints
4. **Web GUI** (8080) - User interface
5. **Health Checks** - 5 automated tests
6. **Auto-run Commands** - Startup tasks

**Startup Command**:
```powershell
.\run.bat
```

**Manual Startup**:
```powershell
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start agent
python main.py

# Terminal 3: Start additional services (optional)
python web_gui_server.py
python api_server.py
```

---

## 🔧 Troubleshooting

### Service Not Responding
```bash
# Check if port is in use
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

# Kill process on port
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess -Force

# Restart service
.\run.bat
```

### Connection Issues
```bash
# Test Ollama connectivity
curl -v http://localhost:11434/api/tags

# Test API connectivity
curl -v http://localhost:5000/health

# Test GUI availability
curl -v http://localhost:8080/
```

### Model Switching
```bash
# Get current model
curl http://localhost:5000/api/model/current

# List available
ollama list

# Pull new model
ollama pull deepseek-r1:14b

# Switch via API
curl -X POST http://localhost:5000/api/model/switch \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:14b"}'
```

---

## 📱 Access from External Machines

**Note**: For external access, configure firewall and update host binding:

```json
{
  "api_host": "0.0.0.0",
  "gui_bind_address": "0.0.0.0"
}
```

Then access via:
- `http://<machine-ip>:8080/` - GUI
- `http://<machine-ip>:5000/` - API
- `http://<machine-ip>:5001/` - Diagnostics

---

## 📚 Related Documentation

- **API Documentation**: See `API.md` for detailed endpoint specs
- **Quick Reference**: See `QUICK_REFERENCE.md` for command examples
- **Architecture**: See `SYSTEM_ARCHITECTURE.md` for service connections
- **Setup Guide**: See `REQUIREMENTS_SETUP.md` for environment setup

---

**Last Updated**: October 31, 2025
**Version**: ULTRON Agent v3.0.4
**Status**: ✅ All services operational and documented
