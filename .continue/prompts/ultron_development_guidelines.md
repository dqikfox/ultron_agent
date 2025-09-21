# ULTRON Agent Development Guidelines

You are an expert AI assistant helping develop ULTRON Agent 3.0, a sophisticated AI assistant system with the following key components:

## Core Architecture
- **Agent Core**: Central integration hub managing all components
- **Brain Module**: AI reasoning engine with multi-model support (Mistral Codestral, Claude, Gemini, Ollama)
- **Voice System**: Multi-engine voice with ElevenLabs TTS and comprehensive fallbacks
- **GUI System**: Enhanced ULTRON Pokédex GUI (EUP GUI) with real-time monitoring
- **Tool Ecosystem**: Modular plugin system with dynamic discovery
- **Event System**: Pub/sub communication between components
- **Model Awareness**: System that coordinates file modifications between AI models
- **Centralized Logging**: Structured JSON logging with component-specific files

## Development Patterns

### 1. Model Awareness Integration
Before ANY file modification, check with model awareness:
```python
from utils.model_awareness import should_modify_file, check_file_context
context = check_file_context(file_path)
should_proceed, reason, _ = should_modify_file(file_path, "edit", "ai_model")
```

### 2. Centralized Logging
All components must use centralized logging:
```python
from utils.ultron_logger import log_info, log_error, log_ai_decision, log_file_operation
log_info("component", "message", **kwargs)
log_ai_decision("component", "decision", ai_model="model", confidence_score=0.9)
```

### 3. Error Handling with Voice Feedback
Implement comprehensive error handling:
```python
try:
    # operation
    log_info("component", "operation completed")
except Exception as e:
    log_error("component", f"operation failed: {e}")
    # Provide voice feedback if applicable
    voice_manager.speak(f"Error: {str(e)}")
```

### 4. Event System Integration
Use the event system for cross-component communication:
```python
# Subscribe to events
self.event_system.subscribe("command_complete", self.handle_completion)

# Emit events
await self.event_system.emit("command_start", {"command": cmd})
```

### 5. Voice Accessibility
Ensure all features support voice control:
- Hands-free operation
- Clear spoken feedback
- Keyboard navigation preservation
- Error announcements

## Code Quality Standards

### Type Hints
```python
from typing import Dict, List, Optional, Tuple

def process_command(self, command: str) -> Dict[str, Any]:
    """Process a voice command with proper typing."""
```

### Async/Await Patterns
```python
async def handle_request(self, request: Request) -> Response:
    """Handle async requests for responsiveness."""
    result = await self.process_async(request)
    return Response(result)
```

### Thread Safety
```python
import threading
_lock = threading.Lock()

def thread_safe_operation(self):
    with _lock:
        # Critical section
        pass
```

## Testing Requirements

### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

def test_component_functionality():
    """Test core functionality with mocks."""
    with patch('module.external_service') as mock_service:
        mock_service.return_value = expected_result
        result = component.function()
        assert result == expected_result
```

### Integration Tests
```python
def test_api_endpoints():
    """Test API integration points."""
    response = client.post('/api/endpoint', json=payload)
    assert response.status_code == 200
    assert response.json() == expected_response
```

## Documentation Standards

### Component Documentation
```python
class ComponentName:
    """
    Brief description of component purpose.

    Architecture:
    - Key responsibilities
    - Integration points
    - Dependencies

    Configuration:
    - Required settings
    - Optional parameters
    - Environment variables

    Usage:
    - Basic usage examples
    - Advanced features
    - Error handling
    """
```

### API Documentation
```python
@app.post("/api/endpoint")
async def endpoint_handler(request: Request):
    """
    Handle endpoint requests.

    Args:
        request: Incoming request with parameters

    Returns:
        Response: Processed result

    Raises:
        HTTPException: On processing errors
    """
```

## Security Considerations

### Input Validation
```python
from pydantic import BaseModel, validator

class SecureInput(BaseModel):
    command: str

    @validator('command')
    def validate_command(cls, v):
        if not v or len(v) > 1000:
            raise ValueError('Invalid command')
        return v
```

### API Key Management
```python
# Use environment variables for sensitive data
api_key = os.getenv('SERVICE_API_KEY')
if not api_key:
    raise ValueError('API key not configured')
```

## Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_operation(self, param: str) -> Result:
    """Cache expensive operations."""
    return self.expensive_computation(param)
```

### Async Processing
```python
import asyncio

async def process_batch(self, items: List[Item]) -> List[Result]:
    """Process items concurrently."""
    tasks = [self.process_item(item) for item in items]
    return await asyncio.gather(*tasks)
```

## Deployment Considerations

### Configuration Management
```json
{
  "service": {
    "host": "localhost",
    "port": 8000,
    "debug": false
  },
  "models": {
    "primary": "codestral-latest",
    "fallback": "llama3.2:latest"
  },
  "voice": {
    "primary": "elevenlabs",
    "fallback": "pyttsx3"
  }
}
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "ollama": await check_ollama_status(),
            "voice": await check_voice_status(),
            "database": await check_database_status()
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Troubleshooting

### Common Issues
1. **Model Awareness Blocks**: Check file context and recent modifications
2. **Voice Not Working**: Verify ElevenLabs API key and fallback chain
3. **Event System Issues**: Check event subscriptions and emissions
4. **Performance Problems**: Monitor async operations and caching
5. **Integration Failures**: Verify component initialization order

### Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for specific components
logger = logging.getLogger('ultron.component')
logger.setLevel(logging.DEBUG)
```

## Best Practices

1. **Always check model awareness** before file modifications
2. **Use centralized logging** for all operations
3. **Implement comprehensive error handling** with user feedback
4. **Follow async patterns** for I/O operations
5. **Add type hints** for better code maintainability
6. **Write tests** for all new functionality
7. **Document thoroughly** for future maintainers
8. **Consider accessibility** in all user interactions
9. **Monitor performance** and optimize bottlenecks
10. **Keep security** as a primary concern

Remember: ULTRON Agent is a production-ready system that must maintain high reliability, accessibility, and performance standards.
