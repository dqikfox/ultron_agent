# Ultron Agent 2

## Overview

Ultron Agent 2 is a local voice-first AI assistant with multi-model support. It features a Python backend with web and GUI interfaces, designed for AI-enhanced development workflows. The project integrates multiple AI tools and provides a comprehensive development environment with NVIDIA enhanced AI capabilities and a Pokédex-style GUI.

**Latest Version**: 3.0.0
**Last Updated**: September 4, 2025

## 🚀 Quick Start

### Running the Application

The easiest way to run Ultron Agent 2 is using the unified launcher:

```bash
# Launch the unified menu
run_unified.bat
```

This will present a menu with the following options:

1. Full System (NVIDIA AI + Web GUI + API Server + Command Center)
2. NVIDIA Enhanced AI Only
3. Web GUI Only
4. Pokédex GUI
5. Development Mode (with debug logging)
6. Clean Logs
7. Exit

### Installation

```bash
# Python environment setup
python -m venv .venv
.venv\Scripts\activate
pip install -e .

# For development
pip install -e ".[dev]"

# For GUI features
pip install -e ".[gui]"

# For ML features
pip install -e ".[ml]"
```

## 🏗️ Architecture

Ultron Agent 2 consists of several server components:

- **NVIDIA Enhanced AI Chat Server** (port 8000)
- **Web GUI Server** (port 8080)
- **API Server** (port 5000)
- **Command Center GUI** (Electron application)

## 🧠 Features

- **Multiple AI Personalities**: General, Creative, Technical, Productivity, Research
- **Real-time Chat Interface**: Conversation history with context management
- **File Processing**: PDF, DOC, images with AI analysis
- **Web Search Integration**: AI-enhanced web search capabilities
- **Voice Recognition**: Speech-to-text and text-to-speech
- **Modern UI**: Responsive design with dark/light themes
- **Memory System**: Short-term and long-term memory with Google Drive integration
- **NVIDIA Enhanced AI**: Advanced AI capabilities powered by NVIDIA models
- **System Monitoring**: Real-time system health and performance tracking
- **Configuration Validation**: Automated config file validation and error reporting
- **Robust Error Handling**: Centralized error logging and recovery mechanisms
- **Extensible Tools Framework**: Modular tool system for custom functionality

## 🖥️ GUI Interfaces

### Pokédex-style GUI

The project includes a fully functional Pokédex-style GUI interface:

- **Location**: `gui/ultron_enhanced/web/`
- **Main File**: `file:///C:/Projects/ultron_agent_2/gui/ultron_enhanced/web/index.html`
- **Technology**: HTML5 + CSS3 + JavaScript
- **Features**: Console, System Monitor, Vision, Tasks, Files, Settings, Profile

### Command Center

An Electron-based GUI application:

- **Location**: `core/ultron-agent-command-center/`
- **Technology**: Electron + Web Technologies
- **Features**: Desktop application with native capabilities

### Web Interface

- **URL**: <http://localhost:8000>
- **Alternative**: <http://localhost:8080>
- **Technology**: Flask + HTML/CSS/JS

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only
pytest -m gui          # GUI tests only
```

## 🛠️ Development

### VS Code Integration

This project is configured with advanced AI development tools and extensions:

- **Amazon Q (CodeWhisperer)** - AWS AI coding assistant
- **GitHub Copilot** - GitHub's AI pair programmer
- **Sixth AI** - Advanced inline completions

To launch VS Code with AI extensions:

```powershell
code --enable-proposed-api sixth.sixth-ai "C:\Projects\ultron_agent_2"
```

### Development Settings

- **Python**: Strict type checking, Black formatting
- **Editor**: Format on save, trim whitespace
- **Terminal**: PowerShell default

## 📁 Project Structure

```text
ultron_agent_2/
├── .vscode/                    # VS Code workspace settings
├── .github/                    # GitHub workflows and templates
├── assistant/                  # AI Assistant Web Application (React/TypeScript)
├── core/                       # Electron-based Command Center GUI
├── gui/                        # GUI interfaces including Pokédex-style UI
├── logs/                       # Log files for various services
├── tests/                      # Test files for various components (pytest)
├── docs/                       # Documentation files
├── tools/                      # Extensible tools framework
│   ├── base.py                # Base tool class
│   ├── system_tools.py        # System utilities
│   ├── system_monitor_tool.py # Real-time monitoring
│   └── ...                    # Additional tools
├── config.py                   # Configuration management
├── config_validator.py         # Configuration validation
├── robust_error_handler.py     # Centralized error handling
├── error_handler.py            # Basic error logging
├── ultron_config.json          # Main configuration file
├── agent_core.py               # Main agent orchestration
├── api_server.py              # REST API server
├── brain.py                    # AI reasoning and model management
├── memory.py                   # Memory system with Google Drive integration
├── voice.py                    # Voice input/output handling
├── vision.py                   # Screen capture and OCR
├── nvidia_enhanced_ultron.py   # NVIDIA AI server
├── web_gui_server.py          # Web GUI server
├── run_unified.bat             # Unified launcher script
└── README.md                   # This file
```

## 🔧 Configuration

### Main Configuration File

The `ultron_config.json` file contains all major settings:

```json
{
  "use_voice": true,
  "use_vision": true,
  "use_api": true,
  "use_gui": true,
  "voice_engine": "elevenlabs",
  "stt_engine": "whisper",
  "tts_engine": "elevenlabs",
  "openai_api_key": null,
  "ollama_api_key": null,
  "elevenlabs_api_key": "YOUR_ELEVENLABS_API_KEY_HERE",
  "supabase_url": "https://jdkddrfloluhkytxdkkh.supabase.co",
  "supabase_anon_key": "...",
  "gemini_api_key": null,
  "jwt_secret": null,
  "llm_model": "llama3.2:latest",
  "ollama_base_url": "http://localhost:11434",
  "voice_boot_message": "There's No Strings On Me",
  "elevenlabs_agent_id": "YOUR_VOICE_ID_HERE"
}
```

### Configuration Validation

The system includes automated configuration validation:

```python
from config_validator import ConfigValidator

