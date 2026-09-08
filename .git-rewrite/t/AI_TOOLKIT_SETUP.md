# AI Toolkit Extension Setup for GPT-5

## Installation

1. **Install AI Toolkit Extension**
   ```bash
   code --install-extension ms-vscode.vscode-ai-toolkit
   ```

2. **Set OpenAI API Key**
   ```bash
   # Windows
   setx OPENAI_API_KEY "your-api-key-here"
   
   # Or add to .env file
   echo "OPENAI_API_KEY=your-api-key-here" >> .env
   ```

3. **Restart VS Code**

## Configuration Files Created

- `.vscode/extensions.json` - Extension recommendations
- `.vscode/ai-toolkit.json` - AI Toolkit configuration with GPT-5 priority
- `.vscode/settings.json` - Updated with AI Toolkit settings
- `gpt5_integration.py` - Status checker

## Model Priority (GPT-5 not yet available)

1. `gpt-4o` (highest priority)
2. `gpt-4-turbo` (fallback)
3. `gpt-4` (fallback)

*Note: Will auto-upgrade to GPT-5 when released*

## Usage

- **Code Completion**: Automatic with GPT-5
- **Chat Assistant**: Ctrl+Shift+P → "AI Toolkit: Chat"
- **Code Explanation**: Right-click → "Explain with AI"
- **Refactoring**: Right-click → "Refactor with AI"

## Status Check

```bash
python gpt5_integration.py
```

## Features Enabled

- ✅ Code completion with GPT-4o (ready for GPT-5)
- ✅ Chat assistant
- ✅ Code explanation
- ✅ Debugging assistance
- ✅ Refactoring suggestions