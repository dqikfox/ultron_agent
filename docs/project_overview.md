# Ultron Agent 2.0 - Comprehensive Project Overview

## Table of Contents
1. [Project Description](#project-description)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Configuration System](#configuration-system)
5. [Tools & Extensions](#tools--extensions)
6. [Installation & Usage](#installation--usage)
7. [API Reference](#api-reference)
8. [Development Guidelines](#development-guidelines)
9. [Troubleshooting](#troubleshooting)

## 📚 Additional Documentation
- **[Major Components & Features](major_components_and_features.md)** - Comprehensive guide to agent-based workflow engine, built-in tools, sandboxed code interpreter, memory strategies, serialization/resume capabilities, instrumentation, caching, OpenAI-compatible API, and chat UI

## Project Description

**Ultron Agent 2.0** is an advanced, modular AI assistant framework that combines multiple AI services, voice interaction, computer vision, and extensive tool integration. Built with Python, it supports both local (Ollama) and cloud-based (OpenAI, Anthropic) language models, providing a flexible and powerful platform for AI-driven automation and interaction.

### Key Features
- 🤖 **Multi-Model Support**: Ollama, OpenAI, Anthropic, Gemini
- 🎤 **Voice Integration**: Speech-to-text and text-to-speech capabilities
- 👁️ **Computer Vision**: Screen capture, OCR, and image processing
- 🔧 **Extensible Tools**: Modular tool system for various tasks
- 🖥️ **Multiple Interfaces**: GUI, CLI, and API endpoints
- 📱 **Cross-Platform**: Windows, macOS, and Linux support
- 🔒 **Security**: Encrypted API key storage and validation
- 📊 **Performance Monitoring**: Built-in metrics and logging
- ⚡ **Async Architecture**: Non-blocking operations and real-time updates

### 🌟 Advanced Capabilities
- **Agent-Based Workflow Engine**: Event-driven task orchestration with intelligent planning and execution
- **Sandboxed Code Interpreter**: Secure Python code execution with comprehensive safety measures
- **Dual-Layer Memory System**: Short-term context management and long-term knowledge retention
- **Comprehensive Caching**: Multi-level caching for performance optimization and cost reduction
- **OpenAI-Compatible API**: Standard-compliant REST and WebSocket endpoints with function calling
- **Real-Time Instrumentation**: Performance monitoring, health checks, and automated alerting
- **State Persistence**: Serialization and resume capabilities for seamless operation continuity
- **Multi-Modal Interfaces**: Voice, vision, GUI, CLI, and web-based interaction options

> 📖 **For detailed information about these features, see [Major Components & Features](major_components_and_features.md)**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Ultron Agent 2.0                        │
├─────────────────────────────────────────────────────────────┤
│  User Interfaces                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │   GUI   │  │   CLI   │  │   API   │  │  Voice  │      │
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
│  LLM Services                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Ollama  │  │ OpenAI  │  │Anthropic│  │ Gemini  │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Support Systems                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │  Memory │  │  Voice  │  │ Vision  │  │ Config  │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Tool Ecosystem                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ File Tools │ System Tools │ Web Tools │ AI Tools    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### Agent Core (`agent_core.py`)
**Primary orchestrator** that manages all subsystems and provides the main entry point.

**Key Responsibilities:**
- System initialization and dependency management
- Event handling and inter-component communication
- Performance monitoring and health checks
- Task scheduling and automated maintenance
- Tool loading and management
- User interface coordination

**Key Features:**
- Automatic Ollama service detection and startup
- Duplicate initialization prevention
- Comprehensive error handling and recovery
- Built-in diagnostic and maintenance tasks
- Thread-safe operations

### Brain Module (`brain.py`)
**Intelligence layer** that handles reasoning, planning, and execution coordination.

**Key Responsibilities:**
- LLM query orchestration with fallback mechanisms
- Response caching for performance optimization
- Tool selection and parameter parsing
- Context management and conversation flow
- Multi-model support with intelligent routing

**Enhanced Features:**
- Async/await pattern for non-blocking operations
- Robust error handling with detailed logging
- Streaming response processing for better UX
- Intelligent tool matching and execution
- Context-aware response generation

### Configuration System (`config.py`)
**Enhanced configuration manager** with validation, security, and environment support.

**Key Features:**
- JSON schema validation with detailed error reporting
- Environment variable integration with security checks
- Default value management and auto-correction
- Sensitive data masking for logging and debugging
- Configuration backup and recovery
- Real-time configuration updates

### Memory System (`memory.py`)
**Dual-layer memory architecture** for short-term and long-term information storage.

**Components:**
- **Short-term Memory**: Recent conversation context and session data
- **Long-term Memory**: FAISS-based vector storage for persistent knowledge
- **Memory Management**: Automatic cleanup and optimization

### Voice System (`voice.py`)
**Multi-engine voice processing** with text-to-speech and speech-to-text capabilities.

**Supported Engines:**
- **TTS**: pyttsx3 (local), ElevenLabs (cloud), OpenAI TTS
- **STT**: Whisper (local/cloud), SpeechRecognition library
- **Features**: Voice cloning, emotion synthesis, multi-language support

### Vision System (`vision.py`)
**Computer vision capabilities** for screen interaction and image processing.

**Features:**
- Screen capture and region selection
- OCR text extraction using Tesseract
- Image analysis and description
- Visual UI automation support

## Configuration System

### Configuration Structure
```json
{
  "use_voice": true,
  "use_vision": true,
  "use_api": true,
  "use_gui": true,
  "use_pochi": false,
  "llm_model": "llama3.2:latest",
  "ollama_base_url": "http://localhost:11434",
  "voice_engine": "pyttsx3",
  "stt_engine": "whisper",
  "tts_engine": "pyttsx3",
  "log_level": "INFO",
  "cache_enabled": true,
  "max_cache_size": 1000,
  "session_timeout": 3600
}
```

### Environment Variables
Sensitive configuration can be provided via environment variables:
```bash
OPENAI_API_KEY=your_openai_key
OLLAMA_BASE_URL=http://localhost:11434
ELEVENLABS_API_KEY=your_elevenlabs_key
GEMINI_API_KEY=your_gemini_key
LOG_LEVEL=DEBUG
```

## Tools & Extensions

### Tool Architecture
All tools inherit from the base `Tool` class and implement:
- `match(user_input)`: Pattern matching for automatic tool selection
- `execute(**params)`: Main tool functionality
- `schema()`: JSON schema for API integration

### Available Tools

#### Core Tools
- **File Tool** (`file_tool.py`): File system operations (read, write, list, search)
- **System Tool** (`system_tool.py`): System control (processes, applications, shutdown)
- **Web Search Tool** (`web_search_tool.py`): Internet search via DuckDuckGo
- **Screen Reader Tool** (`screen_reader_tool.py`): Screen capture and OCR

#### AI-Powered Tools
- **Code Execution Tool** (`code_execution_tool.py`): Safe Python code execution
- **Image Generation Tool** (`image_generation_tool.py`): AI image creation
- **Database Tool** (`database_tool.py`): Supabase database operations

#### Integration Tools
- **OpenAI Tools** (`openai_tools.py`): Advanced OpenAI API integration
- **Agent Network** (`agent_network.py`): Multi-agent coordination
- **POCHI Tool** (`pochi_tool.py`): External AI assistant integration

### Creating Custom Tools
```python
from tools.base import Tool

class CustomTool(Tool):
    def __init__(self):
        self.name = "custom_tool"
        self.description = "Performs custom operations"
        self.parameters = {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "Input text"}
            },
            "required": ["input"]
        }
    
    def match(self, user_input: str) -> bool:
        return "custom" in user_input.lower()
    
    def execute(self, **kwargs) -> str:
        # Implementation here
        return "Custom tool executed successfully"
```

## Installation & Usage

### Prerequisites
- Python 3.8+
- Node.js 16+ (for web UI features)
- Ollama (for local LLM support)

### Quick Start
1. **Clone and Install**:
   ```bash
   git clone https://github.com/dqikfox/ultron_agent.git
   cd ultron_agent_2
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Agent**:
   ```bash
   python agent_core.py  # GUI mode (default)
   python main.py        # CLI mode
   ```

### Configuration Options
- **GUI Mode**: Full graphical interface with real-time updates
- **CLI Mode**: Command-line interface for server environments
- **API Mode**: RESTful API endpoints for integration
- **Voice Mode**: Hands-free voice interaction

## API Reference

### REST Endpoints
- `GET /status` - System health and status information
- `POST /command` - Execute commands and get responses
- `GET /settings` - Retrieve current configuration
- `PUT /settings` - Update configuration parameters
- `GET /tools` - List available tools and their schemas

### WebSocket Events
- `command` - Real-time command execution
- `status` - System status updates
- `progress` - Command execution progress
- `error` - Error notifications

## Development Guidelines

### Code Standards
- **Type Hints**: Use comprehensive type annotations
- **Error Handling**: Implement robust exception handling
- **Logging**: Use structured logging with appropriate levels
- **Testing**: Write unit tests for all new functionality
- **Documentation**: Maintain comprehensive docstrings

### Performance Considerations
- **Async Operations**: Use async/await for I/O operations
- **Caching**: Implement intelligent caching strategies
- **Resource Management**: Proper cleanup of resources
- **Memory Optimization**: Monitor and optimize memory usage

### Security Best Practices
- **API Key Security**: Use environment variables or encrypted storage
- **Input Validation**: Validate all user inputs and parameters
- **Permission Checks**: Implement proper access controls
- **Audit Logging**: Log security-relevant events

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is installed and running
   - Check `ollama_base_url` in configuration
   - Verify model availability with `ollama list`

2. **Voice Features Not Working**
   - Install system audio dependencies
   - Check microphone permissions
   - Verify TTS/STT engine configuration

3. **Tool Loading Errors**
   - Check tool dependencies are installed
   - Verify tool class implementations
   - Review error logs for specific issues

4. **Performance Issues**
   - Monitor system resources usage
   - Adjust cache settings
   - Check network connectivity for cloud services

### Debugging
- **Verbose Logging**: Set `LOG_LEVEL=DEBUG` for detailed logs
- **Performance Monitoring**: Use built-in performance metrics
- **Health Checks**: Regular system diagnostics
- **Error Tracking**: Comprehensive error logging and reporting

### Support Resources
- **Documentation**: `/docs` directory for detailed guides
- **Examples**: Sample configurations and usage patterns
- **Community**: GitHub issues and discussions
- **Development**: Contributing guidelines and roadmap

---

**Last Updated**: January 2025  
**Version**: 2.0.0  
**License**: MIT
