# Amazon Q Instructions for ULTRON Agent 3.0

## Core Principles for Code Modifications

### 1. **Project Scope Awareness**
- Always analyze the ENTIRE project architecture before making ANY changes
- Review `README.md`, `ultron_config.json`, and `.github/copilot-instructions.md` for context
- Understand the relationship between files: `agent_core.py`, `brain.py`, `gui_ultimate.py`, `voice_manager.py`, `ollama_manager.py`
- Check dependencies in `requirements.txt` and existing imports
- Consider the modular plugin system in `tools/` directory

### 2. **Functionality Preservation**
- **NEVER** remove existing functionality unless explicitly requested
- **ALWAYS** maintain backward compatibility with existing APIs
- **PRESERVE** all existing method signatures and return types
- **MAINTAIN** configuration compatibility in `ultron_config.json`
- **KEEP** all existing event system integrations intact

### 3. **Integration Impact Assessment**
Before editing ANY file, ask:
- How does this change affect other components?
- Will this break the event system (`utils/event_system.py`)?
- Does this impact the GUI integration (`gui_ultimate.py`)?
- Will voice functionality still work (`voice_manager.py`, `voice.py`)?
- Are tool plugins still discoverable (`tools/` directory)?
- Will configuration loading/saving still function (`config.py`)?

### 4. **Testing and Validation Requirements**
- Consider existing test coverage in `tests/`
- Ensure changes don't break `pytest` execution
- Verify startup sequence compatibility (`run.bat`, `main.py`)
- Check logging systems remain functional (`startup.log`, `error.log`, etc.)

### 5. **Architecture Respect**
- **Agent Core**: Central hub - never break its integration points
- **Modular Tools**: Always maintain plugin discovery mechanism
- **Event System**: Preserve pub/sub patterns for cross-component communication
- **GUI Threading**: Maintain thread-safe operations for GUI components
- **Voice System**: Keep fallback chain intact (Enhanced → pyttsx3 → OpenAI → Console)
- **Model Management**: Preserve Ollama integration and model switching

### 6. **Change Implementation Strategy**
1. **Analyze First**: Read related files to understand current implementation
2. **Plan Incrementally**: Make small, testable changes rather than large rewrites
3. **Preserve Interfaces**: Add new functionality alongside existing code
4. **Document Changes**: Update comments and docstrings appropriately
5. **Test Integration**: Verify the change works with existing systems

### 7. **Critical Files - Handle with Extra Care**
- `agent_core.py`: Main integration hub - changes affect everything
- `config.py`: Configuration system - breaking changes affect startup
- `brain.py`: Core AI logic - changes affect all reasoning capabilities
- `voice_manager.py`: Voice system - changes affect accessibility features
- `gui_ultimate.py`: Main GUI - changes affect user experience
- `tools/`: Plugin system - changes affect tool discovery and execution

### 8. **When Functionality Loss IS Acceptable**
Only remove/change functionality when:
- Explicitly requested by user with clear understanding of impact
- Replacing with superior functionality that maintains same interface
- Fixing critical security vulnerabilities
- Removing deprecated code that's already marked for removal

### 9. **Always Consider Accessibility**
- Maintain voice control capabilities for hands-free operation
- Preserve keyboard navigation where applicable
- Keep error messages clear and spoken feedback functional
- Ensure GUI remains usable without mouse input

### 10. **Documentation Updates**
When making changes:
- Update relevant sections in `README.md`
- Modify `.github/copilot-instructions.md` if architecture changes
- Update configuration examples in documentation
- Add comments explaining new integration points

## Before Every Edit, Ask:
1. "What is the full scope of this change across the project?"
2. "Will this break any existing integrations?"
3. "Are there tests I should check or update?"
4. "Does this preserve the accessibility features?"
5. "Is this change documented appropriately?"

## Emergency Rollback Strategy
- Always use the `replace_string_in_file` tool with sufficient context
- Include 3-5 lines of unchanged code before and after changes for precise targeting
- Test immediately after changes when possible
- Be prepared to revert if integration points break

---

**Remember**: This is a complete, functioning AI assistant system with accessibility features. Every change should enhance rather than diminish its capabilities unless explicitly required otherwise.

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
- **.continue/config.yaml**: Continue extension configuration with multi-model support.

## Developer Workflows

### Standard Development
- **Run the agent**: `python main.py` or use `run.bat` for full diagnostics and startup checks.
- **Run tests**: `pytest` (all tests in `tests/` directory).
- **Debug**: Use centralized log files in `logs/` directory for diagnostics (`agent_core.log`, `brain.log`, `voice.log`, etc.).
- **Configuration**: Edit `ultron_config.json` for API keys, model settings, and feature toggles. Environment variables override sensitive values.
- **Model management**: Use Ollama (`ollama run <model>`) for model downloads and switching.

### AI-Assisted Development
- **Amazon Q Auto-Approval**: All Amazon Q actions are automatically approved via enhanced VS Code settings.
- **Model Awareness**: Before making any file changes, AI models check `utils/model_awareness.py` for:
  - Recent file modifications (last 7 days)
  - System stability and error status
  - Concurrent changes by other components
  - File dependencies and relationships
- **Centralized Logging**: All AI activities are logged to `logs/ai_activities.log` with decision context and confidence scores.

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

### Logging Requirements
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

## Critical Development Rules

