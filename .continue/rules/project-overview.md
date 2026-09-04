it loads qwen3-coder:480b-cloud# Ultron Agent Project Overview

This is the Ultron Agent project - an advanced AI-powered automation system with multiple components:

## Core Architecture

- **Agent Core** (`agent_core.py`, `agent_core_enhanced.py`) - Main agent orchestration
- **AI Brain** (`brain.py`, `brain_fixed.py`) - AI reasoning and decision making
- **Memory System** (`memory.py`) - Long-term and short-term memory management
- **Voice Integration** (`voice.py`, `voice_enhanced.py`, `voice_manager.py`) - Speech recognition and synthesis
- **Vision System** (`vision.py`) - Computer vision and OCR capabilities
- **Tool System** (`tools/`) - Modular tool plugins for various functionalities

## Key Components

### AI Integration
- Multiple AI providers: OpenAI, NVIDIA NIM, Ollama, DeepSeek
- Local and cloud-based model support
- Smart model routing based on task requirements

### User Interfaces
- **Web GUI** (`web_gui/`) - Browser-based interface
- **Desktop GUI** (`gui_*.py`) - Tkinter-based desktop application
- **Mobile Interface** (`ultron_assistant/`) - Mobile-friendly web interface
- **Command Line** - CLI interface for automation

### Automation & Tools
- File management and organization
- System control and monitoring
- Web scraping and automation
- Database operations
- Performance monitoring
- Security features

### Configuration
- `ultron_config.json` - Main configuration file
- Environment-specific configs for different deployment scenarios
- Secure API key management

## Development Guidelines

- Python-based architecture with modular design
- Async/await patterns for concurrent operations
- Comprehensive error handling and logging
- Security-first approach with input validation
- Extensive testing framework

When working on this project:
1. Follow the existing modular architecture
2. Maintain compatibility with multiple AI providers
3. Ensure proper error handling and logging
4. Test both GUI and CLI interfaces
5. Consider accessibility features
6. Document API changes and new features
