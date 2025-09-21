# Comprehensive Project-Aware Editing Prompt

## Core Principles for Code Modifications

### 1. **Project Scope Awareness**
- Always analyze the ENTIRE project architecture before making ANY changes
- Review `README.md`, `ultron_config.json`, `.github/copilot-instructions.md`, and `CODE_REFERENCE_LOG.md` for context
- Understand the relationship between core files: `agent_core.py` (main integration hub), `brain.py` (AI reasoning), `voice_manager.py` (voice system), `ollama_manager.py` (model management), `config.py` (configuration)
- Review web interface structure: `gui/ultron_enhanced/web/index.html` (main GUI), `gui/ultron_enhanced/web/styles.css` (styling), `gui/ultron_enhanced/web/app.js` (frontend logic)
- Check dependencies in `requirements.txt` and existing imports
- Consider the modular plugin system in `tools/` directory with 20+ available tools
- Review VS Code configuration: `.vscode/settings.json` with multiple AI tools (GitHub Copilot, Amazon Q, Continue extension)
- Check Continue extension setup: `.continue/config.yaml`, `.continue/config.json`, and custom prompts in `.continue/prompts/`
- Understand startup sequence: `main.py` (primary entry), `run.bat` (Windows startup), `main_gui_server_fixed.py` (GUI server)
- Review service ports: GUI (5000 with auto-fallback), AI Chat (8000 planned), Ollama (11434), API Server (8001 planned)
- Consider recent implementations: Tool Integration Display, GitHub Actions CI bridge (`.github/workflows/ultron_agent.yml`, `scripts/ultron_ci/command_runner.py`)
- Be aware of common issues: API server may not be running (backend offline), ensure proper integration with agent core

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
- Does this impact the GUI integration (`gui/ultron_enhanced/web/index.html`, `gui/ultron_enhanced/web/app.js`)?
- Will voice functionality still work (`voice_manager.py`, `voice.py`)?
- Are tool plugins still discoverable (`tools/` directory)?
- Will configuration loading/saving still function (`config.py`)?
- Does this affect the Continue extension integration (`.continue/config.yaml`)?
- Will this impact the GitHub Actions CI workflow (`.github/workflows/ultron_agent.yml`)?
- Does this maintain compatibility with the startup sequence (`run.bat`, `main.py`)?
- Will this affect service connectivity (ports 5000, 8000, 11434, 8001)?

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
- **Voice System**: Keep fallback chain intact (ElevenLabs → pyttsx3 → OpenAI → Console)
- **Model Management**: Preserve Ollama integration and model switching (llama3.2:latest primary)
- **Web Interface**: Maintain Pokédex-inspired design and Socket.IO integration
- **Continue Extension**: Respect custom prompts and configuration in `.continue/` directory
- **GitHub Actions CI**: Ensure compatibility with remote editing workflow
- **Service Ports**: Maintain proper port allocation and auto-fallback mechanisms

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
- `gui/ultron_enhanced/web/index.html`: Main GUI - changes affect user experience
- `gui/ultron_enhanced/web/app.js`: Frontend logic - affects user interactions
- `gui/ultron_enhanced/web/styles.css`: GUI styling - affects visual design
- `tools/`: Plugin system - changes affect tool discovery and execution
- `ultron_config.json`: Main configuration - affects all system behavior
- `.continue/config.yaml`: Continue extension config - affects AI assistance
- `.github/workflows/ultron_agent.yml`: CI workflow - affects remote editing
- `run.bat`: Startup script - affects system initialization

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

## Helpful Knowledge for ULTRON Agent Development

### Current Project Structure
- **Version**: ULTRON Agent 3.0
- **Language**: Python 3.10+
- **Architecture**: Modular Plugin System
- **Primary GUI**: Pokédex-inspired web interface (`gui/ultron_enhanced/web/`)
- **AI Models**: Ollama (llama3.2:latest primary), OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Voice System**: ElevenLabs (primary), pyttsx3, OpenAI TTS, Console fallback
- **Tools**: 20+ modular tools in `tools/` directory with standardized `match()` and `execute()` methods

### Key Integration Points
- **Agent Core** (`agent_core.py`): Central hub coordinating all components
- **Brain System** (`brain.py`): AI reasoning with multi-model support and streaming
- **Voice Manager** (`voice_manager.py`): Unified voice interface with fallback chain
- **Web Interface**: HTML5/CSS3/JS with Socket.IO for real-time communication
- **Tool Ecosystem**: Dynamic loading from `tools/` with base class in `tools/base.py`
- **Event System** (`utils/event_system.py`): Cross-component communication
- **Configuration**: `ultron_config.json` with environment variable overrides

### VS Code and AI Tools Integration
- **GitHub Copilot**: Enabled for completions, chat, and inline suggestions
- **Amazon Q**: CodeWhisperer integration
- **Continue Extension**: Custom configuration in `.continue/` with project-specific prompts
- **Performance Settings**: File watcher exclusions, memory limits, proxy configuration

### Common Issues and Solutions
- **API Server Offline**: Ensure `api_server.py` is running and integrated with agent core
- **Backend Connectivity**: Check ports 5000 (GUI), 8000 (AI Chat), 11434 (Ollama), 8001 (API)
- **Tool Discovery**: Verify tools implement required `match()` and `execute()` methods
- **Voice Fallback**: Test ElevenLabs → pyttsx3 → OpenAI → Console chain
- **Model Switching**: Ensure Ollama is running and models are available
- **GUI Updates**: Use Socket.IO for real-time updates, maintain Pokédex theme

### Development Workflow
- **Startup**: Use `run.bat` for full system initialization with service checks
- **Testing**: Run `pytest` for test suite, check `tests/` directory
- **Logging**: Centralized logging in `logs/` directory with component-specific files
- **CI/CD**: GitHub Actions workflow for safe remote edits via `/ultron` commands
- **Documentation**: Update `README.md`, `.github/copilot-instructions.md`, and `CODE_REFERENCE_LOG.md`

### Recent Implementations
- **Tool Integration Display**: GUI section for tool management with real-time status
- **GitHub Actions CI**: Remote editing workflow with model awareness and logging
- **Continue Extension**: Custom prompts for ULTRON-specific development assistance

## Emergency Rollback Strategy
- Always use the `replace_string_in_file` tool with sufficient context
- Include 3-5 lines before and after changes for precise targeting
- Test immediately after changes when possible
- Be prepared to revert if integration points break

---

**Remember**: This is a complete, functioning AI assistant system with accessibility features. Every change should enhance rather than diminish its capabilities unless explicitly required otherwise.
