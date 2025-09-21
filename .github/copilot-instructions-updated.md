# Copilot Instructions for ULTRON Agent 3.0

## Project Architecture & Key Components

### Core Components
- **agent_core.py**: Main integration hub. Initializes config, memory, voice, vision, event system, performance monitor, task scheduler, and the modular brain. Handles command routing, tool loading, and system events. Features FastAPI/Socket.IO integration for real-time communication and unified single-port architecture.
- **brain.py**: Core AI logic with Ollama integration. Handles planning, acting, and project analysis. Supports multiple AI models (Claude, GPT, Mistral, Gemini) via NVIDIA API integration. Includes streaming responses, async chat processing, and fallback mechanisms.
- **voice_manager.py / voice.py**: Multi-engine voice system with ElevenLabs TTS integration and comprehensive fallback logic (pyttsx3, OpenAI TTS, Web Speech API, console output).
- **gui/ultron_enhanced/web/index.html**: PRIMARY GUI (Enhanced ULTRON Pokédex GUI - EUP GUI) - This is the main user interface with real-time voice interaction, multi-model AI chat, and comprehensive system monitoring.
- **ollama_manager.py**: Handles AI model management, switching, and status monitoring for local Ollama models.
- **config.py**: Loads and manages configuration from `ultron_config.json` with environment variable overrides for sensitive data.
- **tools/**: Modular tool plugins with standardized `match` and `execute` methods. Tools are dynamically discovered and loaded by `agent_core.py`.
- **utils/**: Event system, performance monitor, task scheduler, and startup helpers.

### New Critical Systems
- **utils/ultron_logger.py**: CENTRALIZED LOGGING SYSTEM - All components must use this for structured JSON logging with component-specific log files, AI decision tracking, and file operation logging.
- **utils/model_awareness.py**: AI MODEL AWARENESS SYSTEM - All AI models must check this before file modifications to ensure system stability and coordinate concurrent changes.
- **logs/**: CENTRAL LOG STORAGE - All logs are stored here with structured JSON format for analysis and debugging.
- **.continue/config.yaml**: Continue extension configuration with multi-model support (Claude, GPT, Mistral, Ollama, etc.).

## Developer Workflows

### Standard Development
- **Run the agent**: `python main.py` or use `run.bat` for full diagnostics and startup checks.
- **Run tests**: `pytest` (all tests in `tests/` directory).
- **Debug**: Use centralized log files in `logs/` directory for diagnostics (`agent_core.log`, `brain.log`, `voice.log`, etc.).
- **Configuration**: Edit `ultron_config.json` for API keys, model settings, and feature toggles. Environment variables override sensitive values.
- **Model management**: Use Ollama (`ollama run <model>`) for model downloads and switching.

### AI-Assisted Development
- **Copilot Auto-Approval**: All Copilot actions are automatically approved via enhanced VS Code settings.
- **Model Awareness**: Before making any file changes, AI models check `utils/model_awareness.py` for:
  - Recent file modifications (last 7 days)
  - System stability and error status
  - Concurrent changes by other components
  - File dependencies and relationships
- **Centralized Logging**: All AI activities are logged to `logs/ai_activities.log` with decision context and confidence scores.
- **Continue Extension**: Multi-model AI support with Claude 3.7 Sonnet, GPT-4o, Mistral Codestral, and local Ollama models configured in `.continue/config.yaml`.

## Project-Specific Patterns & Conventions

### Configuration Management
- **Primary Config**: `ultron_config.json` (not `config.py` which is a stub)
- **Environment Variables**: Override sensitive values (API keys) - see `.continue/config.yaml` for examples
- **Dynamic Loading**: Tools auto-discovered from `tools/` package
- **Service Ports**: 8000 (AI Chat), 8080 (Web GUI), 5000 (API)

### Tool Development Pattern
```python
# tools/example_tool.py
from utils.ultron_logger import log_info, log_error

class ExampleTool:
    name = "Example Tool"
    description = "Description of what this tool does"

    def __init__(self, config=None):
        self.config = config

    def match(self, command: str) -> bool:
        log_info("example_tool", f"Matching command: {command}")
        return "example" in command.lower()

    def execute(self, command: str, context: dict = None) -> str:
        log_info("example_tool", f"Executing with command: {command}")
        try:
            # Tool implementation with error handling
            result = "Tool executed successfully"
            log_info("example_tool", f"Tool execution completed: {result}")
            return result
        except Exception as e:
            log_error("example_tool", f"Tool execution failed: {str(e)}")
            return f"Error: {str(e)}"

    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {}
        }
```

### Voice Integration
- **ElevenLabs Priority**: Primary TTS/STT when API key configured
- **Fallback Chain**: ElevenLabs → pyttsx3 → OpenAI → Console output
- **Thread Safety**: All voice operations support async mode
- **Error Handling**: Graceful degradation when services unavailable

### Event System Usage
```python
# Subscribe to events
self.event_system.subscribe("command_complete", self.handle_completion)

# Emit events
await self.event_system.emit("command_start", {"command": cmd})
```

### Async/Await Patterns
- **Core Logic**: Most operations are async for responsiveness
- **Sync Wrappers**: Provided for GUI compatibility
- **Timeout Handling**: 30-second default for network operations
- **Cancellation**: Proper cleanup on shutdown signals

### Continue Extension Integration
```yaml
# .continue/config.yaml - Multi-model configuration
models:
  - name: Claude 3.7 Sonnet
    provider: anthropic
    model: claude-3-7-sonnet-20240229
    apiKey: ${ANTHROPIC_API_KEY}
    roles: [chat, edit, apply]

  - name: Local Agent
    provider: openai
    model: gpt-3.5-turbo
    apiBase: http://localhost:8000/v1
    apiKey: ultron-local-key
    roles: [chat, edit, apply]
```

## Integration Points & External Dependencies

### AI Services
- **Ollama**: Primary LLM backend (`http://localhost:11434`) - auto-started by `run.bat`
- **Anthropic Claude**: Primary model via `ANTHROPIC_API_KEY` environment variable (Claude 3.7 Sonnet preferred)
- **OpenAI GPT**: High-performance model via `OPENAI_API_KEY` environment variable (GPT-4o)
- **Mistral Codestral**: Coding specialist via `MISTRAL_API_KEY` environment variable
- **Google Gemini**: Fast model via `GEMINI_API_KEY` environment variable (Gemini 2.0 Flash)
- **ElevenLabs**: Voice synthesis via `ELEVENLABS_API_KEY` environment variable with Convai widget integration
- **GitHub**: Repository access via `GITHUB_TOKEN` environment variable

### Python Dependencies
- **FastAPI**: REST API framework with Socket.IO integration
- **WebSockets**: Real-time communication
- **SpeechRecognition**: Local STT fallback
- **PyAutoGUI**: System automation
- **AsyncIO**: Core async framework
- **Transformers**: For enhanced mesh transformer integration

### VS Code Integration
- **Copilot Settings**: Auto-enabled with `.vscode/settings.json` configuration
- **Continue Extension**: Multi-model support with MCP servers (GitHub, filesystem, etc.)
- **File Watcher Exclusions**: Optimized for performance with excluded directories
- **Python Environment**: Uses `.venv-1` virtual environment

## Key Files & Directories

### Core Files
- `main.py` - Application entry point with GUI mode detection
- `brain.py` - AI reasoning engine with Ollama and multi-model support
- `voice.py` - Voice processing system with ElevenLabs integration
- `ultron_config.json` - Configuration file with API keys and settings
- `run.bat` - Production launcher with Ollama service management

### Service Files
- `nvidia_enhanced_ultron.py` - AI chat server with enhanced mesh transformer
- `web_gui_server.py` - Web interface server
- `api_server.py` - REST API server
- `ultron_assistant/` - Standalone assistant with web interface

### Tool Ecosystem
- `tools/` - All tool plugins with base class in `tools/base.py`
- `tools/agent_network.py` - Multi-agent coordination
- `tools/openai_tools.py` - OpenAI integration tools

### Utilities
- `utils/event_system.py` - Event communication
- `utils/performance_monitor.py` - System monitoring
- `utils/task_scheduler.py` - Background task management
- `utils/ultron_logger.py` - Centralized logging system
- `utils/model_awareness.py` - AI model awareness system

### Configuration Files
- `ultron_config.json` - Main configuration
- `.continue/config.yaml` - Continue extension configuration
- `.vscode/settings.json` - VS Code settings with Copilot configuration
- `requirements.txt` - Python dependencies

## Development Best Practices

### Code Organization
- **Separation of Concerns**: Each service runs independently
- **Error Boundaries**: Comprehensive try/catch with logging
- **Resource Cleanup**: Proper shutdown handling for all services
- **Configuration First**: Load config before initializing components

### Performance Considerations
- **Caching**: Response caching in `brain.py` for repeated queries
- **Async Operations**: Non-blocking I/O for all network calls
- **Memory Management**: Monitor via performance utilities
- **Background Processing**: Use task scheduler for long-running tasks

### Security Patterns
- **Input Sanitization**: All user inputs validated and sanitized
- **API Key Management**: Environment variables for sensitive data
- **Error Logging**: Sanitized error messages without sensitive data
- **Network Security**: Timeout and retry logic for external APIs

## Common Development Tasks

### Adding New Tools
1. Create tool class in `tools/` directory following the base pattern
2. Implement `match()`, `execute()`, and `schema()` methods
3. Add comprehensive logging using `utils/ultron_logger`
4. Tool auto-discovered on restart

### Adding Voice Features
1. Configure ElevenLabs API key in `ultron_config.json`
2. Use `voice.py` methods for TTS/STT with fallback chain
3. Handle fallbacks for offline scenarios
4. Test with different voice engines

### Adding API Endpoints
1. Add routes to FastAPI applications (main.py or api_server.py)
2. Use FastAPI decorators and Pydantic models
3. Integrate with event system for cross-service communication
4. Add proper error handling and logging

### Debugging Issues
1. Check component-specific logs in `logs/` directory
2. Use VS Code debugger with launch configurations
3. Monitor events via `utils/event_system.py`
4. Check performance metrics with monitoring tools
5. Use `run.bat` for comprehensive startup diagnostics

### Multi-Model AI Integration
1. Configure models in `.continue/config.yaml`
2. Set environment variables for API keys
3. Test model switching and fallback mechanisms
4. Monitor AI decision logging in `logs/ai_activities.log`

---

## CI/CD Integration: Ultron Command Runner

### Overview
The Ultron Agent repository includes a GitHub Actions-based CI system for safe, remote edits via `/ultron` commands. This feature enables collaborative development while enforcing project guardrails (model awareness, centralized logging, and reversibility).

### Setup Requirements
- GitHub Actions enabled in the repository
- Existing utilities: `utils/model_awareness.py`, `utils/ultron_logger.py`
- Logs directory: `logs/` (auto-created if missing)

### Usage Examples

#### Single File Edit with Context
```
/ultron edit
```yaml
file: brain.py
intent: "Refactor: extract plan() substeps into pure functions"
change:
  type: replace_with_context
  before: |
    def plan(self, ...):
        # existing logic line A
        # existing logic line B
  after: |
    def plan(self, ...):
        plan_steps = self._plan_steps(...)
        return self._execute_plan(plan_steps)
tests: true
```

#### Regex Replacement
```
/ultron replace
```yaml
file: utils/performance_monitor.py
intent: "Increase default timeout from 30s to 45s"
change:
  type: replace_regex
  pattern: r"(DEFAULT_TIMEOUT\s*=\s*)30(\s*)"
  replacement: "\\g<1>45\\2"
tests: true
```

#### Batch Changes
```
/ultron edit
```yaml
intent: "Rename event 'command_start' → 'task_start' across modules"
changes:
  - { type: replace_regex, file: "brain.py", pattern: "command_start", replacement: "task_start" }
  - { type: replace_regex, file: "agent_core.py", pattern: "command_start", replacement: "task_start" }
tests: true
```

### Guardrails and Safety
- **Model Awareness**: Every edit checks `should_modify_file()` and `check_file_context()` before application.
- **Centralized Logging**: All actions logged to `logs/ai_activities.log` and `logs/file_changes.log`.
- **Reversibility**: Changes create PRs for review; use Git for rollbacks.
- **Testing**: Optional `tests: true` runs `pytest` and blocks merges on failures.
- **Security**: Uses only `GITHUB_TOKEN` with minimal permissions.

### Workflow Triggers
- Issue comments containing `/ultron`
- PR review comments
- Manual workflow dispatch

### Artifacts and Auditing
- Logs uploaded as workflow artifacts for review
- PRs created automatically with unified diffs
- Feedback posted back to the triggering comment

### Troubleshooting
- Check workflow logs for errors
- Verify `utils/model_awareness.py` and `utils/ultron_logger.py` are functional
- Ensure branch protection rules allow bot PRs

---

*This document reflects the current state of ULTRON Agent 3.0. Update as architecture evolves.*
