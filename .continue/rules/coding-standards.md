# ULTRON Agent Coding Standards

## Python Code Standards

### Type Hints and Documentation
- Use type hints for all public functions and methods
- Include comprehensive docstrings for complex logic
- Add inline comments for non-obvious code sections
- Follow PEP 8 style guidelines

### Error Handling
- Use centralized logging system (`utils.ultron_logger`)
- Implement proper exception handling with context
- Provide user-friendly error messages
- Log errors with appropriate severity levels

### Async Patterns
- Use async/await for I/O operations and long-running tasks
- Implement proper timeout handling (30-second default)
- Ensure proper cleanup on shutdown signals
- Maintain thread safety for GUI operations

## Tool Development Standards

### Interface Requirements
```python
class ToolTemplate:
    name = "tool_name"
    description = "Clear description of tool functionality"
    
    def match(self, command: str) -> bool:
        """Check if command matches this tool's patterns"""
        return "keyword" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute the tool's functionality"""
        try:
            # Implementation with proper error handling
            return "Success result"
        except Exception as e:
            log_error("tool_name", f"Error: {str(e)}")
            return f"Error: {str(e)}"
    
    @staticmethod
    def schema():
        return {
            "name": "tool_name",
            "description": "Tool description",
            "parameters": {}
        }
```

### Logging Requirements
- Use `from utils.ultron_logger import log_info, log_error`
- Log all significant operations and decisions
- Include context information in log messages
- Use appropriate log levels (info, error, warning, debug)

## Integration Standards

### Event System Usage
```python
# Subscribe to events
self.event_system.subscribe("event_name", self.handler)

# Emit events with context
await self.event_system.emit("event_name", {"data": value})
```

### Configuration Access
```python
# Load configuration
from config import load_config
config = load_config()

# Access settings with fallbacks
setting = config.get("setting_name", "default_value")
```

### Voice System Integration
```python
# Use voice manager for TTS
from voice_manager import get_voice_manager
voice_manager = get_voice_manager()
voice_manager.speak("Message text", async_mode=True)
```

## Security Standards

### Input Validation
- Sanitize all user inputs
- Validate file paths and parameters
- Use parameterized queries for database operations
- Implement proper authentication where needed

### API Key Management
- Store sensitive data in environment variables
- Never commit API keys to version control
- Use secure configuration loading mechanisms
- Implement key rotation capabilities where possible

## Performance Standards

### Memory Management
- Use generators for large data sets
- Clean up resources in finally blocks
- Avoid memory leaks in long-running processes
- Monitor memory usage in performance-critical code

### Network Operations
- Implement connection pooling where appropriate
- Use async operations for I/O
- Handle timeouts gracefully
- Implement retry logic with exponential backoff

## Testing Standards

### Unit Testing
- Write tests for all new functionality
- Mock external dependencies
- Test error conditions and edge cases
- Ensure tests are isolated and repeatable

### Integration Testing
- Test component interactions
- Verify event system communication
- Test configuration loading and validation
- Validate API endpoint functionality

## Documentation Standards

### Code Documentation
- Document all public APIs
- Include usage examples in docstrings
- Explain complex algorithms and business logic
- Keep documentation up to date with code changes

### Architecture Documentation
- Document component relationships
- Explain data flow and communication patterns
- Include deployment and configuration guides
- Maintain troubleshooting documentation