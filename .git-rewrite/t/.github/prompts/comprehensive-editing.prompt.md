# Comprehensive Project-Aware Editing Prompt

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
- Include 3-5 lines before and after changes for precise targeting
- Test immediately after changes when possible
- Be prepared to revert if integration points break

---

**Remember**: This is a complete, functioning AI assistant system with accessibility features. Every change should enhance rather than diminish its capabilities unless explicitly required otherwise.
