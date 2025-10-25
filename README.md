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

### Core Documentation
- **[📖 Developer Guide](.github/copilot-instructions.md)** - Complete development guide and patterns
- **[📚 Documentation Hub](DOCUMENTATION_HUB.md)** - Central index for all documentation
- **[🤖 Continue.dev Integration](CONTINUE_INTEGRATION_COMPLETE.md)** - Agent mode & rules system
- **[🤝 Copilot + Continue.dev](COPILOT_CONTINUE_INTEGRATION.md)** - Multi-AI assistant coordination
- **[🚀 Quick Reference](DOCS_QUICK_REFERENCE.md)** - Fast access to common resources
- **[🔊 Voice System](VOICE_MICROPHONE_DOCUMENTATION.md)** - Voice/microphone integration guide
- **[🔌 MCP Integration](MCP_INTEGRATION_GUIDE.md)** - Model Context Protocol setup
- **[🏗️ System Architecture](SYSTEM_ARCHITECTURE.md)** - Component connections and data flow
- **[📋 Setup Checklist](SETUP_CHECKLIST.md)** - Installation and configuration

### Internal Documentation (Company/Team)
- **[🌐 API Documentation](https://internal.docs/api)** - REST API reference and usage
- **[🏗️ Architecture Guide](https://internal.docs/architecture)** - System design patterns
- **[🚀 Deployment Process](https://internal.docs/deployment)** - Production deployment procedures

### Technical References
- **[Major Components & Features](docs/major_components_and_features.md)** - Technical documentation
- **[Project Overview](docs/project_overview.md)** - Architecture overview
- **[Component Specifications](COMPONENT_SPECIFICATIONS.md)** - Detailed specifications
- **[GUI Reference Guide](GUI_REFERENCE.md)** - Interface documentation

## AI Tools Enabled

### Active AI Extensions

- **Amazon Q (CodeWhisperer)** - AWS AI coding assistant with ULTRON architecture awareness
- **GitHub Copilot** - GitHub's AI pair programmer with ULTRON pattern recognition
- **Continue Extension** - Multi-model LLM integration with MCP orchestration
- **Sixth AI** - Advanced inline completions (with proposed API)
- **Pochi/Tabby** - MCP-enabled AI assistant
- **IDL for VS Code** - Specialized development environment

### AI Assistant Coordination

- **Unified Development Team**: All AI assistants work together with shared ULTRON context
- **Task-Specific Routing**: Commands automatically routed to appropriate AI assistant
- **Cross-Assistant Communication**: Coordinated workflow for complex development tasks
- **Enhanced Context Awareness**: Complete understanding of ULTRON architecture and patterns

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Install dependencies
pip install -r requirements.txt

# Install Ollama (required for AI backend)
# Download from: https://ollama.ai/download
# Or use package manager:
winget install Ollama.Ollama
```

### 2. Configuration
```bash
# Copy configuration template
cp ultron_config.json.example ultron_config.json

# Edit configuration with your API keys
# Set OpenAI, Anthropic, or other API keys as needed
# Default model: llava:7b (multimodal, vision-enabled)
```

### 3. Launch (Recommended Method)
```bash
# Use the master launcher with automated health checks
.\run.bat

# This will:
# 1. Clean up any existing processes
# 2. Verify Python and required files
# 3. Start/verify Ollama service
# 4. Run 5 comprehensive health tests
# 5. Launch Web GUI and Frontend UI
# 6. Provide complete system status
```

**New in v3.0**: The launcher now includes **automated health checks** that validate your system before startup:
- ✅ Service availability check
- ✅ Model availability verification (llava:7b)
- ✅ Text generation test
- ✅ Chat API validation
- ✅ Context retention test

All test results are logged to `ultron_master_startup.log`. If any test fails, you'll be prompted to continue or abort.

### 4. Alternative Launch Methods
```bash
# Development mode (minimal, no health checks)
python main.py

# Web GUI only
python web_gui_server.py

# Run standalone health tests
.\test_ollama_communication.ps1
```

### 5. Access Interfaces

- **Web GUI (Primary)**: Pokédex-style retro interface at `http://localhost:8080`
- **Frontend UI**: Modern interface at `http://localhost:5175`
- **Mobile Web Interface**: Responsive mobile UI at `http://localhost:8001`
- **API Server**: REST endpoints on `http://localhost:5000` (when api_server.py is running)
- **Ollama Backend**: AI model service at `http://localhost:11434`

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

### Amazon Q (Enhanced)

- Use `/help` in Q Chat for guidance
- Ask questions about ULTRON architecture and components
- Request code reviews with ULTRON-specific analysis
- Get security recommendations for ULTRON integrations
- **New**: "ai help create tool [name]" - Coordinate tool development
- **New**: "ai help review code" - Multi-AI code review
- **New**: "ai help optimize performance" - Performance optimization

### GitHub Copilot (Enhanced)

- Tab to accept suggestions
- `Ctrl+Right Arrow` to accept word-by-word
- `Alt+]` and `Alt+[` to cycle through suggestions
- **New**: Understands ULTRON tool patterns and suggests compatible implementations
- **New**: Provides ULTRON-specific error handling and logging patterns
- **New**: Suggests voice system integration for user-facing functions

### Continue Extension (New)

- Multi-model LLM support with ULTRON-optimized configurations
- MCP server orchestration for enhanced capabilities
- Codebase documentation awareness with ULTRON rules
- Context-aware code generation with project understanding
- **Usage**: Use `@codebase`, `@docs`, `@terminal` context providers

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

### System Health Checks

The `run.bat` launcher includes automated diagnostics. If you encounter issues:

1. **Check Startup Log**:
   ```bash
   Get-Content ultron_master_startup.log -Tail 50
   ```

2. **Review Test Results**:
   ```
   [TEST] Summary: Passed=5 Failed=0
   ```
   - If tests fail, see which specific test failed
   - Refer to `STARTUP_HEALTH_CHECKS.md` for troubleshooting

3. **Run Standalone Tests**:
   ```bash
   .\test_ollama_communication.ps1
   ```

### Common Issues

#### "Chat backend unavailable" or Connection Errors

**Symptoms**: "⚠️ System Alert: Chat backend unavailable"

**Quick Fix**:
```powershell
# 1. Restart Ollama service
Stop-Process -Name "ollama" -Force
.\run.bat

# 2. Verify Ollama is running
curl http://localhost:11434/api/tags

# 3. Check if model is loaded
ollama list | findstr "llava"

# 4. Check agent logs
Get-Content logs\brain.log -Tail 50
```

**Detailed Diagnostics**:
- Check port 11434 availability
- Verify model pulled: `ollama pull llava:7b`
- Review `ultron_master_startup.log` for health test failures
- Ensure sufficient RAM for model loading (8GB+ recommended)

#### Port Conflicts (8080, 5175, 11434)

**Symptoms**: "Port already in use" or "Address already in use"

**Fix**: The `run.bat` launcher now automatically kills conflicting processes. If issues persist:
```powershell
# Check what's using the port
Get-NetTCPConnection -LocalPort 8080,5175,11434

# Kill specific process
Stop-Process -Id <PID> -Force

# Or let run.bat handle it automatically
.\run.bat
```

#### Health Tests Failing

**Test 1 Failure (Service Availability)**:
- Ollama not running or crashed
- Port 11434 blocked by firewall
- Fix: Restart Ollama service

**Test 2 Failure (Model Availability)**:
- Model not downloaded
- Fix: `ollama pull llava:7b`

**Test 3/4 Failure (Generation/Chat)**:
- Model loading timeout
- Insufficient memory
- Fix: Wait for model warmup, check available RAM

**Test 5 Failure (Context Retention)**:
- Model not retaining context
- May still work for single-turn conversations
- Fix: Try different model or restart Ollama

### AI Tool Issues

1. **Sixth AI API Error**: Ensure VS Code launched with `--enable-proposed-api sixth.sixth-ai`
2. **Amazon Q Connectivity**: Check network settings and proxy configuration
3. **Copilot Not Working**: Verify authentication in VS Code settings
4. **Performance Issues**: Review file watcher exclusions

### Quick Fixes

```powershell
# Full system restart (cleans everything)
Stop-Process -Name "ollama", "python" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
.\run.bat

# Restart with all AI tools
& "$env:USERPROFILE\launch-vscode-ai.ps1" -WorkspacePath "." -WithProposedAPIs

# Check extension status
code --list-extensions --show-versions | findstr -i "amazon\|github\|sixth"

# Verify all services
Get-NetTCPConnection -LocalPort 8080,5175,11434 | Format-Table -AutoSize
```

### Getting Help

- 📖 **Full Documentation**: See `STARTUP_HEALTH_CHECKS.md` for detailed health check guide
- 🔍 **Test Results**: Check `OLLAMA_TEST_RESULTS.md` for test suite documentation
- 📝 **Logs**: Review service-specific logs in `logs/` directory
- 🤖 **AI Instructions**: See `.github/copilot-instructions.md` for development guidance

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

### Version 3.0.3 - January 15, 2025

**Major Update: AI Assistant Integration & Enhanced Development Workflow**

- ✅ **NEW**: Comprehensive AI Assistant Integration
  - Amazon Q enhanced with deep ULTRON architecture awareness
  - GitHub Copilot trained on ULTRON patterns and conventions
  - Continue extension with multi-model coordination and MCP integration
  - AI Development Coordinator tool for unified workflow management

- 🤖 **NEW**: Enhanced Voice System Integration
  - Multi-engine STT with automatic fallback (ElevenLabs → OpenAI → pyttsx3 → Web Speech)
  - Context-aware command processing with conversation memory
  - Intent classification with confidence scoring and confirmation dialogs
  - Reference resolution for natural language ("that thing", "yesterday", "it")
  - Enhanced GUI voice controls with real-time confidence display

- 🔧 **NEW**: Advanced Tool Ecosystem
  - Enhanced OCR tool with advanced image preprocessing
  - Windows system tool with natural language understanding
  - Browser MCP tool for web automation
  - Memory context tool for conversation history
  - Continue documentation integration tool
  - Amazon Q integration tool for development assistance

- 📚 **NEW**: Comprehensive Documentation System
  - Complete AI assistant integration rules in `.continue/rules/`
  - Project architecture documentation for codebase awareness
  - Coding standards and development patterns
  - Internal and external codebase integration guides
  - Common tasks and troubleshooting procedures

- 🚀 **Enhanced Capabilities**:
  - Natural language commands: "hey ultron open chrome and search for cars"
  - Context-aware conversations with memory persistence
  - Multi-modal interfaces with voice, GUI, and API integration
  - Real-time AI coordination for development tasks
  - Enhanced MCP server integration with browser automation

- 🔧 **Configuration Enhancements**:
  - Enhanced voice configuration with wake words and confidence thresholds
  - Multi-model Continue configuration optimized for ULTRON development
  - ULTRON-specific context providers for better AI understanding
  - Comprehensive MCP server setup for all integrations

### Version 3.0.2 - October 24, 2025

**Major Update: Automated Health Checks & System Validation**

- ✅ **NEW**: Comprehensive startup health check system in `run.bat`
  - 5 automated tests validate Ollama integration before service launch
  - Service availability, model availability, generation, chat, and context retention tests
  - All results logged to `ultron_master_startup.log` with timestamps
  - User prompt on test failures with option to continue or abort
  - Auto-continue when all tests pass

- ✅ **NEW**: Process cleanup at startup
  - Automatically kills existing ULTRON Python processes
  - Frees ports 8080, 5175 to prevent conflicts
  - 2-second cooldown period for clean shutdown

- ✅ **NEW**: Standalone test suite
  - `test_ollama_communication.ps1` - PowerShell test script for manual validation
  - Tests all 5 health checks independently
  - Color-coded pass/fail output with detailed metrics
  - Performance timing for each test

- 📖 **Documentation Updates**:
  - Added `STARTUP_HEALTH_CHECKS.md` - Complete health check system documentation
  - Added `OLLAMA_TEST_RESULTS.md` - Test results and validation guide
  - Updated `.github/copilot-instructions.md` - AI development guidelines
  - Enhanced README with troubleshooting section for common Ollama issues

- 🔧 **Improvements**:
  - Better error messages with specific troubleshooting steps
  - Detailed logging of all startup phases
  - Graceful handling of model loading timeouts (15s per test)
  - Port conflict detection and automatic resolution

- 🐛 **Fixes**:
  - Resolved port 5175 conflict issue with `frontend_server.py`
  - Fixed "Chat backend unavailable" false alarms from stale logs
  - Improved Ollama service detection and retry logic (5 attempts, 3s intervals)

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