### Before ANY File Modification
1. **Check Model Awareness**:
   ```python
   from utils.model_awareness import should_modify_file, check_file_context
   context = check_file_context(file_path)
   should_proceed, reason, _ = should_modify_file(file_path, "edit", "amazon_q")
   ```

2. **Log the Decision**:
   ```python
   from utils.ultron_logger import log_ai_decision
   log_ai_decision("amazon_q", f"Considering modification to {file_path}", ai_model="amazon_q")
   ```

3. **Review Recent Changes**:
   - Check `logs/file_changes.log` for recent modifications
   - Review `logs/ai_activities.log` for related AI activities
   - Consider system stability from recent error logs

### File Modification Guidelines
- **Core Files**: `agent_core.py`, `brain.py`, `config.py` - Require extra caution and testing
- **GUI Files**: Only modify EUP GUI (`gui/ultron_enhanced/web/index.html`)
- **Configuration**: Use environment variables for sensitive data, validate JSON syntax
- **Logging**: All changes must be logged with context and component information
- **Error Handling**: Include try/catch blocks with proper logging for all operations

### Code Quality Standards
- **Type Hints**: Use type annotations for all public functions and methods
- **Documentation**: Comprehensive docstrings and comments, especially for complex logic
- **Error Handling**: Proper exception handling with logging and user-friendly messages
- **Async/Await**: Use async patterns for I/O operations and long-running tasks
- **Security**: Sanitize inputs, validate file paths, and use secure API key handling
- **Testing**: Include unit tests for new functionality, especially for core components

## Examples

### Adding a New Tool
```python
from utils.ultron_logger import log_info, log_error
from tools.base import Tool

class NewTool(Tool):
    name = "new_tool"
    description = "Description of the tool"
    parameters = {
        "param1": {"type": "string", "description": "Parameter description"}
    }

    @staticmethod
    def schema():
        return {
            "name": NewTool.name,
            "description": NewTool.description,
            "parameters": NewTool.parameters
        }

    def match(self, command: str) -> bool:
        log_info("new_tool", f"Matching command: {command}")
        return "new_tool" in command.lower()

    def execute(self, **kwargs):
        log_info("new_tool", "Executing new tool", **kwargs)
        try:
            # Tool implementation with error handling
            result = "Tool executed successfully"
            log_info("new_tool", f"Tool execution completed: {result}")
            return result
        except Exception as e:
            log_error("new_tool", f"Tool execution failed: {str(e)}")
            return f"Error: {str(e)}"
```

### Proper File Modification
```python
from utils.model_awareness import should_modify_file, check_file_context
from utils.ultron_logger import log_ai_decision, log_file_operation

def modify_file_safely(file_path, changes):
    # Check if modification should proceed
    context = check_file_context(file_path)
    should_proceed, reason, _ = should_modify_file(file_path, "edit", "amazon_q")

    if not should_proceed:
        log_ai_decision("amazon_q", f"Modification denied: {reason}", ai_model="amazon_q")
        return False

    # Log the modification
    log_ai_decision("amazon_q", f"Proceeding with modification to {file_path}", ai_model="amazon_q")

    # Perform modification with error handling
    try:
        # ... modification code ...
        log_file_operation("amazon_q", f"Modified {file_path}", file_path, "edit")
        return True
    except Exception as e:
        log_error("amazon_q", f"File modification failed: {str(e)}")
        return False
```

### Voice System Integration
```python
from voice_manager import get_voice_manager

def speak_with_fallback(text, async_mode=True):
    """Speak text with comprehensive fallback system"""
    voice_manager = get_voice_manager()

    # Voice manager handles all fallback logic automatically
    # Order: enhanced -> pyttsx3 -> openai -> console
    return voice_manager.speak(text, async_mode)
```

### Event System Usage
```python
from utils.ultron_logger import log_info

def handle_event(event_data):
    log_info("component", f"Handling event: {event_data.get('type', 'unknown')}")
    # Event handling logic with proper logging
```

## Quality Assurance

### Pre-Commit Checks
- [ ] Model awareness check passed
- [ ] Centralized logging implemented
- [ ] File modification guidelines followed
- [ ] Error handling and type hints added
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated

### Code Review Requirements
- [ ] Type hints used appropriately for all public methods
- [ ] Comprehensive error handling with logging
- [ ] Logging at appropriate levels with context
- [ ] Model awareness integration for file modifications
- [ ] GUI changes use EUP GUI only
- [ ] Async patterns used for I/O operations
- [ ] Security best practices followed

## Emergency Contacts & Resources

- **Primary GUI**: `gui/ultron_enhanced/web/index.html` (EUP GUI)
- **Central Logs**: `logs/` directory with component-specific files
- **Model Awareness**: `utils/model_awareness.py` for file modification checks
- **Configuration**: `ultron_config.json` with environment variable support
- **Documentation**: `README.md` and project-specific guides

---

## Emergency Rollback Strategy
- Always use the `replace_string_in_file` tool with sufficient context
- Include 3-5 lines of unchanged code before and after changes for precise targeting
- Test immediately after changes when possible
- Be prepared to revert if integration points break

**Remember**: This is a production-ready AI assistant system with centralized logging, model awareness, and the Enhanced ULTRON Pokédex GUI (EUP GUI) as the primary interface. All modifications must follow these guidelines to maintain system integrity and functionality.

---

*This document reflects the current state of ULTRON Agent 3.0. Update as architecture evolves.*
