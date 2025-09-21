# Amazon Q Writing Guidelines for ULTRON Agent 3.0

## Code Writing Standards

### Minimal Code Principle
- Write only the ABSOLUTE MINIMAL amount of code needed to address the requirement correctly
- Avoid verbose implementations and any code that doesn't directly contribute to the solution
- Focus on essential functionality without unnecessary complexity

### Type Safety & Documentation
- Use type hints for all public functions and methods
- Include comprehensive docstrings for complex logic
- Add inline comments for non-obvious code sections

### Error Handling
- Include proper exception handling with logging
- Use centralized logging system (`utils.ultron_logger`)
- Provide user-friendly error messages

### Async Patterns
- Use async/await for I/O operations and long-running tasks
- Implement proper timeout handling (30-second default for network operations)
- Ensure proper cleanup on shutdown signals

### Security Best Practices
- Sanitize all user inputs
- Validate file paths and parameters
- Use environment variables for sensitive data
- Implement secure API key handling

## File Modification Protocol

### Before Writing Any Code
1. **Check Model Awareness**:
   ```python
   from utils.model_awareness import should_modify_file, check_file_context
   context = check_file_context(file_path)
   should_proceed, reason, _ = should_modify_file(file_path, "edit", "amazon_q")
   ```

2. **Log the Decision**:
   ```python
   from utils.ultron_logger import log_ai_decision
   log_ai_decision("amazon_q", f"Writing code for {file_path}", ai_model="amazon_q")
   ```

### Code Structure Requirements
- **Imports**: Group standard library, third-party, and local imports
- **Classes**: Use clear, descriptive names with proper inheritance
- **Functions**: Keep functions focused on single responsibility
- **Variables**: Use descriptive names, avoid abbreviations

### Testing Requirements
- Include unit tests for new functionality
- Mock external dependencies in tests
- Test error conditions and edge cases
- Ensure tests are isolated and repeatable

## Component-Specific Guidelines

### Tool Development
```python
from utils.ultron_logger import log_info, log_error
from tools.base import Tool

class MinimalTool(Tool):
    name = "minimal_tool"
    description = "Minimal tool implementation"

    def match(self, command: str) -> bool:
        return "minimal" in command.lower()

    def execute(self, **kwargs):
        try:
            # Minimal implementation
            return "Success"
        except Exception as e:
            log_error("minimal_tool", f"Error: {str(e)}")
            return f"Error: {str(e)}"
```

### GUI Components
- Only modify EUP GUI (`gui/ultron_enhanced/web/index.html`)
- Maintain voice control and keyboard navigation
- Use minimal JavaScript for functionality
- Ensure responsive design principles

### API Endpoints
```python
from fastapi import APIRouter
from utils.ultron_logger import log_info

router = APIRouter()

@router.post("/minimal")
async def minimal_endpoint(data: dict):
    log_info("api", "Minimal endpoint called")
    # Minimal processing
    return {"status": "success"}
```

### Voice Integration
```python
def minimal_voice_response(text: str):
    """Minimal voice response implementation"""
    from voice_manager import get_voice_manager
    voice_manager = get_voice_manager()
    return voice_manager.speak(text, async_mode=True)
```

## Quality Checklist

### Before Committing Code
- [ ] Minimal implementation achieved
- [ ] Model awareness check passed
- [ ] Centralized logging implemented
- [ ] Error handling included
- [ ] Type hints added
- [ ] Documentation updated
- [ ] Tests written (if applicable)

### Code Review Points
- [ ] No unnecessary complexity
- [ ] Proper error handling
- [ ] Appropriate logging levels
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] Integration points tested

## Common Patterns

### Configuration Loading
```python
def load_minimal_config():
    """Load minimal configuration"""
    import json
    try:
        with open("ultron_config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        log_error("config", f"Config load failed: {str(e)}")
        return {}
```

### Event Handling
```python
def handle_minimal_event(event_data):
    """Minimal event handler"""
    log_info("event", f"Handling: {event_data.get('type', 'unknown')}")
    # Minimal processing
    return True
```

### Database Operations
```python
async def minimal_db_operation(query: str):
    """Minimal database operation"""
    try:
        # Minimal query execution
        return {"result": "success"}
    except Exception as e:
        log_error("db", f"Query failed: {str(e)}")
        return {"error": str(e)}
```

## Performance Guidelines

### Memory Management
- Use generators for large data sets
- Clean up resources in finally blocks
- Avoid memory leaks in long-running processes

### CPU Optimization
- Use appropriate data structures
- Minimize nested loops
- Cache frequently accessed data

### Network Efficiency
- Implement connection pooling
- Use async operations for I/O
- Handle timeouts gracefully

## Debugging Support

### Logging Levels
- `log_info()`: General information
- `log_error()`: Error conditions
- `log_ai_decision()`: AI decision points
- `log_file_operation()`: File operations

### Debug Utilities
```python
def debug_minimal_state():
    """Debug current state with minimal output"""
    log_info("debug", "Current state check")
    # Minimal state information
    return {"status": "ok"}
```

---

**Remember**: Write the minimal code that solves the problem correctly. Every line should have a clear purpose and contribute directly to the solution.