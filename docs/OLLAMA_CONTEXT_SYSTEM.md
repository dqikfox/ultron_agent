# Ollama Model Context System

## Overview

The **Ollama Context Provider** is a universal system that gives all Ollama models access to the full functionality of the ultron_agent platform. This includes memory, tools, capabilities, and system state - all injected dynamically into model prompts regardless of which Ollama model is active.

## Key Features

### 1. **Model-Agnostic Design**
- Works with **ANY** Ollama model (llama3.1, llava:7b, qwen3-coder, deepseek-r1, etc.)
- No model-specific code required
- Automatic context adaptation based on available components

### 2. **Comprehensive Context Injection**
The system provides models with:
- **Memory**: Short-term conversation history and long-term knowledge
- **Tools**: Available tools and their schemas for function calling
- **Capabilities**: Agent capabilities and system status
- **Configuration**: System settings and preferences

### 3. **Configurable Context Sections**
Fine-grained control over what context is included:
```json
{
  "ollama_include_memory": true,
  "ollama_include_tools": true,
  "ollama_include_capabilities": true,
  "ollama_max_memory_items": 10,
  "ollama_max_tool_schemas": 20,
  "ollama_enable_function_calling": false
}
```

### 4. **Performance Optimized**
- Context limits to prevent overwhelming models
- Efficient memory retrieval
- Lazy loading of context sections

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    Ultron Agent                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────┐  ┌────────────────┐     │
│  │   Memory    │  │  Tools   │  │  Configuration │     │
│  └──────┬──────┘  └────┬─────┘  └───────┬────────┘     │
│         │              │                 │              │
│         └──────────────┼─────────────────┘              │
│                        │                                │
│              ┌─────────▼─────────┐                      │
│              │ Context Provider  │                      │
│              │  (Universal)      │                      │
│              └─────────┬─────────┘                      │
│                        │                                │
│              ┌─────────▼─────────┐                      │
│              │   Enhanced Prompt │                      │
│              └─────────┬─────────┘                      │
│                        │                                │
│              ┌─────────▼─────────┐                      │
│              │   Ollama Model    │                      │
│              │  (Any Model)      │                      │
│              └───────────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### Context Provider Class

The `OllamaContextProvider` class is the heart of the system:

```python
class OllamaContextProvider:
    def __init__(self, memory=None, tools=None, config=None):
        """Initialize with agent components"""
        
    def build_enhanced_prompt(self, user_prompt: str, model_name: str = None) -> str:
        """Build enhanced prompt with full context"""
        
    def get_tools_as_function_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas for function calling"""
        
    def update_memory(self, new_memory):
        """Update memory reference"""
        
    def update_tools(self, new_tools: Dict[str, Any]):
        """Update tools dictionary"""
        
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context statistics"""
```

## Usage

### Basic Setup

The context provider is automatically initialized when the brain is created:

```python
from brain import UltronBrain

# Create brain with memory, tools, and config
brain = UltronBrain(config, tools, memory)

# The brain.ollama_context is now available
# It will automatically inject context into all Ollama calls
```

### Sending Queries

All queries through `brain.direct_chat()` automatically get enhanced context:

```python
# User query
response = await brain.direct_chat("What tools do you have access to?")

# The model receives:
# - System capabilities
# - Memory context
# - List of available tools
# - The user query
```

### Dynamic Updates

Update context when components change:

```python
# Update when new tools are loaded
brain.update_context_provider(tools=new_tools)

# Update when memory changes
brain.update_context_provider(memory=new_memory)

# Update configuration
brain.update_context_provider(config=new_config)
```

### Getting Context Statistics

Monitor what context is available:

```python
stats = brain.get_ollama_context_stats()
print(stats)
# Output:
# {
#   'timestamp': '2025-10-24T05:30:00',
#   'memory_available': True,
#   'tools_count': 15,
#   'short_term_memory_count': 5,
#   'long_term_memory_count': 100,
#   'context_sections_enabled': {
#       'memory': True,
#       'tools': True,
#       'capabilities': True
#   }
# }
```

## Configuration Options

### Core Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ollama_include_memory` | bool | `true` | Include memory context |
| `ollama_include_tools` | bool | `true` | Include tools context |
| `ollama_include_capabilities` | bool | `true` | Include capabilities |
| `ollama_max_memory_items` | int | `10` | Max recent memory items |
| `ollama_max_tool_schemas` | int | `20` | Max tool schemas |
| `ollama_enable_function_calling` | bool | `false` | Enable function calling |

### Example Configuration

In `ultron_config.json`:

```json
{
  "llm_model": "llava:7b",
  "ollama_base_url": "http://localhost:11434",
  
  "ollama_include_memory": true,
  "ollama_include_tools": true,
  "ollama_include_capabilities": true,
  "ollama_max_memory_items": 15,
  "ollama_max_tool_schemas": 25,
  "ollama_enable_function_calling": false
}
```

## Enhanced Prompt Structure

The system builds prompts with the following structure:

