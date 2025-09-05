# ULTRON Agent 3.0

**A powerful, voice-first AI assistant framework with multi-model support and extensive automation capabilities.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0+-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 Overview

ULTRON Agent is an advanced, modular AI assistant framework that combines multiple AI services, voice interaction, computer vision, and extensive tool integration. Built with Python and FastAPI, it supports both local (Ollama) and cloud-based (OpenAI, Anthropic, NVIDIA) language models, providing a flexible and powerful platform for AI-driven automation.

### ✨ Key Features

- 🤖 **Multi-Model Support**: Ollama, OpenAI, Anthropic, NVIDIA NIM, and more
- 🎤 **Voice Integration**: Advanced speech-to-text and text-to-speech with multiple engines
- 👁️ **Computer Vision**: Screen capture, OCR, and intelligent image processing
- 🔧 **Extensible Tools**: Modular plugin system for unlimited functionality
- 🖥️ **Multiple Interfaces**: Modern GUI, CLI, and RESTful API endpoints
- 📱 **Cross-Platform**: Full support for Windows, macOS, and Linux
- 🔒 **Enterprise Security**: Encrypted API key storage and comprehensive validation
- 📊 **Performance Monitoring**: Built-in metrics, logging, and diagnostics
- ⚡ **Async Architecture**: High-performance non-blocking operations

## 🛠 Installation

### Prerequisites

- **Python 3.10 or higher**
- **Node.js 16+ and npm** (for web interface)
- **Git** for cloning the repository

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent
```

2. **Install Python Dependencies**
```bash
# Using pip
pip install -e .

# Or with development dependencies
pip install -e ".[dev,gui,ml]"

# Using poetry (recommended)
poetry install --extras "dev gui ml"
```

3. **Configure Environment**
```bash
# Copy example configuration
cp ultron_config.json.example ultron_config.json
cp .env.example .env

# Edit configuration files with your API keys and preferences
```

4. **Run ULTRON Agent**
```bash
# Start with GUI
python main.py

# Or use the CLI
ultron --help

# Or run as a service
python -m uvicorn agent_core:app --host 0.0.0.0 --port 8000
```

### Docker Installation

```bash
# Build and run with Docker
docker build -t ultron-agent .
docker run -p 8000:8000 -v $(pwd)/config:/app/config ultron-agent
```

## 🎯 Usage

### Basic Commands

```bash
# Voice interaction mode
ultron --voice

# Process a single command
ultron "What's the weather like today?"

# Start web interface
ultron --web --port 8000

# Run specific tool
ultron --tool web_search --query "Python tutorials"
```

### GUI Interface

ULTRON Agent features multiple GUI options:

1. **Modern Pokédex-style Interface** (Recommended)
```bash
python pokedex_ultron_gui.py
```

2. **Web-based Interface**
```bash
python web_gui_server.py
# Open http://localhost:8000 in your browser
```

3. **Desktop GUI**
```bash
python gui_ultimate.py
```

### API Usage

```python
import requests

# Send a query to ULTRON
response = requests.post("http://localhost:8000/query", 
    json={"message": "Hello ULTRON, what can you do?"})
print(response.json())