validator = ConfigValidator("ultron_config.json")
if validator.load_config():
    if validator.validate():
        print("Configuration is valid")
    else:
        print("Configuration errors:", validator.get_errors())
```

## 🔧 Troubleshooting

### Common Issues

1. **Servers not starting**: Check logs in the `logs/` directory
2. **GUI not showing**: Verify the correct ports are being used (8000, 8080, 5000)
3. **Voice recognition issues**: Check microphone permissions and settings
4. **Performance issues**: Adjust memory settings in configuration
5. **Configuration errors**: Run config validation to check for missing keys

### Log Files

Log files are stored in the `logs/` directory:

- `nvidia_chat.log` - NVIDIA AI server logs
- `web_gui_server.log` - Web GUI server logs
- `api_server.log` - API server logs
- `error.log` - General error logs

## 📚 Documentation

- **PROJECT_STATUS.md** - Current project status and issues
- **API.md** - API documentation
- **DEVELOPMENT.md** - Development workflow
- **docs/UPDATE_NOTES.md** - Recent updates and changes
- **ARCHITECTURE_DESIGN.md** - System architecture details

## 🆕 Recent Updates

### Version 3.0.0 (September 2025)

- ✅ Added configuration validation system
- ✅ Implemented robust error handling framework
- ✅ Enhanced system monitoring capabilities
- ✅ Improved file structure and organization
- ✅ Updated documentation and README
- ✅ Fixed merge conflicts and repository issues

### Upcoming Features

- 🔄 Multi-modal AI integration
- 🔄 Enhanced voice processing
- 🔄 Advanced GUI components
- 🔄 Plugin system for extensibility

---

## About

Ultron Agent 2 - Your AI-powered development assistant



## Integration Quick Start (SDK and Service)

This repository now provides a minimal, stable integration surface you can use from other apps, either in-process (Python SDK) or via a small HTTP service.

- Python SDK (in-process):
  - Works without running a separate server.
  - Uses the built-in UltronAgent from this repo under the hood.

Example:

```python
from ultron_integration.client import UltronAgent2Client

# Local in‑process mode
client = UltronAgent2Client()          # optionally pass config_path="ultron_config.json"
client.start()
reply = client.send_message("hello")
print(reply)

# Remote HTTP mode (if a service is running)
client = UltronAgent2Client(base_url="http://127.0.0.1:8080")
reply = client.send_message("hello")
print(reply)
```

- HTTP Service (FastAPI):
  - Start a tiny service that exposes two endpoints:
    - GET /status -> {"status":"ok"}
    - POST /chat  -> {"reply":"..."}
  - Requires: fastapi, uvicorn, pydantic

Commands (Windows PowerShell):

```powershell
# (Optional) Install service dependencies if not already available
pip install fastapi uvicorn pydantic

# Start the service
python scripts\start_ultron_service.py

# Smoke check using the client over HTTP
$env:ULTRON_AGENT2_URL = "http://127.0.0.1:8080"
python scripts\integration_check.py

# Or run locally without HTTP
Remove-Item Env:\ULTRON_AGENT2_URL
python scripts\integration_check.py
```

- Run only the new integration tests:

```powershell
pytest -q tests\test_ultron_integration_client.py
```

Notes:
- In local mode, the client initializes UltronAgent and calls process_command under the hood.
- If tools are missing or optional integrations aren’t configured, you may see warnings in logs; the basic reply still works.
- In remote mode, the client posts to /chat; for streaming, it returns an iterator of chunks when supported.
