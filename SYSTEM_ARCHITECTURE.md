# ULTRON Agent 3.0 - System Architecture & Setup Guide

**Last Updated**: October 24, 2025
**Version**: 3.0
**Status**: Production

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Service Architecture](#service-architecture)
3. [Port Dependencies](#port-dependencies)
4. [Startup Sequence](#startup-sequence)
5. [Configuration System](#configuration-system)
6. [Service Connections](#service-connections)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [Environment Variables](#environment-variables)
9. [Troubleshooting](#troubleshooting)

---

## System Overview

ULTRON Agent 3.0 is a **multi-service AI platform** with these core characteristics:
- **Voice-First Architecture**: Integrated speech recognition and synthesis
- **Local LLM Backend**: Ollama serving models like `llava:7b`
- **Web-Based GUI**: Pokédex-themed interface on port 8080
- **Event-Driven Design**: Async pub/sub messaging between components
- **Plugin-Based Tools**: Auto-discovered from `tools/` directory

### Key Components

```
┌─────────────────────────────────────────────────────────────┐
│                    ULTRON Agent 3.0                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Web GUI    │  │  API Server  │  │  AI Backend  │      │
│  │  Port 8080   │◄─┤  Port 5000   │◄─┤ Ollama:11434 │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                         │                                    │
│                  ┌──────▼──────┐                            │
│                  │ agent_core  │                            │
│                  │   brain.py  │                            │
│                  │   voice.py  │                            │
│                  └─────────────┘                            │
│                         │                                    │
│                  ┌──────▼──────┐                            │
│                  │ Event System│                            │
│                  │  (Pub/Sub)  │                            │
│                  └─────────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Service Architecture

### 1. Ollama LLM Backend
**File**: External service (Ollama)
**Port**: 11434
**Purpose**: Local LLM inference for AI reasoning
**Startup**: Via `run.bat` or manual `ollama serve`
**Health Check**: `curl http://localhost:11434/api/tags`

**Dependencies**:
- None (foundational service)

**Used By**:
- `brain.py` (AI reasoning)
- `agent_core.py` (model initialization)
- All tools requiring AI assistance

**Configuration**:
```json
{
  "ollama_base_url": "http://localhost:11434",
  "llm_model": "llava:7b"
}
```

---

### 2. API Server (Flask)
**File**: `api_server.py`
**Port**: 5000
**Purpose**: REST API for command execution and system control
**Startup**: Via `run.bat` or `python api_server.py`

**Dependencies**:
- Ollama (port 11434) - For AI model access
- `agent_core.py` - Agent instance initialization

**Endpoints**:
```
GET  /health              - Health check
POST /command             - Execute agent command
POST /api/voice/toggle    - Toggle voice on/off
GET  /api/voice/status    - Get voice status
POST /api/voice/speak     - Speak text via TTS
POST /api/model/switch    - Switch AI model
GET  /api/tools/*         - Tool-specific endpoints
```

**Used By**:
- Web GUI (port 8080) - API calls from JavaScript
- External clients - REST API integration
- Mobile interface (port 8001)

**Configuration**:
```python
# api_server.py
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 5000
```

---

### 3. Web GUI Server
**File**: `web_gui_server.py`
**Port**: 8080
**Purpose**: Serve static GUI files and WebSocket communication
**Startup**: Via `run.bat` or `python web_gui_server.py`

**Dependencies**:
- API Server (port 5000) - For command execution
- Voice backend (ElevenLabs or pyttsx3) - For TTS

**Serves**:
- `gui/ultron_enhanced/web/index.html` - Main GUI
- `gui/ultron_enhanced/web/app.js` - JavaScript controller
- `gui/ultron_enhanced/web/styles.css` - Pokédex theme

**Used By**:
- End users via web browser (http://localhost:8080)

**Configuration**:
```python
# web_gui_server.py
PORT = 8080
STATIC_DIR = "gui/ultron_enhanced/web"
```

---

### 4. Voice System
**Files**: `voice.py`, `app.js` (frontend)
**Ports**: Uses API server (5000) for TTS/STT coordination
**Purpose**: Speech recognition (STT) and synthesis (TTS)

**Dependencies**:
- **Frontend**: Web Speech API (browser-based)
- **Backend**: ElevenLabs API (cloud) or pyttsx3 (local fallback)
- API Server (port 5000) - `/api/voice/*` endpoints

**Architecture**:
```
┌──────────────────────────────────────────────────┐
│              Voice System Flow                    │
├──────────────────────────────────────────────────┤
│                                                   │
│  User clicks microphone button (app.js)          │
│         │                                         │
│         ▼                                         │
│  toggleVoice() → toggleVoiceChat()                │
│         │                                         │
│         ▼                                         │
│  POST /api/voice/toggle (port 5000)               │
│         │                                         │
│         ▼                                         │
│  web_gui_server.py updates voice state            │
│         │                                         │
│         ▼                                         │
│  Response: { enabled: true }                      │
│         │                                         │
│         ▼                                         │
│  app.js: startVoiceRecognition()                  │
│         │                                         │
│         ▼                                         │
│  Browser Web Speech API starts listening          │
│         │                                         │
│         ▼                                         │
│  User speaks → transcript captured                │
│         │                                         │
│         ▼                                         │
│  POST /command (port 5000) with transcript        │
│         │                                         │
│         ▼                                         │
│  agent_core.py processes command                  │
│         │                                         │
│         ▼                                         │
│  brain.py generates response                      │
│         │                                         │
│         ▼                                         │
│  POST /api/voice/speak with response text         │
│         │                                         │
│         ▼                                         │
│  voice.py generates audio (ElevenLabs/pyttsx3)    │
│         │                                         │
│         ▼                                         │
│  Audio blob returned to app.js                    │
│         │                                         │
│         ▼                                         │
│  app.js plays audio via Audio() element           │
│         │                                         │
│         ▼                                         │
│  onended: Resume voice recognition                │
│                                                   │
└──────────────────────────────────────────────────┘
```

**Configuration**:
```json
{
  "voice_enabled": true,
  "voice_engine": "elevenlabs",
  "stt_engine": "whisper",
  "tts_engine": "elevenlabs",
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY"
}
```

**Environment Variables**:
```bash
export ELEVENLABS_APIKEY=sk-...
```

**See Also**: `VOICE_MICROPHONE_DOCUMENTATION.md` for complete voice system details

---

### 5. Agent Core
**File**: `agent_core.py`
**Purpose**: Central coordinator for all subsystems
**Startup**: Via `main.py` entry point

**Dependencies**:
- All services (initializes everything)

**Responsibilities**:
- Initialize brain.py, voice.py, event_system
- Discover and load tools from `tools/`
- Handle component lifecycle
- Coordinate between services

**Configuration**:
```python
# Loaded from ultron_config.json
config = {
    "llm_model": "llava:7b",
    "ollama_base_url": "http://localhost:11434",
    "voice_enabled": true,
    # ... more settings
}
```

---

### 6. AI Brain
**File**: `brain.py`
**Purpose**: AI reasoning engine with Ollama integration
**Dependencies**:
- Ollama (port 11434) - LLM backend

**Features**:
- Async planning and reasoning
- Response caching for repeated queries
- Multi-model support (llava:7b, llama3.1, deepseek-r1, etc.)
- Timeout handling (default: 30s)

**Configuration**:
```python
# brain.py
OLLAMA_URL = "http://localhost:11434"
DEFAULT_TIMEOUT = 30  # seconds
```

---

## Port Dependencies

**Port Allocation**:

| Port | Service | File | Purpose | Depends On |
|------|---------|------|---------|------------|
| **11434** | Ollama LLM | External | AI model inference | None |
| **5000** | API Server | `api_server.py` | REST API | Ollama (11434) |
| **8080** | Web GUI | `web_gui_server.py` | Static files + WebSocket | API (5000) |
| **8000** | AI Chat | `nvidia_enhanced_ultron.py` | Enhanced AI chat | Ollama (11434) |
| **8001** | Mobile UI | `tools/mobile_web_interface_tool.py` | Mobile web interface | API (5000) |
| **5175** | Frontend UI | `frontend_server.py` | Alternative frontend | API (5000) |

**Critical Dependencies**:
```
Ollama (11434) ◄─── API Server (5000) ◄─── Web GUI (8080)
                          │
                          └──────────────► Voice System
                          │
                          └──────────────► Mobile UI (8001)
```

**Port Conflict Resolution**:
- `utils/port_manager.py` checks availability before startup
- `main.py` validates port 8080 before launching web_gui_server.py
- `run.bat` includes port health checks

---

## Startup Sequence

### Master Startup (`run.bat`)

```
┌─────────────────────────────────────────────────┐
│              run.bat Startup Flow                │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Check Python installation                   │
│     └─ python --version                         │
│                                                  │
│  2. Start Ollama service (background)           │
│     └─ ollama serve                             │
│     └─ Wait 3 seconds for startup               │
│                                                  │
│  3. Health Check: Ollama service                │
│     └─ curl http://localhost:11434/api/tags     │
│     └─ Retry 3 times if failed                  │
│                                                  │
│  4. Health Check: Model availability            │
│     └─ Verify llava:7b is loaded                │
│                                                  │
│  5. Health Check: Text generation               │
│     └─ Test /api/generate endpoint (15s timeout)│
│                                                  │
│  6. Health Check: Chat API                      │
│     └─ Test /api/chat endpoint (15s timeout)    │
│                                                  │
│  7. Health Check: Context retention             │
│     └─ Test multi-turn conversation memory      │
│                                                  │
│  8. Start API Server (background)               │
│     └─ python api_server.py                     │
│     └─ Wait 2 seconds for startup               │
│                                                  │
│  9. Start Web GUI Server (background)           │
│     └─ python web_gui_server.py                 │
│     └─ Wait 2 seconds for startup               │
│                                                  │
│  10. Open browser to http://localhost:8080      │
│      └─ GUI loads and connects to API           │
│                                                  │
│  11. Log all results to:                        │
│      └─ ultron_master_startup.log               │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Startup Logs**: `ultron_master_startup.log`

**Expected Output**:
```
[TEST] Ollama Service Availability... PASSED
[TEST] Model Availability (llava:7b)... PASSED
[TEST] Text Generation Test... PASSED
[TEST] Chat API Test... PASSED
[TEST] Context Retention Test... PASSED
[TEST] Summary: Passed=5 Failed=0

Starting API Server on port 5000...
Starting Web GUI on port 8080...
Opening browser...
```

---

### Development Startup (`main.py`)

**Minimal Agent Only** (no web services):

```
┌─────────────────────────────────────────────┐
│         main.py Startup Flow                │
├─────────────────────────────────────────────┤
│                                              │
│  1. Setup signal handlers (SIGINT, SIGTERM) │
│     └─ Graceful shutdown on Ctrl+C          │
│                                              │
│  2. Import agent_core                       │
│                                              │
│  3. Initialize UltronAgent                  │
│     ├─ Load ultron_config.json              │
│     ├─ Initialize event_system              │
│     ├─ Initialize brain.py                  │
│     ├─ Initialize voice.py                  │
│     └─ Discover tools from tools/           │
│                                              │
│  4. Start command loop                      │
│     └─ await agent.run_command(user_input)  │
│                                              │
└─────────────────────────────────────────────┘
```

**Usage**:
```bash
python main.py
```

**Logs**: `logs/agent_core.log`

---

## Configuration System

### Primary Configuration: `ultron_config.json`

**Location**: Project root
**Format**: JSON
**Purpose**: All system settings and service configurations

**Structure**:
```json
{
  "llm_model": "llava:7b",
  "ollama_base_url": "http://localhost:11434",

  "voice_enabled": true,
  "voice_engine": "elevenlabs",
  "stt_engine": "whisper",
  "tts_engine": "elevenlabs",
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY",

  "api_port": 5000,
  "gui_port": 8080,

  "log_level": "INFO",
  "cache_responses": true,

  "tools_directory": "tools/",
  "auto_discover_tools": true
}
```

### Environment Variable Pattern

**Secrets Management**: Use `USE_ENV_*` pattern for sensitive data

**Example**:
```json
{
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY",
  "openai_api_key": "USE_ENV_OPENAI_API_KEY"
}
```

**Set Environment Variables**:
```bash
# Windows (PowerShell)
$env:ELEVENLABS_APIKEY = "sk-..."
$env:OPENAI_API_KEY = "sk-..."

# Windows (Batch)
set ELEVENLABS_APIKEY=sk-...
set OPENAI_API_KEY=sk-...

# Linux/Mac
export ELEVENLABS_APIKEY=sk-...
export OPENAI_API_KEY=sk-...
```

### Configuration Loading

**Code Reference** (`agent_core.py`):
```python
import json

# Load configuration
with open('ultron_config.json', 'r') as f:
    config = json.load(f)

# Resolve environment variables
for key, value in config.items():
    if isinstance(value, str) and value.startswith('USE_ENV_'):
        env_var = value.replace('USE_ENV_', '')
        config[key] = os.environ.get(env_var)
```

---

## Service Connections

### API Server → Ollama Connection

**File**: `brain.py`
**Connection**:
```python
import aiohttp

async def query_ollama(prompt: str):
    async with aiohttp.ClientSession() as session:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llava:7b",
            "prompt": prompt,
            "stream": False
        }
        async with session.post(url, json=payload, timeout=30) as resp:
            result = await resp.json()
            return result['response']
```

**Health Check**:
```bash
curl http://localhost:11434/api/tags
```

---

### Web GUI → API Server Connection

**File**: `gui/ultron_enhanced/web/app.js`
**Connection**:
```javascript
async apiCall(endpoint, options = {}) {
    const url = `http://localhost:5000${endpoint}`;

    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    return await response.json();
}

// Example: Send command
async sendCommand(command) {
    return await this.apiCall('/command', {
        method: 'POST',
        body: JSON.stringify({ command })
    });
}

// Example: Toggle voice
async toggleVoiceChat() {
    const response = await this.apiCall('/api/voice/toggle', {
        method: 'POST',
        body: JSON.stringify({ enable: !this.voiceEnabled })
    });

    this.voiceEnabled = response.enabled;

    if (this.voiceEnabled) {
        this.startVoiceRecognition();
    } else {
        this.stopVoiceRecognition();
    }
}
```

---

### Voice System → ElevenLabs API Connection

**File**: `voice.py`
**Connection**:
```python
import requests
import os

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_APIKEY')
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

def speak_text(text: str) -> bytes:
    """Generate speech audio from text using ElevenLabs API"""
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        'text': text,
        'voice_id': 'default',
        'model_id': 'eleven_monolingual_v1'
    }

    response = requests.post(ELEVENLABS_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.content  # Audio blob
    else:
        # Fallback to pyttsx3
        return speak_with_pyttsx3(text)
```

**Fallback Chain**:
```
ElevenLabs API → pyttsx3 (local) → Console output
```

---

## Data Flow Diagrams

### Command Execution Flow

```
┌──────────────────────────────────────────────────────────┐
│            User Command Processing Flow                   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  User Input (GUI or Voice)                               │
│         │                                                 │
│         ▼                                                 │
│  ┌─────────────────┐                                     │
│  │   app.js        │                                     │
│  │  (Frontend)     │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ POST /command                                 │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │  api_server.py  │                                     │
│  │  (Port 5000)    │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ AGENT_INSTANCE.run_command()                  │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │  agent_core.py  │                                     │
│  │  (Coordinator)  │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ Match command to tool                         │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │  tool_loader    │                                     │
│  │  (Tools/)       │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ tool.execute(command)                         │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │   brain.py      │ ◄──────── Ollama (11434)            │
│  │  (AI Reasoning) │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ Response text                                 │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │  event_system   │                                     │
│  │  (Pub/Sub)      │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ emit('command_complete')                      │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │   voice.py      │ ◄──────── ElevenLabs API            │
│  │  (TTS)          │                                     │
│  └────────┬────────┘                                     │
│           │                                               │
│           │ Audio blob                                    │
│           ▼                                               │
│  ┌─────────────────┐                                     │
│  │   app.js        │                                     │
│  │  Play audio     │                                     │
│  └─────────────────┘                                     │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## Environment Variables

### Required Variables

| Variable | Purpose | Example | Used By |
|----------|---------|---------|---------|
| `ELEVENLABS_APIKEY` | ElevenLabs TTS/STT | `sk-...` | `voice.py` |

### Optional Variables

| Variable | Purpose | Default | Used By |
|----------|---------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API fallback | None | `tools/openai_tools.py` |
| `ULTRON_TEST_MODE` | Enable test mode | `0` | `conftest.py` (pytest) |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `utils/ultron_logger.py` |

### Setting Variables

**PowerShell**:
```powershell
$env:ELEVENLABS_APIKEY = "sk-your-key-here"
$env:OPENAI_API_KEY = "sk-your-openai-key"
```

**Batch**:
```batch
set ELEVENLABS_APIKEY=sk-your-key-here
set OPENAI_API_KEY=sk-your-openai-key
```

**Linux/Mac**:
```bash
export ELEVENLABS_APIKEY=sk-your-key-here
export OPENAI_API_KEY=sk-your-openai-key
```

**Persistent (Windows)**:
```powershell
[System.Environment]::SetEnvironmentVariable('ELEVENLABS_APIKEY', 'sk-your-key', 'User')
```

---

## Troubleshooting

### Service Won't Start

**Check Port Availability**:
```powershell
# Check if port is in use
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue

# Kill process using port
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

**Check Ollama Connection**:
```powershell
curl http://localhost:11434/api/tags
```

**Check Logs**:
```powershell
# Master startup log
Get-Content ultron_master_startup.log -Tail 50

# Agent core log
Get-Content logs/agent_core.log -Tail 50

# Brain log
Get-Content logs/brain.log -Tail 50
```

---

### Voice Not Working

**See**: `VOICE_MICROPHONE_DOCUMENTATION.md` for comprehensive voice troubleshooting

**Quick Checks**:
1. Verify ElevenLabs API key set: `echo $env:ELEVENLABS_APIKEY`
2. Check browser microphone permissions
3. Verify voice toggle endpoint: `curl http://localhost:5000/api/voice/status`
4. Check voice.py logs: `logs/voice.log`

---

### Configuration Not Loading

**Verify JSON Syntax**:
```powershell
python -c "import json; json.load(open('ultron_config.json'))"
```

**Check Environment Variables**:
```powershell
# List all ULTRON-related env vars
Get-ChildItem Env: | Where-Object { $_.Name -like '*ULTRON*' -or $_.Name -like '*ELEVENLABS*' }
```

---

## Related Documentation

- **Voice System**: `VOICE_MICROPHONE_DOCUMENTATION.md`
- **Recent Fixes**: `FIXES_SUMMARY_2025-10-24.md`
- **Developer Guide**: `.github/copilot-instructions.md`
- **Testing**: `pytest.ini`, `conftest.py`
- **Startup Logs**: `ultron_master_startup.log`

---

**End of System Architecture Guide**
