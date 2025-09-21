# Ultron Agent - Quick Reference for Continue Extension

## 🎯 Current Development Context

### Active Files & Key Functions
```python
# automation.py - Enhanced PyAutoGUI system
def run_command(command: str) -> str:
    """Main automation command parser with 20+ categories"""

def move_mouse_with_easing(coords: str, easing: str) -> str:
    """Move mouse with 25+ easing functions"""

def take_screenshot_region(coords: str) -> str:
    """Capture specific screen region"""

def get_pixel_color(coords: str) -> str:
    """Analyze pixel RGB values"""

def write_text_with_interval(text: str, interval: float) -> str:
    """Type text with custom speed"""

# app.py - FastAPI backend
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time communication with frontend"""

@app.post("/voice-command")
async def process_voice_command(command: VoiceCommand):
    """Process voice input and return response"""

# ollama_client.py - AI model interface
async def stream_chat(messages: List[dict]) -> AsyncIterator[str]:
    """Stream responses from Qwen2.5-VL model"""
```

### Recent Code Patterns (August 2025)
```python
# Enhanced error handling with logging
try:
    result = automation_function(params)
    logger.info(f"Automation success: {result}")
    return result
except Exception as e:
    logger.error(f"Automation error: {e}")
    return f"Failed: {str(e)}"

# Async voice processing
async def process_voice_input(audio_data: bytes) -> str:
    result = await voice_recognition.process(audio_data)
    return await ai_model.respond(result)

# Safety-first automation
def safe_automation(action: str) -> str:
    if not PYAUTOGUI_AVAILABLE:
        return "Automation not available"
    
    try:
        # Validation
        validate_input(action)
        # Execution with safety
        return execute_with_safety(action)
    except Exception as e:
        return handle_error(e)
```

## 🔧 Development Commands

### Testing
```bash
# Run automation tests
python test_enhanced_automation.py

# Test Continue configuration  
python test_continue_config.py

# Run specific test categories
pytest tests/ -m automation
pytest tests/ -m voice
```

### Model Management
```bash
# Check Ollama status
ollama list

# Start/restart model
ollama run qwen2.5vl:latest

# Check model performance
curl http://localhost:11434/api/generate
```

### Common Development Tasks
```python
# Add new automation command
# 1. Update run_command() parser
# 2. Implement function
# 3. Add to help system
# 4. Write tests

# Integrate new AI feature
# 1. Update ollama_client.py
# 2. Modify brain.py logic
# 3. Test with frontend
# 4. Update configuration
```

## 🎯 Code Quality Standards

### Type Hints (Required)
```python
from typing import Dict, List, Optional, Union, AsyncIterator

def process_automation(
    command: str, 
    params: Optional[Dict[str, Any]] = None
) -> Union[str, Dict[str, Any]]:
    """Always include comprehensive type hints"""
```

### Docstring Format
```python
def enhanced_function(param1: str, param2: int) -> str:
    """
    Brief description of function purpose.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        SpecificError: When specific condition occurs
    """
```

### Error Handling Pattern
```python
import logging

logger = logging.getLogger(__name__)

def robust_function(input_data: str) -> str:
    try:
        # Validate input
        if not input_data:
            raise ValueError("Input cannot be empty")
        
        # Process
        result = process_data(input_data)
        
        # Log success
        logger.info(f"Function completed: {result[:50]}...")
        return result
        
    except SpecificError as e:
        logger.error(f"Specific error in function: {e}")
        return f"Specific error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in function: {e}")
        return f"Unexpected error: {str(e)}"
```

## 🚀 Performance Guidelines

### Async Patterns
```python
import asyncio
from typing import List

# Use async for I/O operations
async def process_multiple_commands(commands: List[str]) -> List[str]:
    """Process commands concurrently"""
    tasks = [process_single_command(cmd) for cmd in commands]
    return await asyncio.gather(*tasks)

# Sync wrapper when needed
def sync_process_commands(commands: List[str]) -> List[str]:
    """Sync wrapper for async function"""
    return asyncio.run(process_multiple_commands(commands))
```

### Memory Management
```python
# Clean up resources
def process_large_data():
    try:
        data = load_large_dataset()
        result = process_data(data)
        return result
    finally:
        # Explicit cleanup
        del data
        gc.collect()
```

## 🛡️ Security Best Practices

### Input Validation
```python
import re

def validate_coordinates(coords: str) -> bool:
    """Validate coordinate input"""
    pattern = r'^\d+,\s*\d+$'
    return bool(re.match(pattern, coords))

def sanitize_command(command: str) -> str:
    """Remove potentially dangerous characters"""
    # Remove special characters except allowed ones
    return re.sub(r'[^\w\s\-.,()]', '', command)
```

### Safe Automation
```python
def safe_automation_wrapper(func):
    """Decorator for automation safety"""
    def wrapper(*args, **kwargs):
        if not pyautogui_available():
            return "Automation not available"
        
        try:
            # Enable safety
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            
            return func(*args, **kwargs)
        except pyautogui.FailSafeException:
            return "Automation stopped by failsafe"
        except Exception as e:
            return f"Automation error: {str(e)}"
    
    return wrapper
```

## 📋 Current Issues & Solutions

### Known Issues
1. **Voice Latency**: ~1-2 second delay in processing
   - **Solution**: Implement async audio pipeline
   - **Status**: In development

2. **Model Loading Time**: Initial model load takes 10-15 seconds
   - **Solution**: Implement model preloading
   - **Status**: Planned

3. **Cross-platform Compatibility**: Some automation features Windows-specific
   - **Solution**: Add OS detection and platform-specific handlers
   - **Status**: In progress

### Performance Optimizations
```python
# Cache frequently used data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_screen_info() -> tuple:
    """Cache screen information"""
    return pyautogui.size()

# Use connection pooling for AI requests
import aiohttp

class OptimizedOllamaClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=10)
        )
```

## 🎯 Next Development Steps

### Priority 1: Performance
- [ ] Implement async voice pipeline
- [ ] Optimize model loading
- [ ] Add request caching
- [ ] Performance monitoring dashboard

### Priority 2: Features  
- [ ] MCP server integration
- [ ] Advanced automation workflows
- [ ] Enhanced error recovery
- [ ] Cross-platform compatibility

### Priority 3: Quality
- [ ] Comprehensive test coverage
- [ ] Documentation updates
- [ ] Code review automation
- [ ] Performance benchmarking

This reference should help your Qwen2.5-Coder model provide contextually accurate assistance for the Ultron Agent project!
