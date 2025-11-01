# Development Guidelines - ULTRON Agent 3.0

## Code Quality Standards

### Python Code Formatting
- **Docstrings**: Triple-quoted strings at module/class/function level with clear descriptions
- **Type Hints**: Not consistently used but recommended for public APIs
- **Line Length**: Generally under 120 characters, flexible for readability
- **Imports**: Grouped by standard library, third-party, and local imports
- **String Formatting**: Mix of f-strings and format() method, prefer f-strings for new code

### JavaScript/TypeScript Formatting
- **Component Structure**: React functional components with TypeScript
- **Naming**: PascalCase for components, camelCase for functions/variables
- **Props**: Explicit type definitions using TypeScript interfaces
- **Exports**: Named exports at end of file for component libraries
- **Styling**: Tailwind CSS utility classes with cn() helper for conditional classes

### Naming Conventions
- **Python Classes**: PascalCase (e.g., `UltronBrain`, `MobileWebInterfaceTool`)
- **Python Functions**: snake_case (e.g., `run_command`, `take_screenshot`)
- **Python Constants**: UPPER_SNAKE_CASE (e.g., `PYAUTOGUI_AVAILABLE`, `SIDEBAR_WIDTH`)
- **TypeScript Components**: PascalCase (e.g., `SidebarProvider`, `SidebarMenuButton`)
- **TypeScript Hooks**: camelCase with 'use' prefix (e.g., `useSidebar`, `useIsMobile`)

## Structural Conventions

### Python Module Structure
1. Module docstring with purpose description
2. Standard library imports
3. Third-party imports
4. Local/project imports
5. Constants and configuration
6. Helper functions
7. Main classes
8. Utility functions
9. Main execution block (if __name__ == "__main__")

### Error Handling Patterns
```python
# Pattern 1: Try-except with logging
try:
    # Operation
    result = perform_operation()
    log_info("component", "Operation successful")
    return result
except Exception as e:
    log_error("component", f"Operation failed: {sanitize_log_input(str(e))}")
    return f"Error: {sanitize_html_output(str(e))}"

# Pattern 2: Availability checks with fallbacks
if not DEPENDENCY_AVAILABLE:
    return "Feature not available - dependency not installed"

# Pattern 3: Graceful degradation
try:
    enhanced_result = use_enhanced_feature()
except Exception as e:
    warning(f"Enhanced feature failed: {e}")
    enhanced_result = use_fallback_feature()
```

### Async/Await Patterns
```python
# Pattern 1: Async function with progress callback
async def process_task(data, progress_callback=None):
    if progress_callback:
        progress_callback(10, "Starting...")
    
    result = await async_operation(data)
    
    if progress_callback:
        progress_callback(100, "Complete")
    
    return result

# Pattern 2: Sync wrapper for async code
def sync_wrapper(message):
    loop = new_event_loop()
    set_event_loop(loop)
    try:
        return loop.run_until_complete(async_function(message))
    finally:
        loop.close()
```

## Semantic Patterns

### Tool Development Pattern
All tools follow a standardized interface:
```python
class ExampleTool(ToolInterface):
    name = "Tool Name"
    description = "Tool description"
    
    def __init__(self, config=None, memory=None):
        self.config = config
        self.memory = memory
    
    def match(self, command: str) -> bool:
        """Check if command matches this tool"""
        return "keyword" in command.lower()
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute the tool operation"""
        try:
            # Implementation
            return "Success message"
        except Exception as e:
            log_error("tool_name", f"Error: {e}")
            return f"Error: {str(e)}"
    
    @classmethod
    def schema(cls):
        return {
            "name": cls.name,
            "description": cls.description,
            "parameters": {}
        }
```

### Logging Pattern
```python
# Import centralized logger
from utils.ultron_logger import log_info, log_error, log_ai_decision

# Component-specific logging
log_info("component_name", "Information message")
log_error("component_name", f"Error: {sanitize_log_input(error_msg)}")

# AI decision logging
log_ai_decision(
    "component_name",
    "Decision description",
    ai_model="model_name",
    confidence_score=0.85
)
```

### Configuration Access Pattern
```python
# Pattern 1: Dictionary-style access with defaults
value = self.config.get("key", "default_value")

# Pattern 2: Attribute access with fallback
try:
    value = self.config.key
except AttributeError:
    value = "default_value"

# Pattern 3: Environment variable override
api_key = self.config.get("api_key", "USE_ENV_API_KEY")
if api_key.startswith("USE_ENV_"):
    api_key = os.getenv(api_key[8:])
```

### Flask Route Pattern
```python
@app.route('/api/endpoint', methods=['POST'])
def endpoint_handler():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'required_field' not in data:
            return jsonify({'error': 'Invalid input'}), 400
        
        # Process request
        result = process_data(data)
        
        # Return response
        return jsonify({
            'status': 'success',
            'result': result,
            'timestamp': time.time()
        })
    
    except Exception as e:
        log_error("api", f"Endpoint failed: {e}")
        return jsonify({'error': str(e)}), 500
```

