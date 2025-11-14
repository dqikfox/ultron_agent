# ULTRON Agent 3.0 - Development Guidelines

## Code Quality Standards

### Formatting and Structure
- **Indentation**: 4 spaces for Python, 2 spaces for JavaScript/HTML
- **Line Length**: Maximum 120 characters (Python), 100 characters (JavaScript)
- **Encoding**: UTF-8 with explicit encoding declarations in file operations
- **Docstrings**: Triple-quoted strings for all classes and public methods
- **Comments**: Inline comments for complex logic, section headers with decorative separators

### Naming Conventions
- **Classes**: PascalCase (e.g., `UltronCore`, `VoiceProcessor`, `SystemAutomation`)
- **Functions/Methods**: snake_case (e.g., `process_command`, `load_config`, `analyze_screen`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `WAKE_WORDS`, `ULTRON_ROOT`, `MAX_STRING_SIZE`)
- **Private Methods**: Leading underscore (e.g., `_init_modules`, `_handle_wake_word`)
- **File Names**: snake_case for Python (e.g., `agent_core.py`, `voice_manager.py`)

### Documentation Standards
- **Module Docstrings**: Brief description at file top with purpose and key features
- **Class Docstrings**: Purpose, initialization parameters, and key responsibilities
- **Method Docstrings**: Args, Returns, and Raises sections for public methods
- **Inline Comments**: Explain "why" not "what" for complex logic
- **Section Headers**: Use decorative comment blocks for major sections

## Semantic Patterns

### Error Handling Pattern
```python
try:
    # Primary operation
    result = perform_operation()
    log_info(f"Operation successful: {result}")
    return result
except SpecificException as e:
    log_error(f"Specific error: {e}")
    return fallback_value
except Exception as e:
    log_error(f"Unexpected error: {e}")
    raise
```
**Frequency**: Used in 95% of methods across all core modules

### Logging Pattern
```python
from utils.ultron_logger import log_info, log_error, log_ai_decision

# Information logging
log_info("component_name", "Operation description")

# Error logging
log_error("component_name", f"Error description: {str(e)}")

# AI decision logging
log_ai_decision("component", "Decision context", ai_model="model_name", confidence_score=0.95)
```
**Frequency**: Mandatory in all components, used in 100% of error handlers

### Configuration Loading Pattern
```python
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return default_config_dict

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
```
**Frequency**: Used in all configuration-dependent modules

### Async/Await Pattern
```python
async def async_operation(self, data: dict) -> dict:
    """Async operation with proper error handling"""
    try:
        result = await self.perform_async_task(data)
        return {"success": True, "result": result}
    except Exception as e:
        log_error("component", f"Async operation failed: {e}")
        return {"success": False, "error": str(e)}
```
**Frequency**: Used in 60% of I/O operations and network calls

### Event System Pattern
```python
# Subscribe to events
self.event_system.subscribe("event_name", self.handler_method)

# Emit events
await self.event_system.emit("event_name", {"data": value})

# Handler method
def handler_method(self, data: dict):
    log_info("component", f"Event received: {data}")
```
**Frequency**: Used in all inter-component communication

### Model Awareness Pattern
```python
from utils.model_awareness import should_modify_file, check_file_context

# Before file modification
context = check_file_context(file_path)
should_proceed, reason, _ = should_modify_file(file_path, "edit", "amazon_q")

if not should_proceed:
    log_ai_decision("amazon_q", f"Modification denied: {reason}")
    return False

# Proceed with modification
log_file_operation("amazon_q", f"Modifying {file_path}", file_path, "edit")
```
**Frequency**: Mandatory before any file modification (100% compliance required)

### Tool Plugin Pattern
```python
class ToolName(Tool):
    name = "tool_name"
    description = "Tool description"
    
    @staticmethod
    def schema():
        return {
            "name": ToolName.name,
            "description": ToolName.description,
            "parameters": {}
        }
    
    def match(self, command: str) -> bool:
        return "keyword" in command.lower()
    
    def execute(self, **kwargs):
        try:
            result = self.perform_action(**kwargs)
            log_info("tool_name", f"Execution successful: {result}")
            return result
        except Exception as e:
            log_error("tool_name", f"Execution failed: {str(e)}")
            return f"Error: {str(e)}"
```
**Frequency**: Standard pattern for all 15+ tools in tools/ directory

