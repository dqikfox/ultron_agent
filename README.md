# Ultron Agent 3.0 - Advanced AI Agent Platform

## Overview

Ultron Agent 3.0 is a sophisticated AI agent platform that combines autonomous workflow execution, comprehensive tool integration, and multi-modal interaction capabilities. Built with a modular architecture, it provides an extensible foundation for AI-driven automation and intelligent assistance.

## 🌟 Key Features

- **Agent-Based Workflow Engine**: Event-driven task orchestration with intelligent planning
- **Sandboxed Code Interpreter**: Secure Python execution environment with safety measures
- **Dual-Layer Memory System**: Short-term context and long-term knowledge management
- **Multi-Modal Interfaces**: Voice, vision, GUI, CLI, and API access
- **OpenAI-Compatible API**: Standard REST and WebSocket endpoints with function calling
- **Comprehensive Tool Ecosystem**: 15+ built-in tools for system control, web access, and AI operations
- **Real-Time Monitoring**: Performance metrics, health checks, and instrumentation
- **State Persistence**: Serialization and resume capabilities for continuous operation

## 📚 Documentation

- **[📖 Major Components & Features](docs/major_components_and_features.md)** - Comprehensive technical documentation
- **[🏗️ Project Overview](docs/project_overview.md)** - Architecture and system design
- **[📋 Component Specifications](COMPONENT_SPECIFICATIONS.md)** - Detailed technical specifications
- **[GUI Reference Guide](GUI_REFERENCE.md)** - Primary GUI interface and deprecated file information

## AI Tools Enabled

### Active AI Extensions

- **Amazon Q (CodeWhisperer)** - AWS AI coding assistant
- **GitHub Copilot** - GitHub's AI pair programmer
- **Sixth AI** - Advanced inline completions (with proposed API)
- **Pochi/Tabby** - MCP-enabled AI assistant
- **IDL for VS Code** - Specialized development environment

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy configuration template
cp ultron_config.json.example ultron_config.json

# Edit configuration with your API keys
# Set OpenAI, Anthropic, or other API keys as needed
```

### 3. Launch
```bash
# Start the agent
python main.py

# Or use the enhanced launcher
./run.bat
```

### 4. Access Interfaces

- **Pokédex GUI**: Retro gaming interface at `http://localhost:8081`
- **Mobile Web Interface**: Modern responsive interface at `http://localhost:8001`
- **CLI**: Interactive command-line interface
- **API**: HTTP endpoints on `http://localhost:8001`

## Configuration Features

### AI Optimizations

- Proposed APIs enabled for Sixth AI
- Network proxy configuration for connectivity
- Performance optimizations for file watching
- Memory usage optimizations

### Development Settings

- **Python**: Strict type checking, Black formatting
- **Editor**: Format on save, trim whitespace
- **Terminal**: PowerShell default
- **Theme**: Neon IDL with IDL icons

## AI Usage Tips

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

## 🤖 Model Awareness & Testing

### Current Model Configuration

The ULTRON Agent uses **qwen3-coder:480b-cloud** as its primary LLM model, hosted via Ollama at `http://localhost:11434`.

### Automated Model Validation

Use the comprehensive model awareness validator script for systematic testing:

```bash
# Test current configured model
python model_awareness_validator.py

# Test specific model
python model_awareness_validator.py deepseek-r1:14b

# Test all available models
for model in $(curl -s http://localhost:11434/api/tags | jq -r '.models[].name'); do
  echo "Testing $model..."
  python model_awareness_validator.py "$model"
done
```

**Latest Validation Results** (as of 2025-10-11):

- **qwen3-coder:480b-cloud**: ✅ PASSED (2/3)
  - Model Identity: ❌ Failed (identified as "Qwen3" but not full name)
  - Project Awareness: ✅ Passed (8/8 - perfect score)
  - Model Switching: ✅ Passed (6/6 - perfect score)

- **deepseek-r1:14b**: ❌ FAILED (0/3 - timeouts)
  - All tests timed out, indicating performance issues

### Manual Model Testing

Test the current model's awareness of itself and the project:

```bash
# Test model identity
echo "What model are you? Be specific about your name and architecture." | ollama run qwen3-coder:480b-cloud

# Test project knowledge
echo "You are running in the ULTRON Agent project. Describe its key components and purpose." | ollama run qwen3-coder:480b-cloud
```

### Available Models

The system supports multiple models for different use cases:

- **qwen3-coder:480b-cloud**: Primary coding and reasoning model (MoE architecture)
- **gerard/ultron:latest**: ULTRON-specific personality model
- **deepseek-r1:14b**: Advanced reasoning model
- **llama3.1:latest**: General purpose model
- **mistral-small3.2:latest**: Efficient conversational model

### Model Switching

To switch models, update `ultron_config.json`:

```json
{
  "llm_model": "qwen3-coder:480b-cloud"
}
```

Or use the API to switch dynamically:

```bash
curl -X POST http://localhost:8001/api/model/switch \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1:14b"}'
```

### Model Awareness Requirements

All models used in ULTRON Agent should be aware of:

1. **Identity**: Correct model name and architecture
2. **Project Context**: ULTRON Agent architecture and components
3. **Environment**: VS Code integration, tool ecosystem, and capabilities
4. **Safety**: Ethical guidelines and responsible AI practices

**Validation Criteria**:

- **PASS**: 2/3 or higher on automated validation tests
- **Project Awareness**: Must score 3+ out of 8 key indicators
- **Model Switching**: Must score 3+ out of 6 understanding indicators
- **Identity**: Should correctly identify model name (bonus requirement)

### Validation Script Features

The `model_awareness_validator.py` script provides:

- **Automated Testing**: Runs comprehensive test suite on any model
- **Detailed Logging**: Saves results to `logs/model_awareness_*.json`
- **Scoring System**: Quantifies awareness levels with numerical scores
- **Batch Testing**: Can test multiple models sequentially
- **CI/CD Ready**: Returns appropriate exit codes for automation

### Testing Model Capabilities

```bash
# Test coding capabilities
echo "Write a Python function to parse JSON and handle errors gracefully." | ollama run qwen3-coder:480b-cloud

# Test reasoning capabilities
echo "Analyze this code for potential security vulnerabilities: [paste code]" | ollama run qwen3-coder:480b-cloud

# Test project-specific knowledge
echo "How does the ULTRON Agent handle tool discovery and execution?" | ollama run qwen3-coder:480b-cloud
```

## Project Structure

```bash
ultron_agent_2/
 .vscode/
    settings.json     # AI-optimized workspace settings
    launch.json       # Debug configurations
 assistant/           # AI Assistant Web Application
    ai-assistant/     # React TypeScript web app
    main.py          # Python backend integration
    todo.md          # Project tasks
    *.md, *.pdf      # Project documentation
 docs/
    README.md         # This guide
    API.md           # API documentation
    DEVELOPMENT.md   # Development workflow
 src/                  # Source code
 tests/               # Test files
 requirements.txt     # Python dependencies
 pyproject.toml      # Python project configuration
```

## Troubleshooting

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

## Customization

### Adding New AI Tools

1. Install extension via VS Code marketplace
2. Add configuration to `.vscode/settings.json`
3. Update launch script if needed
4. Test functionality

### Performance Tuning

- Adjust `files.watcherExclude` for your project structure
- Modify `python.analysis.typeCheckingMode` as needed
- Configure additional formatters/linters

## ULTRON Enhanced GUI Interface

The project includes two web interfaces:

### Pokédex GUI (Primary)

- **Location**: `gui/ultron_enhanced/web/`
- **Technology**: HTML5 + CSS3 + JavaScript with retro gaming theme
- **Port**: 8081
- **Status**: ✅ Fully Functional
- **Features**: Console, System Monitor, Vision, Tasks, Files, Settings, Profile
- **Launch**: `cd gui/ultron_enhanced/web && python -m http.server 8081`

### Mobile Web Interface

- **Location**: `tools/mobile_web_interface_tool.py`
- **Technology**: Flask-based responsive web app
- **Port**: 8001
- **Status**: ✅ Functional with API backend
- **Features**: Command execution, status monitoring, mobile-optimized
- **Launch**: `python tools/mobile_web_interface_tool.py`

### Features (Both Interfaces)

- 🤖 Multiple AI personalities (General, Creative, Technical, Productivity, Research)
- 💬 Real-time chat interface with conversation history
- 📁 File processing (PDF, DOC, images) with AI analysis
- 🔍 Web search integration with AI insights
- 📝 Productivity suite (notes, tasks, reminders)
- 🎨 Modern responsive UI with dark/light themes

### Quick Start - GUI Interface

```bash
# Launch the Pokédex GUI (recommended)
cd gui/ultron_enhanced/web
python -m http.server 8081

# Access at: http://localhost:8081

# Alternative: Launch mobile web interface
python tools/mobile_web_interface_tool.py
# Access at: http://localhost:8001
```

## Commands Reference

### AI Assistant Commands

- `Ctrl+Shift+P`  "Amazon Q: Open Chat"
- `Ctrl+I`  Inline AI editing
- `Alt+/`  Trigger completions
- `F1`  Command palette (all AI commands)

### Development Commands

- `Ctrl+K, Ctrl+F`  Format document
- `Ctrl+Shift+I`  Organize imports

---
**Ready to code with AI assistance!**

## 📝 Changelog

### Version 3.0.1 - October 9, 2025

- **Fixed**: UltronLogger compatibility issues - added missing `info()`, `error()`, `warning()`, `debug()` methods
- **Improved**: Model identity awareness - switched from `qwen3-coder:480b-cloud` to `gerard/ultron:latest` for better role-playing
- **Enhanced**: Vision system OCR support - added multiple Tesseract installation path detection
- **Fixed**: Event system logging errors resolved
- **Updated**: Configuration validation and error handling improvements

### Version 3.0.0 - Initial Release

- Complete AI agent platform with modular architecture
- Multi-modal interfaces (voice, vision, GUI, API)
- Comprehensive tool ecosystem
- Real-time monitoring and state persistence
- OpenAI-compatible API endpoints

