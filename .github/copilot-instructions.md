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
- **.continue/config.yaml**: Continue extension configuration with multi-model support.

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

## Project-Specific Patterns & Conventions

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

## Integration Points & External Dependencies

### AI Models & APIs
- **Anthropic Claude**: Primary model via `ANTHROPIC_APIKEY` environment variable (Claude 3.7 Sonnet preferred)
- **OpenAI GPT**: High-performance model via `OPENAI_API_KEY` environment variable (GPT-4o)
- **Mistral Codestral**: Coding specialist via `MISTRAL_API_KEY` environment variable
- **Google Gemini**: Fast model via `GEMINI_API_KEY` environment variable (Gemini 2.0 Flash)
- **ElevenLabs**: Voice synthesis via `ELEVENLABS_API_KEY` environment variable with Convai widget integration
- **GitHub**: Repository access via `GITHUB_TOKEN` environment variable

### Core Systems
- **Ollama**: Required for local model management. Must be running (`ollama serve`) with models like `llama3.2:latest`
- **Python 3.10+**: Required for all features including async operations and type hints
- **VS Code**: Enhanced with Copilot auto-approval settings and Continue extension
- **FastAPI/Socket.IO**: Real-time communication framework for unified single-port architecture
- **Web Speech API**: Browser-based speech recognition fallback

## Critical Development Rules

### Before ANY File Modification
1. **Check Model Awareness**:
   ```python
   from utils.model_awareness import should_modify_file, check_file_context
   context = check_file_context(file_path)
   should_proceed, reason, _ = should_modify_file(file_path, "edit", "copilot")
   ```

2. **Log the Decision**:
   ```python
   from utils.ultron_logger import log_ai_decision
   log_ai_decision("copilot", f"Considering modification to {file_path}", ai_model="copilot")
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
    should_proceed, reason, _ = should_modify_file(file_path, "edit", "copilot")

    if not should_proceed:
        log_ai_decision("copilot", f"Modification denied: {reason}", ai_model="copilot")
        return False

    # Log the modification
    log_ai_decision("copilot", f"Proceeding with modification to {file_path}", ai_model="copilot")

    # Perform modification with error handling
    try:
        # ... modification code ...
        log_file_operation("copilot", f"Modified {file_path}", file_path, "edit")
        return True
    except Exception as e:
        log_error("copilot", f"File modification failed: {str(e)}")
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

## Key Files & Directories

### Core System Files
- `agent_core.py` - Main integration hub with FastAPI/Socket.IO
- `brain.py` - Core AI logic with Ollama and multi-model support
- `config.py` - Configuration management with environment variable support
- `voice_manager.py` - Unified voice system with ElevenLabs integration
- `ollama_manager.py` - Local model management and switching

### New Critical Systems
- `utils/ultron_logger.py` - CENTRALIZED LOGGING SYSTEM
- `utils/model_awareness.py` - AI MODEL AWARENESS SYSTEM
- `logs/` - CENTRAL LOG STORAGE with component-specific files
- `gui/ultron_enhanced/web/index.html` - PRIMARY EUP GUI

### Configuration Files
- `ultron_config.json` - Main configuration with API keys and settings
- `.vscode/settings.json` - Enhanced Copilot settings
- `.continue/config.yaml` - Continue extension configuration
- `requirements.txt` - Python dependencies

### Development Tools
- `run.bat` - Unified startup script with diagnostics
- `tests/` - Test suite with pytest
- `docs/` - Documentation and guides
- `tools/` - Modular tool plugins

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
