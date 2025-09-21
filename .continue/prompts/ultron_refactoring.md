# ULTRON Agent Code Refactoring Prompt

You are refactoring code to follow ULTRON Agent 3.0 development patterns and best practices. Apply these refactoring guidelines:

## Refactoring Priorities

### 1. Model Awareness Integration
**Before:**
```python
def modify_file(self, file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)
```

**After:**
```python
def modify_file(self, file_path, content):
    from utils.model_awareness import should_modify_file, check_file_context

    # Check file context and modification permission
    context = check_file_context(file_path)
    should_proceed, reason, _ = should_modify_file(file_path, "edit", "component_name")

    if not should_proceed:
        from utils.ultron_logger import log_ai_decision
        log_ai_decision("component_name", f"Modification blocked: {reason}", ai_model="component_name")
        raise PermissionError(f"Modification not allowed: {reason}")

    # Proceed with modification
    with open(file_path, 'w') as f:
        f.write(content)

    # Log the successful modification
    from utils.ultron_logger import log_file_operation
    log_file_operation("component_name", f"Modified {file_path}", file_path, "edit")
```

### 2. Centralized Logging Implementation
**Before:**
```python
def process_data(self, data):
    try:
        result = self._process(data)
        print(f"Processing completed: {result}")
        return result
    except Exception as e:
        print(f"Error processing data: {e}")
        raise
```

**After:**
```python
def process_data(self, data):
    from utils.ultron_logger import log_info, log_error

    try:
        log_info("component_name", f"Starting data processing", data_size=len(data))
        result = self._process(data)
        log_info("component_name", f"Data processing completed", result_size=len(result))
        return result
    except Exception as e:
        log_error("component_name", f"Data processing failed: {e}", error_type=type(e).__name__)
        raise
```

### 3. Voice Accessibility Integration
**Before:**
```python
def show_result(self, result):
    print(f"Result: {result}")
```

**After:**
```python
def show_result(self, result):
    from voice_manager import get_voice_manager

    # Display result
    print(f"Result: {result}")

    # Provide voice feedback
    try:
        voice_manager = get_voice_manager()
        voice_manager.speak(f"Result: {result}")
    except Exception as e:
        from utils.ultron_logger import log_error
        log_error("component_name", f"Voice feedback failed: {e}")
```

### 4. Event System Integration
**Before:**
```python
def execute_command(self, command):
    result = self._execute(command)
    return result
```

**After:**
```python
def execute_command(self, command):
    from utils.ultron_logger import log_info
    from utils.event_system import get_event_system

    # Emit command start event
    event_system = get_event_system()
    event_system.emit("command_start", {"command": command, "component": "component_name"})

    try:
        log_info("component_name", f"Executing command: {command}")
        result = self._execute(command)

        # Emit command completion event
        event_system.emit("command_complete", {
            "command": command,
            "result": result,
            "component": "component_name",
            "success": True
        })

        return result
    except Exception as e:
        # Emit command failure event
        event_system.emit("command_failed", {
            "command": command,
            "error": str(e),
            "component": "component_name",
            "success": False
        })
        raise
```

### 5. Comprehensive Error Handling
**Before:**
```python
def risky_operation(self):
    return self.external_service.call()
```

**After:**
```python
def risky_operation(self):
    from utils.ultron_logger import log_error, log_info
    import time

    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            log_info("component_name", f"Attempting risky operation (attempt {attempt + 1}/{max_retries})")
            result = self.external_service.call()
            log_info("component_name", "Risky operation completed successfully")
            return result
        except ConnectionError as e:
            if attempt < max_retries - 1:
                log_error("component_name", f"Connection error (attempt {attempt + 1}): {e}. Retrying...")
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            else:
                log_error("component_name", f"Connection error failed after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            log_error("component_name", f"Unexpected error in risky operation: {e}", error_type=type(e).__name__)
            raise
```

### 6. Type Hints and Documentation
**Before:**
```python
def process_items(items):
    results = []
    for item in items:
        results.append(process_item(item))
    return results
```

**After:**
```python
from typing import List, Dict, Any

def process_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process a list of items and return results.

    Args:
        items: List of item dictionaries to process

    Returns:
        List of processed item dictionaries

    Raises:
        ValueError: If items is None or empty
        ProcessingError: If item processing fails
    """
    from utils.ultron_logger import log_info, log_error

    if not items:
        raise ValueError("Items list cannot be None or empty")

    log_info("component_name", f"Processing {len(items)} items")
    results = []

    for i, item in enumerate(items):
        try:
            result = self.process_item(item)
            results.append(result)
        except Exception as e:
            log_error("component_name", f"Failed to process item {i}: {e}")
            # Continue processing other items or raise depending on requirements
            raise ProcessingError(f"Item processing failed: {e}")

    log_info("component_name", f"Successfully processed {len(results)} items")
    return results
```

### 7. Async/Await Patterns
**Before:**
```python
def fetch_data(self, url):
    response = requests.get(url)
    return response.json()
```

**After:**
```python
import aiohttp
import asyncio
from typing import Dict, Any

async def fetch_data(self, url: str) -> Dict[str, Any]:
    """Asynchronously fetch data from URL.

    Args:
        url: The URL to fetch data from

    Returns:
        Parsed JSON response

    Raises:
        aiohttp.ClientError: On network errors
        ValueError: On invalid JSON response
    """
    from utils.ultron_logger import log_info, log_error

    timeout = aiohttp.ClientTimeout(total=30)

    try:
        log_info("component_name", f"Fetching data from {url}")
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                log_info("component_name", f"Successfully fetched data from {url}")
                return data
    except aiohttp.ClientError as e:
        log_error("component_name", f"Network error fetching data: {e}")
        raise
    except ValueError as e:
        log_error("component_name", f"Invalid JSON response: {e}")
        raise
```

