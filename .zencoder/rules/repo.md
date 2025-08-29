---
description: Repository Information Overview
alwaysApply: true
---

# Ultron Agent 2 Information

## Summary
Ultron Agent 2 is a local voice-first AI assistant with multi-model support. It features a Python backend with web and GUI interfaces, designed for AI-enhanced development workflows. The project integrates multiple AI tools and provides a comprehensive development environment with NVIDIA enhanced AI capabilities and a Pokédex-style GUI.

## Structure
- **Root**: Main Python modules, configuration files, and documentation
- **.vscode/**: VS Code workspace settings optimized for AI development
- **assistant/**: AI Assistant Web Application (React/TypeScript)
- **gui/ultron_enhanced/web/**: Pokédex-style GUI interface (HTML/CSS/JS)
- **logs/**: Log files for various services
- **core/**: Electron-based Command Center GUI
- **tests/**: Test files for various components (pytest)

## Architecture
**Server Components**:
- NVIDIA Enhanced AI Chat Server (port 8000)
- Web GUI Server (port 8080)
- API Server (port 5000)
- Command Center GUI (Electron application)

## Issues Identified
- Multiple redundant files with "_fixed" suffix
- Empty directories ("New folder")
- Excessive number of markdown documentation files
- Multiple similar launch scripts (run*.bat)
- Untitled Python files and empty files
- VS Code settings hiding most project folders

## Language & Runtime
**Language**: Python
**Version**: Python 3.10-3.12
**Build System**: setuptools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- fastapi (0.104.1)
- uvicorn (0.24.0)
- openai (1.3.7)
- pydantic (2.5.x)
- websockets (12.0)
- python-socketio (5.10.0)
- pyttsx3 (2.90.x)
- SpeechRecognition (3.10.x)
- PyAudio (0.2.11)
- elevenlabs (1.0.x)
- Pillow (10.0.x)
- opencv-python (4.8.x)

**Optional Dependencies**:
- google-api-python-client, google-auth (for Google Drive integration)
- google-auth-oauthlib (for interactive OAuth flow)

**Development Dependencies**:
- pytest (7.4.x)
- pytest-asyncio (0.21.x)
- black (23.0.x)
- ruff (0.1.x)
- mypy (1.7.x)

**JavaScript Dependencies**:
- React/TypeScript web assistant (in assistant/ai-assistant)

## Build & Installation
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

# Web assistant setup
npm run setup
npm run dev
```

## Launch & Operation
**Run Script (run.bat)**:
```bash
# Start NVIDIA Enhanced AI Chat Server
python nvidia_enhanced_ultron.py

# Start Web GUI Server
python web_gui_server.py

# Start API Server
python api_server.py

# Launch Command Center GUI (if available)
# Or fallback to web interface: http://localhost:8000
```

## Data Storage
**Memory System**:
- Short-term memory (in-memory deque)
- Long-term memory (JSON file with optional Google Drive sync)
- Memory search capabilities
- Google Drive integration for persistent storage

## Testing
**Framework**: pytest
**Test Location**: Root directory and tests/
**Naming Convention**: test_*.py
**Configuration**: pytest.ini
**Run Command**:
```bash
pytest
pytest -m unit  # Run unit tests only
pytest -m integration  # Run integration tests only
pytest -m gui  # Run GUI tests only
```

## Main Entry Points
**Main Application**: main.py
**NVIDIA AI Server**: nvidia_enhanced_ultron.py
**Web GUI Server**: web_gui_server.py
**API Server**: api_server.py
**Agent Core**: agent_core.py
**Memory System**: memory.py

## GUI Interfaces
- **Pokédex-style GUI**: gui/ultron_enhanced/web/index.html
- **Command Center**: core/ultron-agent-command-center/release/win-unpacked/Ultron Agent Command Center.exe
- **Web Interface**: http://localhost:8000

## Improvements Made
- Updated empty config.py with proper implementation
- Removed empty "New folder" directory
- Removed Untitled Python files
- Removed empty and unnecessary files
- Modified VS Code settings to show project folders

## Features
- 🤖 Multiple AI personalities (General, Creative, Technical, Productivity, Research)
- 💬 Real-time chat interface with conversation history
- 📁 File processing (PDF, DOC, images) with AI analysis
- 🔍 Web search integration with AI insights
- 📝 Productivity suite (notes, tasks, reminders)
- 🎨 Modern responsive UI with dark/light themes
- 💾 Persistent memory with Google Drive integration
- 🧠 NVIDIA enhanced AI capabilities