# Get system status
status = requests.get("http://localhost:8000/status")
print(status.json())
```

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ULTRON Agent 3.0                        │
├─────────────────────────────────────────────────────────────┤
│  User Interfaces                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Pokédex │  │   CLI   │  │   API   │  │  Voice  │      │
│  │   GUI   │  │         │  │  REST   │  │   I/O   │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Core Agent (agent_core.py)                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Event System │ Performance Monitor │ Task Scheduler│   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Brain Module (brain.py)                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Query Logic │  │   Caching   │  │ Tool Router │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
├─────────────────────────────────────────────────────────────┤
│  AI Services & Models                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Ollama  │ │ OpenAI  │ │ Anthropic│ │  NVIDIA │        │
│  │ Local   │ │   API   │ │   API   │ │   NIM   │        │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Tools & Extensions                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │Web Search│ │File Ops │ │ Voice   │ │ Vision  │        │
│  │Wikipedia │ │System   │ │Text-to- │ │OCR &    │        │
│  │& APIs   │ │Commands │ │Speech   │ │Screen   │        │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

- **`agent_core.py`**: Main integration hub and FastAPI server
- **`brain.py`**: AI reasoning and tool orchestration
- **`voice_manager.py`**: Multi-engine voice processing
- **`config.py`**: Configuration management
- **`tools/`**: Modular plugin system
- **`utils/`**: Event system, monitoring, and utilities

## 🔧 Configuration

ULTRON Agent uses JSON configuration files and environment variables:

### ultron_config.json
```json
{
    "models": {
        "ollama": {
            "enabled": true,
            "host": "http://localhost:11434",
            "model": "llama3.2:latest"
        },
        "openai": {
            "enabled": true,
            "model": "gpt-4o"
        }
    },
    "voice": {
        "enabled": true,
        "engine": "enhanced",
        "fallback_chain": ["pyttsx3", "openai", "console"]
    },
    "gui": {
        "theme": "dark",
        "accessibility_mode": true
    }
}
```

### Environment Variables
```bash
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
NVIDIA_API_KEY=your_nvidia_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Optional settings
ULTRON_LOG_LEVEL=INFO
ULTRON_GUI_MODE=pokedex
```

## 🧰 Available Tools

ULTRON Agent features a comprehensive plugin system with built-in tools:

- **🌐 Web Tools**: Search, scraping, API integrations
- **📁 File Operations**: Reading, writing, organization
- **💻 System Commands**: Cross-platform automation
- **🎤 Voice Processing**: Multiple TTS/STT engines
- **👁️ Computer Vision**: OCR, screenshot analysis
- **📊 Data Processing**: JSON, CSV, XML handling
- **🔍 Research Tools**: Wikipedia, academic databases
- **🔧 Development**: Code analysis, documentation

### Creating Custom Tools

```python
# tools/my_tool.py
from typing import Dict, Any

class MyTool:
    @staticmethod
    def match(user_input: str) -> bool:
        return "my command" in user_input.lower()
    
    @staticmethod
    def execute(**kwargs) -> Dict[str, Any]:
        return {"result": "Tool executed successfully"}
    
    @staticmethod
    def schema() -> Dict[str, Any]:
        return {
            "name": "my_tool",
            "description": "Description of what the tool does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter description"}
                }
            }
        }
```

## 🧪 Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=ultron_agent --cov-report=html

# Run specific test
pytest tests/test_agent_core.py -v
```

### Code Quality

```bash
# Format code
black .
ruff check . --fix

# Type checking
mypy .

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Debugging

ULTRON Agent provides comprehensive logging:

```bash
# Check logs
tail -f logs/ultron.log
tail -f logs/error.log

# Debug mode
python main.py --debug --log-level DEBUG
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](Contributing.md) for details on:

- Development setup and workflow
- Coding standards and style guide
- Testing requirements
- Pull request process
- Code of conduct

## 📚 Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Usage Guide](USAGE.md) - Comprehensive usage examples
- [API Reference](docs/API.md) - Complete API documentation
- [Architecture Overview](docs/project_overview.md) - Technical details
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -e ".[dev]"`
2. **API Key Issues**: Verify your `.env` file contains valid API keys
3. **Voice Problems**: Check audio permissions and microphone access
4. **GUI Not Loading**: Try different GUI modes or check display settings

For more detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Voice powered by [ElevenLabs](https://elevenlabs.io/) and pyttsx3
- AI models from [Ollama](https://ollama.ai/), [OpenAI](https://openai.com/), and [Anthropic](https://anthropic.com/)
- Special thanks to all contributors and the open-source community

## 🔗 Links

- **Repository**: [github.com/dqikfox/ultron_agent](https://github.com/dqikfox/ultron_agent)
- **Issues**: [Report bugs or request features](https://github.com/dqikfox/ultron_agent/issues)
- **Discussions**: [Community discussions](https://github.com/dqikfox/ultron_agent/discussions)

---

**Made with ❤️ for accessibility and automation**


