# Ollama Manager - Usage Guide

## Overview

The `OllamaManager` class provides a comprehensive interface for managing Ollama models in the ULTRON Agent system. It handles model pulling, switching, and monitoring operations.

## Features

- **Model Management**: Pull, remove, and switch between models
- **Connection Monitoring**: Check Ollama service availability
- **Status Tracking**: Monitor running models and their states
- **Logging**: Comprehensive logging using the centralized ULTRON logger
- **Error Handling**: Robust error handling with timeout management

## Installation

The `ollama_manager.py` module is included in the ULTRON Agent codebase. No additional installation is required beyond the standard ULTRON dependencies.

## Basic Usage

### Initialize Manager

```python
from ollama_manager import OllamaManager

# Create a new manager instance
manager = OllamaManager()

# Or get the singleton instance
from ollama_manager import get_ollama_manager
manager = get_ollama_manager()
```

### Check Connection

```python
# Check if Ollama service is running
if manager.check_connection():
    print("Ollama is connected and available")
else:
    print("Cannot connect to Ollama service")
```

### Pull a Model

```python
# Pull a model from the Ollama registry
model_name = "llama2:7b"
success = manager.pull_model(model_name)

if success:
    print(f"Successfully pulled {model_name}")
else:
    print(f"Failed to pull {model_name}")
```

### Switch Models

```python
# Switch to a different model
model_name = "codellama:13b"
success = manager.switch_model(model_name)

if success:
    print(f"Switched to {model_name}")
else:
    print(f"Failed to switch to {model_name}")
```

### Get Status

```python
# Get comprehensive status information
status = manager.get_status()

print(f"Connected: {status['connected']}")
print(f"Current Model: {status['current_model']}")
print(f"Available Models: {status['available_models']}")
print(f"Model Count: {status['model_count']}")
print(f"Running Models: {status['running_models']}")
```

### List Running Models

```python
# Get list of currently running models
running_models = manager.list_running_models()

for model in running_models:
    print(f"Model: {model['name']}, ID: {model['id']}, Size: {model['size']}")
```

### Remove a Model

```python
# Remove a model from local storage
model_name = "llama2:7b"
success = manager.remove_model(model_name)

if success:
    print(f"Successfully removed {model_name}")
else:
    print(f"Failed to remove {model_name}")
```

### Get Model Information

```python
# Get detailed information about a model
model_name = "llama2:7b"
info = manager.show_model_info(model_name)

if info:
    print(info)
else:
    print(f"Could not get information for {model_name}")
```

### Test Model

```python
# Test if a model is working properly
model_name = "llama2:7b"
is_working = manager.test_model(model_name)

if is_working:
    print(f"{model_name} is working correctly")
else:
    print(f"{model_name} is not responding")
```

## Advanced Usage

### Custom Configuration

```python
from ollama_manager import OllamaManager

# Create manager with custom configuration
# Note: The config object should have a 'data' attribute with model settings
class CustomConfig:
    def __init__(self):
        self.data = {
            'llm_model': 'qwen2.5:latest'
        }

config = CustomConfig()
manager = OllamaManager(config=config)

# Note: Base URL is currently hardcoded to 'http://127.0.0.1:11434'
# To use a different URL, modify the base_url attribute after initialization
# manager.base_url = 'http://custom-host:11434'
```

### Ensure Default Model

```python
# Ensure a default model is loaded
# Tries in order: qwen2.5vl:latest, qwen2.5vl, qwen2.5:latest, qwen2.5
success = manager.ensure_default_model()

if success:
    print("Default model is ready")
else:
    print("Failed to load default model")
```

### Get Model Sizes

```python
# Get size information for all installed models
model_sizes = manager.get_model_sizes()

for model_name, info in model_sizes.items():
    print(f"{model_name}: {info['size']} (Modified: {info['modified']})")
```

## Error Handling

The OllamaManager includes comprehensive error handling:

- **Connection Errors**: Returns `False` when Ollama service is unavailable
- **Timeout Handling**: 10-minute timeout for model pulls, 30-second timeout for other operations
- **Logging**: All errors are logged using the centralized ULTRON logger

Example with error handling:

```python
try:
    manager = OllamaManager()
    
    if not manager.check_connection():
        print("Error: Ollama service is not running")
        exit(1)
    
    # Pull a model with timeout handling
    success = manager.pull_model("llama2:7b")
    
    if not success:
        print("Error: Failed to pull model")
        # Check logs for details
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

All operations are logged using the ULTRON centralized logging system:

- Component logs: `logs/ollama_manager.log`
- Master logs: `logs/ultron_master.log`

Example log entries:
- Model pull operations
- Connection status changes
- Model switching events
- Error conditions

Note: The logger uses the standard Python logging framework via `get_logger('ollama_manager')`

## Integration with ULTRON Agent

The OllamaManager integrates seamlessly with the ULTRON Agent system:

1. **Agent Core**: Can be used by `agent_core.py` for model management
2. **Tools**: Can be wrapped as a tool in the `tools/` directory
3. **API**: Can be exposed via the REST API for remote management
4. **GUI**: Status and operations can be displayed in the GUI

Example integration:

```python
# In agent_core.py or other components
from ollama_manager import get_ollama_manager

class UltronAgent:
    def __init__(self):
        self.ollama_manager = get_ollama_manager()
        
    def ensure_model_ready(self):
        return self.ollama_manager.ensure_default_model()
```

## Testing

Comprehensive tests are available in `tests/test_ollama_manager.py`:

```bash
# Run tests
pytest tests/test_ollama_manager.py -v

# Run with coverage
pytest tests/test_ollama_manager.py --cov=ollama_manager
```

## Requirements

- Python 3.10+
- Ollama service running on localhost:11434
- requests library
- subprocess module (standard library)

## Troubleshooting

### Ollama Service Not Running

```python
if not manager.check_connection():
    print("Start Ollama service with: ollama serve")
```

### Model Pull Timeout

Large models may take longer than the default 10-minute timeout. The timeout is configurable in the code if needed.

### Model Not Available

```python
# Check available models
status = manager.get_status()
available = status['available_models']

if 'llama2:7b' not in available:
    print("Model not available locally, pulling...")
    manager.pull_model('llama2:7b')
```

## API Reference

### OllamaManager Class

#### Methods

- `__init__(config=None)`: Initialize the manager
- `check_connection()`: Check Ollama service availability
- `pull_model(model_name)`: Pull a model from registry
- `switch_model(model_name)`: Switch to a different model
- `remove_model(model_name)`: Remove a model from local storage
- `list_running_models()`: Get list of running models
- `show_model_info(model_name)`: Get detailed model information
- `test_model(model_name=None)`: Test if a model is working
- `get_status()`: Get comprehensive status information
- `get_model_sizes()`: Get size information for all models
- `ensure_default_model()`: Ensure default model is loaded

### Module Functions

- `get_ollama_manager(config=None)`: Get singleton manager instance
- `test_ollama_connection()`: Quick connection test

## Contributing

When contributing to the OllamaManager:

1. Follow the ULTRON Agent coding standards
2. Use the centralized logging system (`utils.ultron_logger`)
3. Add tests for new functionality in `tests/test_ollama_manager.py`
4. Update this documentation for new features

## License

Part of the ULTRON Agent 3.0 system.
