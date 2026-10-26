# ULTRON Agent 3.0 - AI Developer Instructions

## Project Architecture & Key Components

### Core System Design
This is a **multi-modal AI agent platform** with voice-first architecture, combining local LLMs (Ollama) with cloud APIs and a web-based GUI. The system follows an **event-driven, modular design** with centralized logging, AI model coordination, and plugin-based tool discovery.

**Critical Architectural Pattern**: Services run independently with event-based coordination via `utils/event_system.py`. Each component logs to `logs/<component>.log` using the centralized logger.

### Core Components
- **main.py**: Single entry point - minimal initialization, delegates to `agent_core.py` after signal handler setup
- **agent_core.py**: Primary integration hub. Initializes subsystems (config, voice, vision, tools), handles dynamic tool discovery from `tools/`, manages component lifecycle
- **brain.py**: AI reasoning engine with Ollama integration at `http://localhost:11434`, async planning, response caching, multi-model support
- **config.py**: Stub module - **ACTUAL CONFIG** is `ultron_config.json` (JSON format with `USE_ENV_*` pattern for secrets)
- **mcp.json**: **NEW** Model Context Protocol server configuration - defines external tools (browser automation, GitHub, filesystem, databases)
- **utils/ultron_logger.py**: **MANDATORY** centralized logging - use `log_info()`, `log_error()`, `log_ai_decision()`, `log_file_operation()`
- **utils/model_awareness.py**: **CRITICAL** AI coordination - MUST call `should_modify_file()` before file edits
- **utils/event_system.py**: Event bus for async pub/sub messaging between components
- **tools/**: Auto-discovered plugins inheriting `ToolInterface` with `match()`, `execute()`, `schema()` methods
- **tools/mcp_integration_tool.py**: **NEW** MCP server manager - provides unified access to external MCP-compatible tools

### GUI & Service Architecture
- **PRIMARY GUI**: `gui/ultron_enhanced/web/index.html` - Pokédex-style retro interface on port 8080
  - **CRITICAL**: Only edit files in `gui/ultron_enhanced/web/` directory
  - Core files: `index.html`, `app.js`, `styles.css`
  - DO NOT modify `#app` CSS (breaks centering) or `handleStartupAnnouncement()` (voice auto-enable)
- **WEB SERVER**: `web_gui_server.py` - Custom HTTP handler serving static GUI, WebSocket integration with agent
- **API SERVER**: `api_server.py` - Flask REST API on port 5000 with `/health`, `/command`, `/api/tools/*` endpoints
- **MOBILE INTERFACE**: `tools/mobile_web_interface_tool.py` - Flask app on port 8001
- **DEPRECATED GUIS**: All other GUI files (`gui_ultimate.py`, `gui_clean.py`) - DO NOT USE

## Developer Workflows

### Standard Development
```bash
# Production: Full system startup (Ollama + all services + health checks)
run.bat

# Development: Minimal agent only
python main.py

# Web GUI only
python web_gui_server.py

# VS Code tasks available:
# - "Start Ollama Service"
# - "Pull Models"
# - "Run Ultron Assistant"
```

**run.bat Health Checks** (v3.0):
The master launcher now includes 5 automated tests that validate Ollama integration before starting services:
1. **Service Availability**: Verifies Ollama HTTP endpoint responding
2. **Model Availability**: Confirms llava:7b is loaded
3. **Text Generation**: Tests basic generation capability (15s timeout)
4. **Chat API**: Validates conversational endpoint (15s timeout)
5. **Context Retention**: Ensures multi-turn memory works

All test results are logged to `ultron_master_startup.log`. If any test fails, user is prompted to continue or abort startup.

### Critical Development Rules
1. **BEFORE ANY FILE EDIT**:
   ```python
   from utils.model_awareness import should_modify_file
   should_proceed, reason, context = should_modify_file(
       "path/to/file.py", "refactor", "gpt-4"
   )
   if not should_proceed:
       # Stop and inform user
   ```

2. **MANDATORY LOGGING**:
   ```python
   from utils.ultron_logger import log_info, log_error, log_ai_decision
   log_info("component_name", "message", extra_data=value)
   log_ai_decision("brain", "Selected tool X", ai_model="llava:7b", confidence_score=0.95)
   ```

3. **PRIMARY GUI ONLY**: Edit `gui/ultron_enhanced/web/index.html` - ignore all other GUI files
   - **NEVER modify**: `#app` CSS element (breaks child centering)
   - **NEVER modify**: `handleStartupAnnouncement()` to enable voice automatically
   - **NEVER modify**: `dequeueSpeech()` queue processing flow (causes dual TTS)
   - See `VOICE_MICROPHONE_DOCUMENTATION.md` for voice system details

4. **TOOL DISCOVERY**: Place new tools in `tools/` directory - auto-discovered on startup

### Configuration Management
- **File**: `ultron_config.json` (JSON format, not Python)
- **Secrets**: Use `"key": "USE_ENV_KEYNAME"` pattern → reads from environment
- **Service Ports**:
  - 5000: API Server (`api_server.py`)
  - 8000: AI Chat (nvidia_enhanced_ultron.py)
  - 8080: Web GUI (`web_gui_server.py`)
  - 8001: Mobile Interface
  - 5175: Frontend UI (`frontend_server.py`)
  - 11434: Ollama LLM Backend
- **Default Model**: `llava:7b` (multimodal, vision-enabled, recommended for most tasks)
  - Set in both `ultron_config.json` and `run.bat`
  - Alternative models: `llama3.1`, `qwen3-coder:480b-cloud`, `deepseek-r1:14b`

## Project-Specific Patterns & Conventions

### Tool Development Pattern
All tools in `tools/` must inherit from `ToolInterface`:

```python
# tools/example_tool.py
from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error

class ExampleTool(ToolInterface):
    """Brief description of tool purpose"""

    @property
    def name(self) -> str:
        return "Example Tool"

    @property
    def description(self) -> str:
        return "Does something specific"

    def match(self, command: str) -> bool:
        """Check if command should trigger this tool"""
        keywords = ["example", "test", "demo"]
        return any(kw in command.lower() for kw in keywords)

    def execute(self, command: str, **kwargs) -> str:
        """Execute tool logic"""
        log_info("example_tool", f"Executing: {command}")
        try:
            # Tool implementation
            result = "Tool completed successfully"
            return result
        except Exception as e:
            log_error("example_tool", f"Error: {e}")
            return f"Error: {e}"

    @classmethod
    def schema(cls) -> dict:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "example_tool",
            "description": "Does something specific",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    }
                },
                "required": ["command"]
            }
        }
```

**Tool Auto-Discovery**: `agent_core.py` scans `tools/` directory at startup using `tool_loader.py` and registers all `ToolInterface` subclasses.

### Event System Usage
Components communicate via async pub/sub events:

```python
from utils.event_system import get_event_system

# Get event system instance
event_system = get_event_system()

# Subscribe to events (async)
async def handle_completion(data):
    print(f"Command completed: {data}")

await event_system.subscribe("command_complete", handle_completion)

# Emit events (async)
await event_system.emit("command_start", {"command": cmd, "timestamp": now})
```

**Common Events**: `command_start`, `command_complete`, `voice_realtime_text`, `voice_speak_start`, `tool_executed`

### Async/Await Patterns
Most core operations are async for responsiveness:

```python
# In agent_core.py and brain.py
async def initialize(self):
    """Async initialization of components"""
    await self.event_system.emit("agent_init_start", {})
    # Initialize components
    await self.brain.initialize()

# Sync wrappers for GUI compatibility
def start_gui(self):
    """Sync wrapper for GUI thread"""
    asyncio.run(self.gui.run_gui())
```

**Timeouts**: Default 30s for network operations (configurable in brain.py)

### Voice Integration
Voice system follows a priority fallback chain:

```python
# Configuration in ultron_config.json
{
  "voice_engine": "elevenlabs",  # Primary
  "stt_engine": "whisper",       # Speech-to-text
  "tts_engine": "elevenlabs",    # Text-to-speech
  "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY"
}

# Fallback chain: ElevenLabs → pyttsx3 → Console output
# Thread-safe async voice operations in voice.py
```

**Voice Events**: `voice_realtime_start`, `voice_realtime_text`, `voice_speak_start`, `voice_speak_error`

## Integration Points & External Dependencies

### AI Services
- **Ollama**: Primary LLM backend at `http://localhost:11434` (local inference)
  - Configure in `ultron_config.json`: `"ollama_base_url": "http://localhost:11434"`
  - Model switching via `/api/model/switch` endpoint
- **OpenAI**: Optional fallback via `tools/openai_tools.py`
- **ElevenLabs**: Voice synthesis/recognition (requires API key)
- **NVIDIA NIM**: Enhanced suggestions via `nvidia_nim_router.py` (experimental, optional)
- **Azure Cognitive**: Text analytics, LUIS, Speech (experimental, optional)
- **Mesh Transformer**: GPT-J/GPT-NeoX integration (experimental, optional)

### Python Dependencies
Key libraries used throughout:
- **Flask**: Primary API server framework (`api_server.py`) - **STABLE, DO NOT MIGRATE**
- **aiohttp**: Async HTTP client (brain.py, tool communication)
- **SpeechRecognition**: Local STT fallback
- **PyAutoGUI**: System automation tool (`tools/pyautogui_tool.py`)
- **asyncio**: Core async framework
- **pytest**: Testing framework with strict configuration

### External Services Health Checks
Services must be running for full functionality:
1. **Ollama**: Check via `curl http://localhost:11434/api/tags`
2. **Web GUI**: Check port 8080 availability before `web_gui_server.py` starts
3. **API Server**: Check port 5000 for `/health` endpoint

## Key Files & Testing

### Core Entry Points
- `main.py` - Application entry (136 lines)
- `run.bat` - Production launcher (212 lines, PowerShell/Batch hybrid)
- `agent_core.py` - Agent initialization (899 lines)
- `brain.py` - AI reasoning (1017 lines)
- `ultron_config.json` - Configuration file

### Service Files
- `web_gui_server.py` - Web interface server (1036 lines)
- `api_server.py` - REST API (246 lines)
- `nvidia_enhanced_ultron.py` - AI chat server
- `voice.py` - Voice processing system

### Tool Ecosystem
Key tools in `tools/`:
- `tool_interface.py` - Abstract base class (44 lines)
- `tool_loader.py` - Auto-discovery system
- `dynamic_code_executor.py` - Sandboxed code execution
- `pyautogui_tool.py` - System automation
- `web_scraping_tool.py` - Web data extraction
- `mobile_web_interface_tool.py` - Mobile web UI

### Documentation Directories
- **Visual Studio Code**: `.vscode/` - Launch configurations, tasks, settings
- **Continue.dev Rules**: `.continue/rules/` - Agent mode codebase awareness rules (7 files, 3000+ lines)
  - `project-architecture.md` - System structure and patterns
  - `coding-standards.md` - Python style and best practices
  - `internal-documentation.md` - Company documentation links
  - `external-codebases.md` - Framework and library references
  - `common-tasks.md` - Step-by-step task guides
  - `github-copilot-integration.md` - Multi-AI assistant coordination
  - `ultron-tools-reference.md` - Tools, services, MCP servers reference
- **Logs**: `logs/` - Service-specific log files

### Testing
Testing framework: **pytest** with strict configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts = --strict-markers --maxfail=1 --tb=short -x
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    network: Tests requiring network access
```

**Test Environment**: `conftest.py` sets `ULTRON_TEST_MODE=1`, limits test collection to 10 tests max to prevent infinite loops during test discovery (safety measure for CI/CD)

**Running Tests**:
```bash
# Run all tests
pytest

# Run specific markers
pytest -m unit
pytest -m "not slow"

# Run with coverage
pytest --cov=. --cov-report=html
```

## Development Best Practices

### Code Organization
- **Separation of Concerns**: Each service runs independently, communicates via events
- **Error Boundaries**: Comprehensive try/catch with centralized logging
- **Resource Cleanup**: Proper shutdown handling in `main.py` signal handlers
- **Configuration First**: Load config before initializing any components

### Performance Considerations
- **Caching**: Response caching in `brain.py` for repeated queries
- **Async Operations**: Non-blocking I/O for all network calls (aiohttp, asyncio)
- **Memory Management**: Monitor via `utils/performance_profiler.py`
- **Background Processing**: Long-running tasks use `utils/task_scheduler.py`

### Security Patterns
```python
from security_utils import sanitize_log_input, sanitize_html_output, validate_file_path

# Input sanitization
log_error("component", sanitize_log_input(user_input))

# Output sanitization for web
html_safe = sanitize_html_output(ai_response)

# File path validation
if validate_file_path(requested_path):
    # Proceed with file operation
```

- **API Key Management**: Use `USE_ENV_*` pattern in config, never commit secrets
- **Error Logging**: Sanitized error messages without sensitive data
- **Network Security**: 30s timeout, retry logic for external APIs

## Common Development Tasks

### Adding New Tools
1. Create `tools/my_new_tool.py` inheriting from `ToolInterface`
2. Implement required methods: `name`, `description`, `match()`, `execute()`, `schema()`
3. Add logging via `utils.ultron_logger`
4. Restart agent - tool auto-discovered

### Adding Voice Features
1. Configure ElevenLabs API key in `ultron_config.json`:
   ```json
   {
     "voice_enabled": true,
     "elevenlabs_api_key": "USE_ENV_ELEVENLABS_APIKEY"
   }
   ```
2. Set environment variable: `export ELEVENLABS_APIKEY=your_key`
3. Use `voice.py` methods: `speak()`, `listen()`, `start_realtime()`
4. Handle fallbacks gracefully (pyttsx3 → console)
5. **IMPORTANT**: See `VOICE_MICROPHONE_DOCUMENTATION.md` for complete voice system architecture, TTS queue processing, and troubleshooting

### Voice System Critical Rules (DO NOT VIOLATE):
1. **NEVER auto-enable voice** - User must click microphone button manually
2. **NEVER modify `dequeueSpeech()` without understanding TTS queue flow** - Causes dual TTS
3. **ALWAYS use early `return;` after successful TTS playback** - Prevents fallback execution
4. **NEVER remove `this.voiceEnabled = false` from `handleStartupAnnouncement()`**
5. **Voice/mic functionality is CRITICAL** - Test thoroughly after any changes to `app.js`
   ```
2. Set environment variable: `export ELEVENLABS_APIKEY=your_key`
3. Use `voice.py` methods: `speak()`, `listen()`, `start_realtime()`
4. Handle fallbacks gracefully (pyttsx3 → console)

### Adding API Endpoints
1. Add routes to `api_server.py` (Flask):
   ```python
   @app.route("/api/my_endpoint", methods=["POST"])
   @require_auth
   def my_endpoint():
       if not AGENT_INSTANCE:
           return jsonify({"error": "Agent not initialized"}), 500
       data = request.get_json()
       result = AGENT_INSTANCE.my_method(data)
       return jsonify({"result": result}), 200
   ```
2. Integrate with event system for cross-service communication
3. Add health check if long-running

### Debugging Issues
1. **Check Logs**: Service-specific logs in `logs/` directory
   - `logs/agent_core.log` - Agent initialization
   - `logs/brain.log` - AI reasoning
   - `logs/ai_activities.log` - AI decisions
   - `logs/file_changes.log` - File operations
   - `ultron_master_startup.log` - Startup health checks and test results

2. **Use VS Code Debugger**: Launch configurations in `.vscode/launch.json`

3. **Monitor Events**:
   ```python
   # Add event logging
   await event_system.subscribe("*", lambda e: print(f"Event: {e}"))
   ```

4. **Performance Metrics**: Check `utils/performance_profiler.py` outputs

5. **Startup Health Checks**: Review `ultron_master_startup.log` for test results:
   ```
   [TEST] Summary: Passed=5 Failed=0
   ```
   If tests fail, check which specific test failed and see troubleshooting guide below

### Switching AI Models
1. **Via Config**: Edit `ultron_config.json`:
   ```json
   {"llm_model": "deepseek-r1:14b"}
   ```

2. **Via API**:
   ```bash
   curl -X POST http://localhost:5000/api/model/switch \
     -H "Content-Type: application/json" \
     -d '{"model": "llama3.1"}'
   ```

3. **Validate**: Run `python model_awareness_validator.py <model_name>`

## Model Awareness & CI/CD

### Model Awareness System
Before modifying files, the system checks if the AI model is aware of the codebase:

```python
from utils.model_awareness import should_modify_file, check_file_context

# Check if modification should proceed
should_proceed, reason, context = should_modify_file(
    file_path="brain.py",
    modification_type="refactor",
    ai_model="llava:7b"
)

if not should_proceed:
    print(f"❌ Modification blocked: {reason}")
    return

# Get file context for informed decisions
context = check_file_context("agent_core.py")
# Returns: recent_changes, dependencies, related_files, stability_score
```

**Critical Files** (require extra caution):
- `agent_core.py`, `brain.py`, `config.py`, `main.py`, `ultron_config.json`, `run.bat`

### CI/CD Integration: Ultron Command Runner
**Status**: ✅ **IMPLEMENTED** - Active GitHub Actions workflow at `.github/workflows/ultron_agent.yml`

The system provides safe remote code edits via `/ultron` commands in GitHub issues and PRs:

**Usage in GitHub Issues/PRs**:
```yaml
/ultron edit
file: brain.py
intent: "Extract plan() substeps into pure functions"
change:
  type: replace_with_context
  before: |
    def plan(self, ...):
        # existing logic
  after: |
    def plan(self, ...):
        return self._execute_plan(self._plan_steps(...))
tests: true
```

**Implementation Details**:
- **Workflow File**: `.github/workflows/ultron_agent.yml`
- **Command Parser**: `scripts/ultron_ci/command_runner.py`
- **Model Awareness**: Integrated with `utils/model_awareness.py`
- **Logging**: All actions logged to `logs/ai_activities.log`, `logs/file_changes.log`

**Guardrails**:
- ✅ Model awareness checked before application
- ✅ All edits logged with full context
- ✅ Changes create PRs for review (reversibility)
- ✅ Optional `tests: true` runs pytest suite
- ✅ Uses `GITHUB_TOKEN` with minimal permissions
- ✅ Artifacts uploaded for audit trail

**Workflow Triggers**: Issue comments, PR reviews, manual dispatch

## Logging Requirements (MANDATORY)

All components MUST use centralized logging:

```python
from utils.ultron_logger import log_info, log_error, log_ai_decision, log_file_operation

# Standard logging
log_info("component_name", "Initialization complete", config=config_dict)
log_error("component_name", f"Failed to connect: {error}", exception=e)

# AI-specific logging
log_ai_decision(
    component="brain",
    message="Selected tool: web_search",
    ai_model="llava:7b",
    confidence_score=0.92,
    reasoning="User query contains 'search' keyword"
)

# File operation logging
log_file_operation(
    component="auto_patch",
    message="Applied patch to enhance performance",
    file_path="tools/my_tool.py",
    action="patch_applied",
    patch_size=45
)
```

**Log Levels**: INFO (default), ERROR, WARNING, DEBUG

## Known Issues & Gotchas

1. **Port Conflicts**: `main.py` checks port 8080 availability before starting `web_gui_server.py`
2. **Config Confusion**: `config.py` is a stub - actual config is `ultron_config.json`
3. **GUI Deprecation**: Many GUI files exist but only `gui/ultron_enhanced/web/index.html` is active
4. **Tool Discovery**: Tools must be in `tools/` directory root - subdirectories not scanned
5. **Async Context**: Most operations are async - use `asyncio.run()` for sync entry points
6. **Model Timeouts**: `deepseek-r1:14b` has known timeout issues - use `llava:7b` or `qwen3-coder:480b-cloud`

## Recent Critical Fixes (2025-10-24)

### Voice Feedback Loop Prevention
**Issue**: Microphone was recording ULTRON's TTS output and looping it back as input
**Fix Applied**:
- Full destruction of recognition instance before TTS: `this.recognition = null`
- 200ms microphone release delay before audio playback
- Increased post-TTS delay from 500ms to 1000ms
- Applied to both API TTS and browser TTS fallback

**Files Modified**: `gui/ultron_enhanced/web/app.js` (Lines 1818-1935)

**Critical Takeaway**: Voice recognition must be COMPLETELY stopped and destroyed before TTS playback begins. A 1-second delay after TTS finishes ensures no feedback loop occurs.

### GUI Layout & Positioning
**Issue**: Footer and GUI elements not properly positioned/centered
**Fix Applied**:
- `.ultron-footer-status`: Changed from `position: relative` to `position: fixed; bottom: 0;`
- `#app` element: Reverted flex properties that broke child centering
- `.start-screen`: Added full-screen fixed positioning with flexbox centering

**Files Modified**: `gui/ultron_enhanced/web/styles.css` (Lines 2320, 2329, 2764, 964)

### Voice System Fixes
**Issue 1**: Voice auto-enabled on startup despite user preference
**Fix Applied**:
- `handleStartupAnnouncement()`: Force `this.voiceEnabled = false` on startup
- `renderDashboardSnapshot()`: Removed auto-enable logic from server status

**Issue 2**: Dual TTS - Both API and browser TTS playing simultaneously
**Root Cause**: `finally` block in `dequeueSpeech()` always ran, processing queue even after successful API TTS
**Fix Applied**:
- Added early `return;` statements after successful TTS playback
- Moved queue processing into `onended`/`onend` callbacks
- `finally` block only runs if BOTH TTS methods fail

**Files Modified**: `gui/ultron_enhanced/web/app.js` (Lines 360, 520, 1841)

**Critical Takeaway**: Voice/microphone functionality is FULLY OPERATIONAL after these fixes. Any further modifications to `app.js` voice methods MUST preserve:
1. Manual voice activation (no auto-enable)
2. Early returns in TTS queue processing
3. Microphone pause/resume during TTS playback

**Documentation**: See `VOICE_MICROPHONE_DOCUMENTATION.md` and `FIXES_SUMMARY_2025-10-24.md` for complete details.

## Known Issues & Gotcas (Legacy)

## Troubleshooting Guide

### Ollama Backend Issues ("Chat backend unavailable")

**Symptoms**: "⚠️ System Alert: Chat backend unavailable" or connection errors

**Quick Diagnostics**:
```powershell
# 1. Check if Ollama is running
curl http://localhost:11434/api/tags

# 2. Check Ollama process
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}

# 3. Test model availability
ollama list | findstr "llava"

# 4. Check agent logs
Get-Content logs\brain.log -Tail 50
```

**Common Fixes**:

1. **Restart Ollama Service**:
   ```powershell
   # Kill existing processes
   Stop-Process -Name "ollama" -Force

   # Restart via run.bat
   .\run.bat
   ```

2. **Verify Model Configuration**:
   - Check `ultron_config.json`: `"llm_model": "llava:7b"`
   - Check `run.bat`: `OLLAMA_MODEL=llava:7b`
   - Ensure both match and model is pulled

3. **Test Direct Ollama Connection**:
   ```powershell
   # Test generation
   curl -X POST http://localhost:11434/api/generate `
     -H "Content-Type: application/json" `
     -d '{"model": "llava:7b", "prompt": "test", "stream": false}'
   ```

4. **Check for Port Conflicts**:
   ```powershell
   # Verify port 11434 is available
   Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue
   ```

5. **Review Agent Connection Settings**:
   - Verify `brain.py` timeout settings (default: 30s)
   - Check `ollama_base_url` in config matches actual service
   - Look for connection errors in `logs/brain.log`

**Advanced Troubleshooting**:
- **High Memory Usage**: Ollama may be out of memory - restart or use smaller model
- **Model Loading Failures**: Re-pull model: `ollama pull llava:7b`
- **Network Proxy Issues**: Check if corporate proxy blocks localhost:11434
- **Antivirus Interference**: Whitelist Ollama executable and port 11434

**Recovery Steps**:
```powershell
# Full system restart
Stop-Process -Name "ollama", "python" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
.\run.bat
```

---

## Documentation Index

### Core Documentation
- **Developer Guide**: This file (`.github/copilot-instructions.md`)
- **Documentation Hub**: `DOCUMENTATION_HUB.md` - Central index for all resources
- **Continue.dev Integration**: `CONTINUE_INTEGRATION_COMPLETE.md` - Agent mode rules system
- **Copilot + Continue.dev**: `COPILOT_CONTINUE_INTEGRATION.md` - Multi-AI assistant coordination
- **MCP Integration**: `MCP_INTEGRATION_GUIDE.md` - Model Context Protocol servers setup and usage
- **Voice System**: `VOICE_MICROPHONE_DOCUMENTATION.md` - Complete voice/microphone system guide
- **System Architecture**: `SYSTEM_ARCHITECTURE.md` - Service connections, ports, data flow
- **Setup Guide**: `SETUP_CHECKLIST.md` - Step-by-step installation and configuration
- **Recent Fixes**: `FIXES_SUMMARY_2025-10-24.md` - Latest bug fixes and improvements

### Internal Documentation Links
- **API Documentation**: https://internal.docs/api - REST API endpoints and usage
- **Architecture Guide**: https://internal.docs/architecture - System design and patterns
- **Deployment Process**: https://internal.docs/deployment - Production deployment procedures

### Quick Reference
- **Inline Comments**: Critical code sections now have dependency comments
  - `gui/ultron_enhanced/web/app.js` - Voice system comments (Lines 383, 1686, 1873)
  - `gui/ultron_enhanced/web/styles.css` - CSS critical warnings (Lines 2320, 2779)
- **Startup Logs**: `ultron_master_startup.log` - Health check results
- **Component Logs**: `logs/<component>.log` - Service-specific logs
- **MCP Quick Reference**: `MCP_QUICK_REFERENCE.md` - MCP command examples

### Architecture Diagrams
See `SYSTEM_ARCHITECTURE.md` for:
- System component diagram
- Port dependency chart
- Service startup sequence
- Command execution flow
- Voice system data flow

---

*This document reflects the current state of ULTRON Agent 3.0 as of October 2025. Update as architecture evolves.*