### Voice Command Pattern
```python
def process_voice_command(self, command: str):
    """Process voice commands with wake word detection"""
    # Wake word detection
    for wake_word in WAKE_WORDS:
        if wake_word in command.lower():
            self.play_sound("wake")
            command = command.replace(wake_word, "").strip()
            break
    
    # Command processing
    response = self.ai_brain.process_command(command)
    
    # Voice response
    if self.voice_engine:
        self.voice_engine.speak(response)
```
**Frequency**: Used in all voice-enabled components

### GUI Update Pattern
```python
def update_gui_element(self, element_id: str, value: str):
    """Thread-safe GUI updates"""
    try:
        if hasattr(self, 'gui') and self.gui:
            self.gui.after(0, lambda: self._update_element(element_id, value))
    except Exception as e:
        log_error("gui", f"GUI update failed: {e}")
```
**Frequency**: Used in all GUI-related operations

### Database Operation Pattern
```python
def database_operation(self, query: str, params: tuple = ()):
    """Safe database operations with connection management"""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        log_error("database", f"Database operation failed: {e}")
        if conn:
            conn.close()
        return None
```
**Frequency**: Used in all database interactions

## Internal API Usage

### Centralized Logger API
```python
from utils.ultron_logger import ultron_logger, log_info, log_error, log_ai_decision, log_file_operation

# Standard logging
log_info("component", "Message")
log_error("component", "Error message")

# AI decision logging
log_ai_decision("component", "Decision context", ai_model="model_name", confidence_score=0.95)

# File operation logging
log_file_operation("component", "Operation description", file_path, "action_type")
```
**Usage**: Mandatory in all components (100% compliance)

### Model Awareness API
```python
from utils.model_awareness import should_modify_file, check_file_context, get_file_dependencies

# Check file context
context = check_file_context(file_path)
# Returns: recent_changes, dependencies, related_files

# Validate modification
should_proceed, reason, context = should_modify_file(file_path, "edit", "ai_model")

# Get dependencies
dependencies = get_file_dependencies(file_path)
```
**Usage**: Required before all file modifications

### Event System API
```python
from utils.event_system import EventSystem

# Initialize
event_system = EventSystem()

# Subscribe
event_system.subscribe("event_name", callback_function)

# Emit
await event_system.emit("event_name", {"key": "value"})

# Unsubscribe
event_system.unsubscribe("event_name", callback_function)
```
**Usage**: All inter-component communication

### Voice System API
```python
from voice_manager import get_voice_manager

# Get voice manager instance
voice_manager = get_voice_manager()

# Speak text
voice_manager.speak(text, async_mode=True)

# Listen for input
result = voice_manager.listen(timeout=5)

# Set voice properties
voice_manager.set_voice("female")
voice_manager.set_rate(150)
```
**Usage**: All voice-related operations

### Configuration API
```python
from config import load_config, save_config

# Load configuration
config = load_config()

# Access values
api_key = config.get("openai_api_key", "")
voice_enabled = config.get("voice_enabled", False)

# Save configuration
config["new_setting"] = value
save_config(config)
```
**Usage**: All configuration-dependent modules

## Code Idioms

### Dictionary-Based Dispatch
```python
# Command routing
command_handlers = {
    "system": self.handle_system_command,
    "vision": self.handle_vision_command,
    "voice": self.handle_voice_command
}

handler = command_handlers.get(command_type, self.handle_default)
result = handler(command_data)
```
**Frequency**: Used in 80% of command routing logic

### Context Manager for Resources
```python
# File operations
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Database connections
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute(query)
```
**Frequency**: Used in 100% of file and database operations

### List Comprehensions
```python
# Data transformation
results = [process_item(item) for item in items if item.is_valid()]

# File filtering
python_files = [f for f in os.listdir(path) if f.endswith('.py')]
```
**Frequency**: Used in 70% of data processing operations

### F-String Formatting
```python
# String interpolation
message = f"Processing {count} items in {duration:.2f} seconds"
log_info("component", f"Operation completed: {result}")
```
**Frequency**: Used in 95% of string formatting operations

### Ternary Expressions
```python
# Conditional assignment
value = config.get("setting") if config else default_value
status = "active" if is_running else "inactive"
```
**Frequency**: Used in 60% of conditional assignments

### Pathlib for File Operations
```python
from pathlib import Path

# Path manipulation
project_path = Path(__file__).parent
config_file = project_path / "config.json"

# File operations
if config_file.exists():
    content = config_file.read_text(encoding='utf-8')
```
**Frequency**: Used in 80% of file path operations

