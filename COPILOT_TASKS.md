# Tasks for GitHub Copilot

## Priority 1: Fix Async Initialization

**File**: `agent_core.py`
**Lines**: 327-332
**Problem**: Coroutines not properly awaited

### Current Code (BROKEN)
```python
init_tasks: List[Tuple[str, Any]] = [
    ("computer_use", self._initialize_computer_use()),
    ("event_system", self._initialize_event_system()),
    ("platform_manager", self._initialize_platform_manager()),
    ("idle_monitor", self._initialize_idle_monitor()),
    ("keyboard_listener", self._initialize_keyboard_listener()),
    ("tools", self._load_tools()),
]

for task_name, task in init_tasks:
    try:
        await task  # RuntimeWarning: coroutine was never awaited
```

### Suggested Fix
```python
# Option 1: Await immediately
for task_name in ["computer_use", "event_system", "platform_manager", "idle_monitor", "keyboard_listener", "tools"]:
    try:
        if task_name == "computer_use":
            await self._initialize_computer_use()
        elif task_name == "event_system":
            await self._initialize_event_system()
        # ... etc

# Option 2: Use asyncio.gather
await asyncio.gather(
    self._initialize_computer_use(),
    self._initialize_event_system(),
    # ... etc
    return_exceptions=True
)
```

## Priority 2: Fix Voice Encoding

**File**: `voice_manager.py` or `voice.py`
**Problem**: Emoji character '\U0001f504' causing charmap codec error

### Suggested Fix
```python
# Option 1: Remove emoji
message = "Voice system initialized"  # No emoji

# Option 2: Use UTF-8 encoding
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Option 3: Catch and sanitize
try:
    print("🔄 Voice system")
except UnicodeEncodeError:
    print("[Voice] Voice system")
```

## Priority 3: Test Integration

After fixes, verify:
1. Agent starts without errors
2. Command history records commands
3. Performance tracking works
4. Error recovery retries on failure

## Success Criteria
- [ ] Agent starts successfully
- [ ] No async warnings
- [ ] No encoding errors
- [ ] All enhancements functional
