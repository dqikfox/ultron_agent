# OpenAI Computer Use Integration for ULTRON Agent

## Overview

ULTRON Agent now includes OpenAI Computer Use capabilities for direct screen control, mouse/keyboard automation, and visual interface interaction.

## Features

- **Screen Capture**: Automatic screenshot capture and analysis
- **Mouse Control**: Click, drag, and scroll operations
- **Keyboard Input**: Text typing and key press automation  
- **Voice Commands**: Natural language computer control
- **Session Logging**: Complete audit trail of all actions
- **Safety Controls**: Configurable action limits and restrictions

## Quick Start

### 1. Configuration

Add OpenAI API key to environment:
```bash
set OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Voice Commands

```
"computer click desktop"     -> Clicks center of desktop
"type hello world"          -> Types text
"scroll down"               -> Scrolls down page
"take screenshot"           -> Captures screen
"press enter"               -> Presses Enter key
```

### 3. Direct API Usage

```python
from openai_computer_use_integration import ultron_computer_use

# Execute computer command
result = ultron_computer_use.manager.process_computer_command("click on button")

# Get session status
status = ultron_computer_use.get_status()
```

## Configuration Options

In `ultron_config.json`:

```json
{
  "openai_computer_use": {
    "enabled": true,
    "model": "gpt-4o",
    "max_actions_per_request": 10,
    "action_delay_seconds": 0.5,
    "safety_mode": true,
    "allowed_actions": ["click", "type", "key", "scroll", "screenshot"],
    "voice_commands": {
      "enabled": true,
      "wake_phrases": ["computer", "screen", "click", "type"]
    }
  }
}
```

## Available Actions

### Mouse Actions
- `click` - Click at coordinates
- `right_click` - Right-click at coordinates  
- `double_click` - Double-click at coordinates
- `scroll` - Scroll up/down at coordinates

### Keyboard Actions
- `type` - Type text string
- `key` - Press individual keys (enter, escape, tab, etc.)
- `hotkey` - Press key combinations (ctrl+c, alt+tab, etc.)

### Screen Actions
- `screenshot` - Capture current screen
- `find_element` - Locate UI elements
- `wait_for_element` - Wait for element to appear

## Voice Command Examples

```
"computer take a screenshot"
"click on the start button"
"type my email address"
"scroll down to see more"
"press escape to cancel"
"right click on the file"
"double click to open"
```

## Session Management

### View Session Summary
```python
summary = ultron_computer_use.manager.get_session_summary()
print(f"Commands executed: {summary['total_commands']}")
print(f"Success rate: {summary['success_rate']:.2%}")
```

### Export Session Log
```python
log_file = ultron_computer_use.manager.export_session_log()
print(f"Session exported to: {log_file}")
```

### Toggle Computer Use
```python
# Disable computer use
ultron_computer_use.manager.toggle_computer_use(False)

# Re-enable
ultron_computer_use.manager.toggle_computer_use(True)
```

## Safety Features

- **Action Limits**: Maximum actions per request
- **Delay Controls**: Configurable delays between actions
- **Allowed Actions**: Whitelist of permitted operations
- **Session Logging**: Complete audit trail
- **Error Handling**: Graceful failure recovery

## Integration Points

### ULTRON Agent Core
Computer Use is automatically initialized in `agent_core.py`:
```python
await self._initialize_computer_use()
```

### Voice System
Voice commands are processed through the voice manager with computer use wake phrases.

### GUI Integration
Computer Use status and controls are available in the ULTRON web interface.

## Testing

Run the test suite:
```bash
python test_openai_computer_use.py
```

Expected output:
```
=== TESTING OPENAI COMPUTER USE ===
[OK] OpenAI API key configured
Commands: 4
Success Rate: 100.00%
Integration: OK
[SUCCESS] OpenAI Computer Use integration is ready!
```

## Troubleshooting

### Common Issues

1. **API Key Missing**
   - Set `OPENAI_API_KEY` environment variable
   - Verify key has Computer Use access

2. **Actions Not Executing**
   - Check `safety_mode` setting
   - Verify `allowed_actions` list
   - Review session logs for errors

3. **Voice Commands Not Working**
   - Ensure voice system is initialized
   - Check wake phrase configuration
   - Verify microphone permissions

### Debug Mode

Enable detailed logging:
```python
import logging
logging.getLogger("openai_computer_use").setLevel(logging.DEBUG)
```

## Security Considerations

- Computer Use provides direct system access
- Use `safety_mode` in production environments
- Regularly review session logs
- Limit `allowed_actions` to required operations only
- Consider network isolation for sensitive operations

## Advanced Usage

### Custom Action Sequences
```python
# Execute multiple actions
actions = [
    {"function": "computer_click", "arguments": {"x": 100, "y": 200}},
    {"function": "computer_type", "arguments": {"text": "Hello"}},
    {"function": "computer_key", "arguments": {"key": "enter"}}
]

result = ultron_computer_use.manager._execute_actions(actions)
```

### Screen Analysis Integration
```python
# Combine with vision system
screenshot = ultron_computer_use.manager.computer_tool._capture_screen()
# Process with ULTRON vision system for intelligent automation
```

## API Reference

### UltronComputerUseManager
- `process_computer_command(command: str)` - Execute computer command
- `get_session_summary()` - Get session statistics
- `export_session_log(filepath: str)` - Export session data
- `toggle_computer_use(enabled: bool)` - Enable/disable functionality

### UltronComputerUseAPI
- `handle_voice_command(voice_input: str)` - Process voice command
- `get_status()` - Get system status

---

**Status**: ✅ Fully Operational
**Integration**: ✅ Complete
**Voice Commands**: ✅ Active
**Session Logging**: ✅ Enabled