### 8. Thread Safety for GUI Components
**Before:**
```python
def update_gui(self, data):
    self.gui_component.update(data)
```

**After:**
```python
import threading
from typing import Any

class GUIComponent:
    def __init__(self):
        self._lock = threading.Lock()
        self._gui_data = {}

    def update_gui(self, data: Dict[str, Any]) -> None:
        """Thread-safe GUI update.

        Args:
            data: Data to update in GUI
        """
        from utils.ultron_logger import log_info

        with self._lock:
            try:
                log_info("gui_component", f"Updating GUI with {len(data)} items")
                self._gui_data.update(data)
                # Actual GUI update logic here
                self._perform_gui_update(data)
                log_info("gui_component", "GUI update completed successfully")
            except Exception as e:
                from utils.ultron_logger import log_error
                log_error("gui_component", f"GUI update failed: {e}")
                raise

    def _perform_gui_update(self, data: Dict[str, Any]) -> None:
        """Internal GUI update method."""
        # Platform-specific GUI update code
        pass

    def get_gui_data(self) -> Dict[str, Any]:
        """Thread-safe getter for GUI data."""
        with self._lock:
            return self._gui_data.copy()
```

### 9. Input Validation and Security
**Before:**
```python
def execute_command(self, command):
    return eval(command)
```

**After:**
```python
import re
from typing import Optional

def execute_command(self, command: str) -> Optional[str]:
    """Safely execute a validated command.

    Args:
        command: Command string to execute

    Returns:
        Command result or None if invalid

    Raises:
        ValueError: If command is invalid or unsafe
    """
    from utils.ultron_logger import log_info, log_error

    # Input validation
    if not command or not isinstance(command, str):
        raise ValueError("Command must be a non-empty string")

    if len(command) > 1000:
        raise ValueError("Command too long")

    # Sanitize input
    command = command.strip()

    # Validate command format (example: only allow specific patterns)
    allowed_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\s]*$')
    if not allowed_pattern.match(command):
        log_error("component_name", f"Invalid command format: {command}")
        raise ValueError("Invalid command format")

    try:
        log_info("component_name", f"Executing validated command: {command}")
        result = self._safe_execute(command)
        log_info("component_name", "Command executed successfully")
        return result
    except Exception as e:
        log_error("component_name", f"Command execution failed: {e}")
        raise
```

### 10. Performance Optimization
**Before:**
```python
def expensive_operation(self, data):
    results = []
    for item in data:
        results.append(self.process_item(item))
    return results
```

**After:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import List, Dict, Any

class OptimizedComponent:
    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._cache = {}

    @lru_cache(maxsize=128)
    def cached_expensive_operation(self, data_hash: str) -> Dict[str, Any]:
        """Cache expensive operations by data hash."""
        # Implementation here
        pass

    async def optimized_batch_operation(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data batch with concurrency and caching.

        Args:
            data: List of data items to process

        Returns:
            List of processed results
        """
        from utils.ultron_logger import log_info, log_error

        if not data:
            return []

        log_info("component_name", f"Processing batch of {len(data)} items")

        try:
            # Process in parallel using thread pool
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(self._executor, self._process_item_cached, item)
                for item in data
            ]

            results = await asyncio.gather(*tasks)
            log_info("component_name", f"Successfully processed {len(results)} items")
            return results

        except Exception as e:
            log_error("component_name", f"Batch processing failed: {e}")
            raise

    def _process_item_cached(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual item with caching."""
        # Generate hash for caching
        item_hash = hash(str(sorted(item.items())))

        if item_hash in self._cache:
            return self._cache[item_hash]

        result = self._process_item(item)
        self._cache[item_hash] = result

        # Cache size management
        if len(self._cache) > 1000:
            # Remove oldest entries (simple LRU)
            oldest_keys = list(self._cache.keys())[:100]
            for key in oldest_keys:
                del self._cache[key]

        return result
```

## Refactoring Checklist

### Architecture Compliance
- [ ] Model awareness checks added
- [ ] Centralized logging implemented
- [ ] Event system integration added
- [ ] Voice accessibility features included
- [ ] Thread safety implemented for GUI components

### Code Quality
- [ ] Type hints added to all functions
- [ ] Comprehensive error handling implemented
- [ ] Input validation and sanitization added
- [ ] Async/await patterns applied where appropriate
- [ ] Documentation updated with new signatures

### Performance & Security
- [ ] Caching implemented for expensive operations
- [ ] Concurrent processing added for batch operations
- [ ] Security validations implemented
- [ ] Resource cleanup ensured

### Testing & Maintenance
- [ ] Unit tests updated for new interfaces
- [ ] Integration tests added for new features
- [ ] Documentation updated to reflect changes
- [ ] Backward compatibility maintained

## Refactoring Guidelines

1. **Incremental Changes**: Make small, testable changes rather than large rewrites
2. **Preserve Functionality**: Ensure all existing behavior is maintained
3. **Additive Approach**: Add new patterns alongside existing code
4. **Test Frequently**: Test after each significant change
5. **Document Changes**: Update comments and docstrings
6. **Maintain Compatibility**: Keep existing APIs functional
7. **Follow Patterns**: Apply ULTRON Agent patterns consistently
8. **Error Handling**: Add comprehensive error handling and logging
9. **Performance**: Optimize where possible without breaking functionality
10. **Security**: Add security validations and safe coding practices

Remember: The goal is to enhance the code while maintaining full backward compatibility and following ULTRON Agent development standards.
