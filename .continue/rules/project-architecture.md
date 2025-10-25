# ULTRON Agent 3.0 - Project Architecture Rules

## Core Architecture Principles

### 1. Modular Tool System
- All tools in `tools/` directory with standardized interface
- Dynamic discovery via `agent_core.py`
- Each tool implements `match()` and `execute()` methods

### 2. Event-Driven Communication
- Central event system in `utils/event_system.py`
- Pub/sub pattern for cross-component communication
- Async operations for responsiveness

### 3. Multi-Modal Interfaces
- Primary GUI: `gui/ultron_enhanced/web/index.html` (EUP GUI)
- Voice system: `voice_manager.py` with ElevenLabs integration
- API endpoints: FastAPI with WebSocket support
- CLI interface through console commands

### 4. AI Integration Layers
- **Ollama Backend**: Local LLM models on port 11434
- **Continue Extension**: Code assistance and MCP integration
- **Amazon Q**: AWS AI coding assistant integration
- **GitHub Copilot**: Pair programming support

## Key Components

### Core Files
- `agent_core.py` - Main integration hub
- `brain.py` - AI reasoning engine
- `config.py` - Configuration management
- `voice_manager.py` - Voice system controller

### Service Architecture
- `nvidia_enhanced_ultron.py` - AI chat server (port 8000)
- `web_gui_server.py` - Web interface (port 8080)
- `api_server.py` - REST API (port 5000)
- `gui_ocr_integration.py` - Enhanced API (port 5001)

### Tool Ecosystem
- Modular plugins in `tools/` directory
- MCP server integrations
- Windows system control
- Browser automation
- OCR and vision processing

## Integration Points

### Amazon Q Integration
- VS Code extension for code assistance
- Workspace-aware code suggestions
- Real-time error detection and fixes
- Integration with ULTRON's tool system

### Continue Extension
- Multi-model LLM support
- MCP server orchestration
- Codebase documentation awareness
- Context-aware code generation

### ULTRON Agent Coordination
- Unified command routing through `agent_core.py`
- Shared configuration in `ultron_config.json`
- Centralized logging via `utils/ultron_logger.py`
- Cross-service communication via event system

## Development Patterns

### Tool Development
```python
class NewTool:
    name = "tool_name"
    description = "Tool description"

    def match(self, command: str) -> bool:
        return "keyword" in command.lower()

    def execute(self, command: str, **kwargs) -> str:
        # Implementation
        return "Result"
```

### Service Integration
- Use async/await for I/O operations
- Implement proper error handling with logging
- Follow event-driven patterns for communication
- Maintain thread safety for GUI operations

### Configuration Management
- Environment variables for sensitive data
- JSON configuration for application settings
- Dynamic reloading for development
- Validation and fallback mechanisms