```
System Capabilities:
- Memory System: Available
- Tool Access: 15 tools available
- Reasoning: Advanced problem-solving
- [Other capabilities...]

Recent Conversation Context:
1. User asked about weather
2. Assistant provided forecast
3. [More recent items...]

Available Tools and Functions:
- WebScrapingTool: Extract data from web pages
- FileSystemTool: File operations
- DatabaseTool: Database queries
- [More tools...]

---

User Query: [Original user query]

Response:
```

## Function Calling Support

For models that support function calling, the system can provide tool schemas:

```python
# Get function schemas
schemas = brain.ollama_context.get_tools_as_function_schemas()

# Each schema follows OpenAI format:
# {
#   "name": "web_scraping_tool",
#   "description": "Extract data from web pages",
#   "parameters": {
#     "type": "object",
#     "properties": {
#       "url": {"type": "string", "description": "URL to scrape"}
#     },
#     "required": ["url"]
#   }
# }
```

## Memory Integration

### Short-Term Memory

Recent conversation items (configurable limit):
```python
# Automatically includes recent conversation
# Limited by ollama_max_memory_items config
```

### Long-Term Memory

Relevant knowledge from long-term storage:
```python
# Includes recent long-term memories
# Formatted for easy model consumption
```

### System Prompts

System-level context from memory:
```python
if hasattr(memory, 'get_system_prompt'):
    system_prompt = memory.get_system_prompt()
    # Included at top of context
```

## Tool Integration

### Automatic Tool Discovery

All loaded tools are automatically available:
```python
# Tools from tools/ directory are auto-discovered
# Context provider gets updated after tools load
```

### Tool Schema Format

Tools can provide schemas for the model:
```python
class MyTool:
    def schema(self):
        return {
            "name": "my_tool",
            "description": "Does something useful",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            }
        }
```

## Performance Considerations

### Context Limits

To prevent overwhelming models:
- Memory items limited (default: 10)
- Tool schemas limited (default: 20)
- Text truncation for long items (200 chars)

### Lazy Loading

Context sections only built when enabled:
```python
# Disabled sections don't add overhead
if self.include_memory and self.memory:
    # Only build if enabled and available
```

### Caching

Future enhancement: Cache generated contexts for repeated queries.

## Testing

Comprehensive test suite included:

```bash
# Run tests
python -m pytest tests/test_ollama_context_provider.py -v

# All 17 tests should pass
```

Test coverage includes:
- Initialization with/without components
- Prompt building with various contexts
- Context limits
- Error handling
- Multiple model compatibility

## Examples

### Example 1: Basic Query

```python
# User: "What can you do?"
# Model receives full context about capabilities and tools
response = await brain.direct_chat("What can you do?")
```

### Example 2: Conversation with Memory

```python
# Previous: "My name is John"
# Current: "What's my name?"
# Model receives conversation history including previous name mention
response = await brain.direct_chat("What's my name?")
```

### Example 3: Tool-Aware Response

```python
# User: "Search the web for Python tutorials"
# Model receives context about WebScrapingTool availability
response = await brain.direct_chat("Search the web for Python tutorials")
# Response may reference the tool: "I can use the WebScrapingTool to..."
```

## Troubleshooting

### No Context Appearing

Check configuration:
```python
stats = brain.get_ollama_context_stats()
print(stats['context_sections_enabled'])
```

### Too Much Context

Reduce limits:
```json
{
  "ollama_max_memory_items": 5,
  "ollama_max_tool_schemas": 10
}
```

### Memory Not Working

Verify memory system:
```python
if brain.memory:
    print("Memory available")
    print(f"Short-term: {len(brain.memory.retrieve_short_term())}")
```

### Tools Not Showing

Check tools are loaded:
```python
print(f"Tools available: {len(brain.tools)}")
print(f"Tool names: {list(brain.tools.keys())}")
```

## Future Enhancements

1. **Smart Context Selection**: Use AI to select most relevant context
2. **Context Compression**: Summarize large contexts
3. **Model-Specific Optimization**: Tune context for specific model types
4. **Streaming Context**: Stream context for very long prompts
5. **Context Caching**: Cache generated contexts for performance

## API Reference

See the docstrings in `utils/ollama_context_provider.py` for detailed API documentation.

## Contributing

When adding new features to ultron_agent that should be accessible to Ollama models:

1. Add the feature to the appropriate system (memory, tools, etc.)
2. The context provider will automatically expose it
3. Add tests to verify the feature is accessible
4. Update this documentation

## Summary

The Ollama Context Provider is a **universal system** that works with **any Ollama model** to provide full access to ultron_agent's capabilities. It's:

- ✅ **Model-agnostic**: Works with all Ollama models
- ✅ **Automatic**: No manual prompt engineering required  
- ✅ **Configurable**: Fine-tune what context is included
- ✅ **Performant**: Optimized with limits and lazy loading
- ✅ **Extensible**: Easy to add new context sources
- ✅ **Well-tested**: Comprehensive test coverage

This enables all your Ollama models to leverage the full power of the ultron_agent platform! 🚀
