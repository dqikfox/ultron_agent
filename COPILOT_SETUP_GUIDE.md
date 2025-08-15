# GitHub Copilot Setup & Troubleshooting Guide

## Quick Setup Checklist

### 1. Verify Copilot Installation
```bash
# Check if Copilot extension is installed
code --list-extensions | findstr copilot
```

### 2. Sign In to GitHub
- Press `Ctrl+Shift+P`
- Type "GitHub Copilot: Sign In"
- Follow authentication prompts

### 3. Check Copilot Status
- Look for Copilot icon in VS Code status bar (bottom right)
- Should show "Copilot: Ready" or similar

## Keyboard Shortcuts

### Essential Copilot Commands
- `Tab` - Accept suggestion
- `Ctrl+Right Arrow` - Accept word by word
- `Alt+]` - Next suggestion
- `Alt+[` - Previous suggestion
- `Ctrl+Enter` - Open Copilot suggestions panel
- `Ctrl+I` - Inline chat with Copilot

### Copilot Chat
- `Ctrl+Shift+P` → "GitHub Copilot: Open Chat"
- `Ctrl+Alt+I` - Quick chat

## Troubleshooting Common Issues

### Issue 1: No Suggestions Appearing
**Solutions:**
1. Check status bar - ensure Copilot is active
2. Restart VS Code
3. Sign out and sign back in to GitHub
4. Check internet connection

### Issue 2: Copilot Disabled for File Type
**Solution:**
```json
// Add to settings.json
"github.copilot.enable": {
    "python": true,
    "javascript": true,
    // Add your file types here
}
```

### Issue 3: Slow or No Response
**Solutions:**
1. Check network connectivity
2. Disable other AI extensions temporarily
3. Clear VS Code cache:
   ```bash
   # Close VS Code, then delete:
   %APPDATA%\\Code\\User\\workspaceStorage
   ```

### Issue 4: Authentication Problems
**Solutions:**
1. `Ctrl+Shift+P` → "GitHub Copilot: Sign Out"
2. `Ctrl+Shift+P` → "GitHub Copilot: Sign In"
3. Check GitHub subscription status

## Optimizing Copilot Performance

### 1. Provide Context
- Write descriptive comments
- Use meaningful variable names
- Include function docstrings

### 2. Example Context Patterns
```python
# Good context for Copilot
def calculate_user_score(user_data: dict, weights: dict) -> float:
    """
    Calculate weighted score for user based on multiple factors.
    
    Args:
        user_data: Dictionary containing user metrics
        weights: Dictionary with scoring weights
    
    Returns:
        Calculated score as float
    """
    # Copilot will suggest implementation here
```

### 3. Use Comments to Guide Suggestions
```python
# Create a secure password hash using bcrypt
# Validate email format using regex
# Handle database connection errors gracefully
```

## Multi-AI Setup (Your Current Configuration)

You have multiple AI assistants configured:
- **Amazon Q** - AWS-focused assistance
- **GitHub Copilot** - Code completion and chat
- **Sixth AI** - Advanced inline completions

### Avoiding Conflicts
1. Use different shortcuts for each AI
2. Enable/disable as needed for specific tasks
3. Amazon Q for AWS/cloud questions
4. Copilot for general coding
5. Sixth AI for advanced completions

## Testing Copilot

### Quick Test
1. Create a new Python file
2. Type: `def fibonacci(`
3. Wait for Copilot suggestion
4. Press `Tab` to accept

### Advanced Test
```python
# Create a function that reads a CSV file and returns a pandas DataFrame
# with proper error handling and type hints
```

## Performance Tips

### 1. File Size Optimization
- Keep files under 1000 lines for best performance
- Split large files into modules

### 2. Context Window
- Copilot considers ~8KB of surrounding code
- Keep related code nearby

### 3. Language-Specific Tips
- **Python**: Use type hints and docstrings
- **JavaScript**: Use JSDoc comments
- **TypeScript**: Leverage type definitions

## Useful Commands

```bash
# Check Copilot status
Ctrl+Shift+P → "GitHub Copilot: Check Status"

# View Copilot logs
Ctrl+Shift+P → "GitHub Copilot: Open Logs"

# Toggle Copilot on/off
Ctrl+Shift+P → "GitHub Copilot: Toggle"

# Copilot settings
Ctrl+Shift+P → "Preferences: Open Settings (JSON)"
```

## Integration with Your ULTRON Project

### Optimized for Your Codebase
- Copilot will learn from your existing code patterns
- Use consistent naming conventions
- Add comments explaining complex logic
- Leverage your security_utils.py patterns

### Example Usage in ULTRON
```python
# Copilot will suggest secure implementations based on your security_utils
from security_utils import sanitize_log_input, validate_file_path

def process_user_input(user_data: str) -> str:
    # Copilot suggests: return sanitize_log_input(user_data)
```

### GUI Integration
The ULTRON Enhanced GUI is located at:
- **Path**: `gui/ultron_enhanced/web/index.html`
- **URL**: `file:///C:/Projects/ultron_agent_2/gui/ultron_enhanced/web/index.html`
- **Launcher**: Use `launch_gui.bat` or `python launch_gui.py`

## Need Help?

1. **VS Code Command Palette**: `Ctrl+Shift+P` → Search "Copilot"
2. **GitHub Copilot Docs**: https://docs.github.com/copilot
3. **Status Bar**: Check Copilot icon for current status
4. **Output Panel**: View → Output → Select "GitHub Copilot"

---
**Your Copilot is now optimized for the ULTRON Agent 3.0 project!** 🚀