### React Component Pattern
```typescript
// Pattern 1: Component with context
const Component = React.forwardRef<HTMLElement, Props>(
  ({ prop1, prop2, ...props }, ref) => {
    const context = useContext()
    
    return (
      <Element ref={ref} {...props}>
        {children}
      </Element>
    )
  }
)
Component.displayName = "Component"

// Pattern 2: Component with variants
const componentVariants = cva(
  "base-classes",
  {
    variants: {
      variant: {
        default: "default-classes",
        outline: "outline-classes"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
)
```

## Internal API Usage

### Ollama Integration
```python
# Direct chat with streaming
async def direct_chat(self, prompt: str, progress_callback=None):
    ollama_base_url = self.config.get("ollama_base_url", "http://localhost:11434")
    model = self.config.get("llm_model", "llama3.1")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    async with ClientSession(timeout=ClientTimeout(total=60)) as session:
        async with session.post(f"{ollama_base_url}/api/chat", json=payload) as response:
            reply_parts = []
            async for line in response.content:
                data = json_loads(line.decode('utf-8'))
                content = data.get("message", {}).get("content", "")
                if content:
                    reply_parts.append(content)
            
            return "".join(reply_parts)
```

### Memory System Integration
```python
# Store interaction in memory
if self.memory and hasattr(self.memory, 'add_interaction'):
    self.memory.add_interaction(user_input, response)

# Retrieve context from memory
if self.memory and hasattr(self.memory, 'get_recent_context'):
    context = self.memory.get_recent_context(limit=5)
```

### Event System Usage
```python
# Subscribe to events
self.event_system.subscribe("event_name", self.handler_method)

# Emit events
await self.event_system.emit("event_name", {"data": value})
```

## Code Idioms

### Availability Checks
```python
# Check if optional dependency is available
try:
    import optional_module
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False
    optional_module = None

# Use availability flag
if not FEATURE_AVAILABLE:
    return "Feature not available - install optional_module"
```

### Progress Callbacks
```python
# Consistent progress reporting
if progress_callback:
    progress_callback(percentage, "Status message")

# Error reporting via callback
if progress_callback:
    progress_callback(0, error_message, error=True)
```

### Sanitization Pattern
```python
# Input sanitization for logging
log_error("component", f"Error: {sanitize_log_input(user_input)}")

# Output sanitization for HTML
return f"Result: {sanitize_html_output(result)}"
```

### Path Validation
```python
# Validate file paths before operations
if not validate_file_path(path) or not os.path.exists(path):
    return f"Invalid or inaccessible path: {sanitize_html_output(path)}"
```

## Popular Annotations

### Python Decorators
```python
# Diagnostic wrapper for performance tracking
@diagnostic_wrapper("component_name", track_performance=True)
def method(self, param):
    # Implementation
    pass

# React forwardRef for component refs
Component = React.forwardRef<ElementType, PropsType>(
  (props, ref) => {
    // Implementation
  }
)
```

### Type Annotations
```python
# Python type hints
def function(param: str, optional: Optional[int] = None) -> Dict[str, Any]:
    return {"result": param}

# TypeScript type definitions
type ComponentProps = {
  variant?: "default" | "outline"
  size?: "sm" | "md" | "lg"
  children?: React.ReactNode
}
```

## Best Practices

### Security
- Always sanitize user input before logging: `sanitize_log_input()`
- Always sanitize output before HTML display: `sanitize_html_output()`
- Validate file paths before operations: `validate_file_path()`
- Use environment variables for sensitive data
- Never hardcode API keys or credentials

### Performance
- Use async/await for I/O operations
- Implement progress callbacks for long-running tasks
- Cache frequently accessed data
- Use streaming for large responses
- Implement timeouts for network requests (default 30-60 seconds)

### Error Handling
- Always use try-except blocks for external operations
- Log errors with component context
- Provide user-friendly error messages
- Implement graceful degradation with fallbacks
- Return error messages in consistent format

### Testing
- Include availability checks for optional dependencies
- Provide fallback implementations when features unavailable
- Test with and without optional dependencies
- Validate inputs before processing
- Include edge case handling

### Documentation
- Module-level docstrings explaining purpose
- Function docstrings with parameter descriptions
- Inline comments for complex logic
- Type hints for public APIs
- Examples in docstrings for complex functions

## Code Review Checklist

- [ ] Centralized logging used (`log_info`, `log_error`, `log_ai_decision`)
- [ ] Input sanitization applied (`sanitize_log_input`)
- [ ] Output sanitization applied (`sanitize_html_output`)
- [ ] Error handling with try-except blocks
- [ ] Progress callbacks implemented for long operations
- [ ] Async/await used for I/O operations
- [ ] Type hints added for public functions
- [ ] Docstrings provided for classes and functions
- [ ] Configuration accessed with defaults
- [ ] Environment variables used for sensitive data
- [ ] File paths validated before operations
- [ ] Availability checks for optional dependencies
- [ ] Graceful degradation with fallbacks
- [ ] Consistent naming conventions followed
- [ ] Tool interface pattern followed (for tools)
- [ ] Component pattern followed (for React components)
