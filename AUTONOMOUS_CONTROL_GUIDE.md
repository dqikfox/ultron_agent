# ULTRON Autonomous Desktop Control
## Direct Python Execution with PyAutoGUI

## 🎯 Overview

ULTRON now has **full autonomous desktop control** through direct Python execution. The local Ollama model can generate and execute PyAutoGUI code in real-time.

---

## 🚀 Quick Start

### Method 1: Interactive Shell
```bash
python ultron_exec.py
```

**Example Session**:
```
🤖 You: Move mouse to center and click twice

💬 ULTRON:
<code>
pyautogui.moveTo(960, 540, duration=0.5)
pyautogui.click(clicks=2, interval=0.3)
</code>

⚡ Execution Result:
✅ Executed successfully
```

### Method 2: Through Agent Core
```python
from agent_core import UltronAgent

agent = UltronAgent()
await agent.initialize()

# Agent automatically uses autonomous_pyautogui tool
result = await agent.process_command("take a screenshot")
```

---

## 🧠 How It Works

### 1. **Model Training**
The model receives this system prompt:

```
You are ULTRON AI with full PyAutoGUI control.

AVAILABLE FUNCTIONS:
- pyautogui.moveTo(x, y, duration=0.5)
- pyautogui.click(x, y, clicks=1)
- pyautogui.write('text', interval=0.1)
- pyautogui.press('key')
- pyautogui.hotkey('ctrl', 'c')
- pyautogui.screenshot('path.png')
- pyautogui.scroll(amount)

OUTPUT FORMAT:
Wrap code in <code>...</code> tags
```

### 2. **Code Extraction**
ULTRON extracts code from:
- `<code>...</code>` tags
- ` ```python...``` ` markdown blocks

### 3. **Safe Execution**
Code runs in controlled environment with:
- PyAutoGUI access
- Basic Python builtins
- No file system access (unless explicitly added)

### 4. **Result Feedback**
Execution results return to model for continued reasoning.

---

## 📚 Available Commands

### Mouse Control
```python
# Move mouse
pyautogui.moveTo(500, 500, duration=0.5)

# Click
pyautogui.click()
pyautogui.doubleClick()
pyautogui.rightClick()

# Drag
pyautogui.drag(100, 0, duration=0.5)  # Drag right 100px
```

### Keyboard Control
```python
# Type text
pyautogui.write('Hello World', interval=0.1)

# Press keys
pyautogui.press('enter')
pyautogui.press('esc')

# Hotkeys
pyautogui.hotkey('ctrl', 'c')  # Copy
pyautogui.hotkey('ctrl', 'v')  # Paste
pyautogui.hotkey('win', 'd')   # Show desktop
```

### Screen Operations
```python
# Screenshot
pyautogui.screenshot('screenshot.png')

# Get screen info
size = pyautogui.size()  # (1920, 1080)
pos = pyautogui.position()  # (500, 500)

# Find image on screen
location = pyautogui.locateOnScreen('button.png')
if location:
    pyautogui.click(location)
```

### Scrolling
```python
# Scroll up
pyautogui.scroll(10)

# Scroll down
pyautogui.scroll(-10)
```

---

## 💡 Example Use Cases

### 1. Automated Testing
```
You: Test the login form - enter username "test" and password "pass123"

ULTRON:
<code>
pyautogui.click(100, 200)  # Username field
pyautogui.write('test', interval=0.1)
pyautogui.press('tab')
pyautogui.write('pass123', interval=0.1)
pyautogui.press('enter')
</code>
```

### 2. Screenshot Analysis
```
You: Take a screenshot and analyze it

ULTRON:
<code>
pyautogui.screenshot('analysis.png')
</code>

[Then uses vision tool to analyze the screenshot]
```

### 3. Window Management
```
You: Minimize all windows and open notepad

ULTRON:
<code>
pyautogui.hotkey('win', 'd')  # Show desktop
pyautogui.hotkey('win', 'r')  # Run dialog
pyautogui.write('notepad', interval=0.1)
pyautogui.press('enter')
</code>
```

### 4. Repetitive Tasks
```
You: Click the refresh button 5 times with 2 second delays

ULTRON:
<code>
import time
for i in range(5):
    pyautogui.click(1000, 100)
    time.sleep(2)
</code>
```

---

## 🔒 Security Considerations

### ✅ Safe (Local Only)
- No network access
- Runs on your machine
- Full control over execution

### ⚠️ Cautions
- Model has **full desktop control**
- Can click, type, delete files (if enabled)
- Don't leave running unattended
- Review generated code before execution (optional)

### 🛡️ Safety Features

**1. Restricted Environment**
```python
safe_env = {
    'pyautogui': pyautogui,
    'print': print,
    # No 'os', 'sys', 'subprocess' by default
}
```

**2. Execution Logging**
All code execution logged to `logs/ultron_exec.log`

**3. Manual Confirmation (Optional)**
```python
# Add to ultron_exec.py
if input(f"Execute this code? (y/n)\n{code}\n> ") != 'y':
    return "Execution cancelled"
```

---

## 🎮 Advanced Features

### 1. Add More Modules
```python
# In ultron_exec.py, add to safe_env:
safe_env = {
    'pyautogui': pyautogui,
    'time': time,
    'os': os,  # File operations
    'requests': requests,  # Web requests
}
```

### 2. Image Recognition
```python
# Teach model to find UI elements
You: Click the save button

ULTRON:
<code>
location = pyautogui.locateOnScreen('save_button.png')
if location:
    pyautogui.click(location)
else:
    print("Save button not found")
</code>
```

### 3. Continuous Monitoring
```python
# Watch for changes
You: Monitor the screen and alert if color changes at (500, 500)

ULTRON:
<code>
import time
original = pyautogui.pixel(500, 500)
while True:
    current = pyautogui.pixel(500, 500)
    if current != original:
        print(f"Color changed from {original} to {current}")
        break
    time.sleep(1)
</code>
```

---

## 📊 Performance

| Operation | Speed | Notes |
|-----------|-------|-------|
| Mouse move | <0.5s | Smooth animation |
| Click | <0.1s | Instant |
| Type text | ~0.1s/char | Configurable interval |
| Screenshot | ~0.5s | Full screen |
| Image search | 1-3s | Depends on screen size |

---

## 🐛 Troubleshooting

### PyAutoGUI Not Found
```bash
pip install pyautogui pillow
```

### Permission Denied (macOS)
```bash
# Grant accessibility permissions
System Preferences → Security & Privacy → Accessibility
```

### Code Not Executing
Check logs:
```bash
Get-Content logs/ultron_exec.log -Tail 50
```

### Model Not Generating Code
Improve prompt:
```
You: [Be specific] Move mouse to coordinates 500, 500 and click
```

---

## 🚀 Next Steps

1. **Run Interactive Shell**:
   ```bash
   python ultron_exec.py
   ```

2. **Test Basic Commands**:
   - "Move mouse to center"
   - "Take a screenshot"
   - "Type hello world"

3. **Integrate with Agent**:
   - Tool auto-loads in `agent_core.py`
   - Use through voice commands
   - Combine with vision for feedback loop

4. **Build Workflows**:
   - Create automation scripts
   - Save successful patterns
   - Chain multiple actions

---

## 📚 Resources

- **PyAutoGUI Docs**: https://pyautogui.readthedocs.io
- **ULTRON Logs**: `logs/ultron_exec.log`
- **Tool Code**: `tools/autonomous_pyautogui.py`
- **Execution Engine**: `ultron_exec.py`

---

*ULTRON now has autonomous desktop control. Use responsibly!* 🤖