## Popular Annotations

### Type Hints
```python
from typing import Dict, List, Optional, Any, Tuple

def process_data(
    data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """Process data with type hints"""
    pass
```
**Frequency**: Used in 90% of public methods

### Dataclass Decorator
```python
from dataclasses import dataclass

@dataclass
class ModelConfig:
    name: str
    version: str
    parameters: Dict[str, Any]
```
**Frequency**: Used for configuration and data structures

### Property Decorator
```python
class Component:
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str):
        self._status = value
        log_info("component", f"Status changed to {value}")
```
**Frequency**: Used in 40% of classes for computed properties

### Staticmethod and Classmethod
```python
class Tool:
    @staticmethod
    def schema() -> Dict:
        return {"name": "tool", "description": "Tool description"}
    
    @classmethod
    def from_config(cls, config: Dict):
        return cls(**config)
```
**Frequency**: Used in all tool plugins and factory patterns

## Best Practices

### Security
- **API Keys**: Always use environment variables, never hardcode
- **Input Validation**: Sanitize all user inputs before processing
- **File Paths**: Validate and sanitize file paths to prevent directory traversal
- **SQL Queries**: Use parameterized queries to prevent SQL injection
- **Error Messages**: Sanitize error messages to avoid exposing sensitive data

### Performance
- **Caching**: Cache frequently accessed data (e.g., model responses, configuration)
- **Async Operations**: Use async/await for I/O-bound operations
- **Lazy Loading**: Load resources only when needed
- **Connection Pooling**: Reuse database connections
- **Memory Management**: Clean up resources in finally blocks

### Testing
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test component interactions
- **Mock External Dependencies**: Use mocks for API calls and external services
- **Test Coverage**: Aim for 80%+ coverage on critical paths
- **Test Isolation**: Each test should be independent and repeatable

### Documentation
- **README Files**: Comprehensive documentation for each major component
- **API Documentation**: Document all public APIs with examples
- **Change Logs**: Maintain CHANGELOG.md with version history
- **Code Comments**: Explain complex algorithms and business logic
- **Type Hints**: Use type hints for better IDE support and documentation

### Deployment
- **Environment Variables**: Use .env files for configuration
- **Dependency Management**: Pin versions in requirements.txt
- **Health Checks**: Implement health check endpoints for services
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Recovery**: Implement graceful degradation and fallback mechanisms

## Anti-Patterns to Avoid

### Don't
- ❌ Hardcode API keys or credentials
- ❌ Use bare except clauses without logging
- ❌ Modify files without model awareness checks
- ❌ Skip error handling in critical operations
- ❌ Use global variables for state management
- ❌ Ignore type hints in public APIs
- ❌ Write methods longer than 50 lines
- ❌ Create circular dependencies between modules
- ❌ Use print() instead of logging
- ❌ Commit sensitive data to version control

### Do
- ✅ Use centralized logging system
- ✅ Implement proper error handling with fallbacks
- ✅ Check model awareness before file modifications
- ✅ Use type hints for better code clarity
- ✅ Keep methods focused on single responsibility
- ✅ Use environment variables for configuration
- ✅ Write comprehensive docstrings
- ✅ Follow the established patterns in the codebase
- ✅ Test critical functionality
- ✅ Document breaking changes

## Code Review Checklist

### Before Committing
- [ ] Model awareness check passed for file modifications
- [ ] Centralized logging implemented
- [ ] Error handling with proper logging
- [ ] Type hints added to public methods
- [ ] Docstrings updated for new/modified functions
- [ ] No hardcoded credentials or API keys
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated (README, comments)
- [ ] Code follows project naming conventions
- [ ] No debug print statements left in code

### Architecture Compliance
- [ ] Follows modular design principles
- [ ] Uses event system for inter-component communication
- [ ] Implements proper async patterns for I/O
- [ ] Respects separation of concerns
- [ ] Maintains backward compatibility
- [ ] No circular dependencies introduced
- [ ] Proper resource cleanup in finally blocks
- [ ] Thread-safe operations for GUI updates

### Quality Assurance
- [ ] Code is readable and self-documenting
- [ ] Complex logic has explanatory comments
- [ ] No code duplication (DRY principle)
- [ ] Performance considerations addressed
- [ ] Security best practices followed
- [ ] Accessibility features maintained
- [ ] Error messages are user-friendly
- [ ] Logging provides sufficient debugging information
