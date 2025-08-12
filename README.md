# Ultron Agent 2 - Development Guide

##  Overview
This is the Ultron Agent 2 project workspace, configured with advanced AI development tools and extensions.

##  AI Tools Enabled

###  Active AI Extensions
- **Amazon Q (CodeWhisperer)** - AWS AI coding assistant
- **GitHub Copilot** - GitHub's AI pair programmer  
- **Sixth AI** - Advanced inline completions (with proposed API)
- **Pochi/Tabby** - MCP-enabled AI assistant
- **IDL for VS Code** - Specialized development environment

##  Quick Start

### 1. Launch with AI Extensions
```powershell
# Use the custom launch script
& "$env:USERPROFILE\launch-vscode-ai.ps1" -WorkspacePath "C:\Projects\ultron_agent_2" -WithProposedAPIs

# Or manually
code --enable-proposed-api sixth.sixth-ai "C:\Projects\ultron_agent_2"
```

### 2. Verify AI Tools
- Press `Ctrl+Shift+P` and type "Amazon Q" to access Q Chat
- Start typing code to see GitHub Copilot suggestions
- Use `Ctrl+I` for inline AI assistance
- Check status bar for active AI services

##  Configuration Features

### AI Optimizations
-  Proposed APIs enabled for Sixth AI
-  Network proxy configuration for connectivity
-  Performance optimizations for file watching
-  Memory usage optimizations

### Development Settings
- **Python**: Strict type checking, Black formatting
- **Editor**: Format on save, trim whitespace
- **Terminal**: PowerShell default
- **Theme**: Neon IDL with IDL icons

##  AI Usage Tips

### Amazon Q
- Use `/help` in Q Chat for guidance
- Ask questions about your code
- Request code reviews and optimizations

### GitHub Copilot
- Tab to accept suggestions
- `Ctrl+Right Arrow` to accept word-by-word
- `Alt+]` and `Alt+[` to cycle through suggestions

### Sixth AI
- Advanced context-aware completions
- Supports inline editing capabilities
- Works with proposed VS Code APIs

##  Project Structure
```
ultron_agent_2/
 .vscode/
    settings.json     # AI-optimized workspace settings
    launch.json       # Debug configurations
 docs/
    README.md         # This guide
    API.md           # API documentation
    DEVELOPMENT.md   # Development workflow
 src/                  # Source code
 tests/               # Test files
 requirements.txt     # Python dependencies
 pyproject.toml      # Python project configuration
```

##  Troubleshooting

### Common Issues
1. **Sixth AI API Error**: Ensure VS Code launched with `--enable-proposed-api sixth.sixth-ai`
2. **Amazon Q Connectivity**: Check network settings and proxy configuration
3. **Copilot Not Working**: Verify authentication in VS Code settings
4. **Performance Issues**: Review file watcher exclusions

### Quick Fixes
```powershell
# Restart with all AI tools
& "$env:USERPROFILE\launch-vscode-ai.ps1" -WorkspacePath "." -WithProposedAPIs

# Check extension status
code --list-extensions --show-versions | findstr -i "amazon\|github\|sixth"
```

##  Customization

### Adding New AI Tools
1. Install extension via VS Code marketplace
2. Add configuration to `.vscode/settings.json`
3. Update launch script if needed
4. Test functionality

### Performance Tuning
- Adjust `files.watcherExclude` for your project structure
- Modify `python.analysis.typeCheckingMode` as needed
- Configure additional formatters/linters

##  Commands Reference

### AI Assistant Commands
- `Ctrl+Shift+P`  "Amazon Q: Open Chat"
- `Ctrl+I`  Inline AI editing
- `Alt+/`  Trigger completions
- `F1`  Command palette (all AI commands)

### Development Commands  
- `Ctrl+Shift+P`  "Python: Select Interpreter"
- `Ctrl+K, Ctrl+F`  Format document
- `Ctrl+Shift+I`  Organize imports

---
** Ready to code with AI assistance!**
