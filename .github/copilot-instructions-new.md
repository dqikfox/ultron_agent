# ULTRON Agent 3.0 - AI Developer Instructions

## Project Architecture & Key Components

### Core System Design
This is a multi-modal AI agent platform with **voice-first architecture**, combining local LLMs (Ollama) with cloud APIs and a sophisticated web-based GUI. The system follows an event-driven, modular design with centralized logging and AI model coordination.

### Core Components
- **main.py**: Single entry point - initializes UltronAgent with signal handling and basic logging setup
- **agent_core.py**: Primary integration hub following copilot instructions architecture. Initializes all subsystems (config, voice, vision, tools), handles dynamic tool discovery, and manages component lifecycle
- **config.py**: Comprehensive configuration system using `ultron_config.json` with JSON Schema validation and environment variable overrides
- **utils/ultron_logger.py**: **MANDATORY** centralized logging with component-specific log files (`logs/agent_core.log`, etc.)
- **utils/model_awareness.py**: **CRITICAL** AI coordination system - must be checked before ANY file modifications
- **tools/**: Modular plugin system with auto-discovery - tools implement `match()`, `execute()`, and `schema()` methods

### GUI Architecture
- **PRIMARY GUI**: `gui/ultron_enhanced/web/index.html` - The ONLY active interface (Pokédex-style design)
- **Technology**: Vanilla HTML5/CSS3/JavaScript with Socket.IO for real-time communication
- **Deprecated**: All other GUI files (gui_ultimate.py, gui_clean.py, etc.) should NOT be used
- **Launch Method**: Use `run.bat` or serve locally with Python HTTP server on port 8080

## Developer Workflows

### Standard Development
- **Start System**: `run.bat` (RECOMMENDED) - Comprehensive launcher that starts Ollama, web server, and all services
- **Entry Point**: `python main.py` for minimal startup
- **Available Tasks**: Use VS Code tasks: "Start Ollama Service", "Pull Models", "Run Ultron Assistant"
- **Configuration**: Edit `ultron_config.json` for settings; sensitive values use `USE_ENV_*` pattern
- **Default Model**: `qwen3-coder:480b-cloud` via Ollama on localhost:11434

### Critical AI Development Rules
- **BEFORE ANY FILE EDIT**: Check `utils/model_awareness.py` using `should_modify_file()`
- **LOGGING REQUIREMENT**: Use `from utils.ultron_logger import get_logger` and log all activities
- **Primary GUI Only**: Only modify `gui/ultron_enhanced/web/index.html` - ignore all other GUI files
- **Tool Discovery**: Place new tools in `tools/` - they're auto-discovered by `agent_core.py`

## Project-Specific Patterns & Conventions

### Configuration Management
- **Primary Config**: `ultron_config.json` (not `config.py` which is a stub)
- **Environment Variables**: Override sensitive values (API keys)
- **Dynamic Loading**: Tools auto-discovered from `tools/` package
- **Service Ports**: 8000 (AI Chat), 8080 (Web GUI), 5000 (API)

### Tool Development Pattern
```python
# tools/example_tool.py
class ExampleTool:
    name = "Example Tool"
    description = "Description of what this tool does"

    def match(self, command: str) -> bool:
        return "example" in command.lower()

    def execute(self, command: str) -> str:
        # Tool implementation
        return "Tool result"

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
- **Fallback Chain**: ElevenLabs → pyttsx3 → Console output
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

## Integration Points & External Dependencies

### AI Services
- **Ollama**: Primary LLM backend (`http://localhost:11434`)
- **OpenAI**: Fallback API integration
- **ElevenLabs**: Voice synthesis and recognition
- **Supabase**: Database and real-time features

### Python Dependencies
- **FastAPI**: REST API framework
- **WebSockets**: Real-time communication
- **SpeechRecognition**: Local STT fallback
- **PyAutoGUI**: System automation
- **AsyncIO**: Core async framework

### External Services
- **Ollama Server**: Must be running locally on port 11434
- **ElevenLabs API**: Requires API key for voice features
- **Supabase**: Configured with anon key for database access

## Key Files & Directories

### Core Files
- `main.py` - Application entry point
- `brain.py` - AI reasoning engine
- `voice.py` - Voice processing system
- `ultron_config.json` - Configuration file
- `run.bat` - Production launcher

### Service Files
- `nvidia_enhanced_ultron.py` - AI chat server
- `web_gui_server.py` - Web interface
- `api_server.py` - REST API server

### Tool Ecosystem
- `tools/` - All tool plugins
- `tools/base.py` - Tool base class
- `tools/agent_network.py` - Multi-agent coordination

### Utilities
- `utils/event_system.py` - Event communication
- `utils/performance_monitor.py` - System monitoring
- `utils/task_scheduler.py` - Background task management

### Testing
- `tests/` - Test suite
- `conftest.py` - Test configuration
- `pytest.ini` - Test settings

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
1. Create tool class in `tools/` directory
2. Implement `match()`, `execute()`, and `schema()` methods
3. Tool auto-discovered on restart

### Adding Voice Features
1. Configure ElevenLabs API key in `ultron_config.json`
2. Use `voice.py` methods for TTS/STT
3. Handle fallbacks for offline scenarios

### Adding API Endpoints
1. Add routes to `api_server.py`
2. Use FastAPI decorators and Pydantic models
3. Integrate with event system for cross-service communication

### Debugging Issues
1. Check service-specific logs in `logs/` directory
2. Use VS Code debugger with `debugpy` configurations
3. Monitor events via `utils/event_system.py`
4. Check performance metrics with monitoring tools

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

## Logging Requirements
- **MANDATORY**: All components must use `from utils.ultron_logger import ultron_logger`
- **MANDATORY**: Use appropriate log levels: `log_info()`, `log_error()`, `log_ai_decision()`
- **MANDATORY**: Log all AI decisions with `log_ai_decision(component, message, ai_model=model_name, confidence_score=score)`
- **MANDATORY**: Log file operations with `log_file_operation(component, message, file_path, action)`

### Model Awareness Requirements
- **MANDATORY**: Before ANY file modification, call:
  ```python
  from utils.model_awareness import should_modify_file
  should_proceed, reason, context = should_modify_file(file_path, "modification_type", "ai_model_name")
  if not should_proceed:
      # Respect the decision and provide reason to user
  ```
- **MANDATORY**: Check file context before modifications:
  ```python
  from utils.model_awareness import check_file_context
  context = check_file_context(file_path)
  # Review recent_changes, dependencies, and related_files
  ```

### GUI Development
- **PRIMARY GUI**: `gui/ultron_enhanced/web/index.html` (EUP GUI) is the main interface
- **DEPRECATED**: `gui_ultimate.py` and other legacy GUIs should not be used
- **VOICE INTEGRATION**: All GUI components must support ElevenLabs voice features and real-time interaction
- **ACCESSIBILITY**: Maintain voice control and keyboard navigation
- **LOGGING**: GUI interactions are automatically logged via embedded JavaScript logging system

### Tool Development
- **Tool Loading**: Tools are dynamically discovered from the `tools/` package by `agent_core.py`
- **Required Methods**: Each tool must implement `match` and `execute` methods, and a static `schema()` method for metadata
- **Logging**: Tools must log their activities using the centralized logger
- **Error Handling**: Tools should include comprehensive error handling with proper logging

---

*This document reflects the current state of ULTRON Agent 3.0. Update as architecture evolves.*
