# Ultron Agent 2

## Overview

Ultron Agent 2 is a local voice-first AI assistant with multi-model support. It features a Python backend with web and GUI interfaces, designed for AI-enhanced development workflows. The project integrates multiple AI tools and provides a comprehensive development environment with NVIDIA enhanced AI capabilities and a Pokédex-style GUI.

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
- **Executable**: `core/ultron-agent-command-center/release/win-unpacked/Ultron Agent Command Center.exe`

### Web Interface

- **URL**: http://localhost:8000
- **Alternative**: http://localhost:8080

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

```
ultron_agent_2/
 .vscode/            # VS Code workspace settings
 assistant/          # AI Assistant Web Application (React/TypeScript)
 core/               # Electron-based Command Center GUI
 gui/                # GUI interfaces including Pokédex-style UI
 logs/               # Log files for various services
 tests/              # Test files for various components (pytest)
 docs/               # Documentation files
 config.py           # Configuration management
 memory.py           # Memory system with Google Drive integration
 nvidia_enhanced_ultron.py  # NVIDIA AI server
 web_gui_server.py   # Web GUI server
 api_server.py       # API server
 run_unified.bat     # Unified launcher script
```

## 🔧 Troubleshooting

### Common Issues

1. **Servers not starting**: Check logs in the `logs/` directory
2. **GUI not showing**: Verify the correct ports are being used (8000, 8080, 5000)
3. **Voice recognition issues**: Check microphone permissions and settings
4. **Performance issues**: Adjust memory settings in configuration

### Log Files

Log files are stored in the `logs/` directory:
- `nvidia_chat.log` - NVIDIA AI server logs
- `web_gui_server.log` - Web GUI server logs
- `api_server.log` - API server logs

## 📚 Documentation

- **PROJECT_STATUS.md** - Current project status and issues
- **API.md** - API documentation
- **DEVELOPMENT.md** - Development workflow

---
**Ultron Agent 2 - Your AI-powered development assistant**

