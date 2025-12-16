# ULTRON Agent Copilot Guide

## Architecture Overview
- **Multi-modal voice-first agent** with event-driven pub/sub architecture using `utils/event_system.py`
- **Service Isolation**: Components decoupled—Web GUI (8080), API Server (5000), Ollama (11434) communicate via event bus
- **Centralized Logging**: All components log to `logs/<component>.log` using `utils/ultron_logger` helpers
- **Data Flow**: `main.py` → `agent_core.py` → initializes `brain.py`, `voice.py`, `vision.py`, tools from `tools/`

## Startup & Configuration
- **Entry Point**: `python main.py` initializes agent; `run.bat` (Windows) or `./run.sh` (Ubuntu/Linux) orchestrates full stack (Ollama health checks, services, GUI)
- **Ubuntu Setup**: Run `./setup_ubuntu.sh` for automated installation; see `UBUNTU_SETUP.md` for detailed Linux instructions
- **Config Source**: `ultron_config.json` is single source of truth; use `USE_ENV_*` placeholders for secrets (e.g., `USE_ENV_ELEVENLABS_APIKEY`)
- **Config Loading**: `config.py` schema validates; **never edit** `config.py` directly—modify `ultron_config.json` instead
- **Health Checks**: Launch scripts run 5 Ollama tests (service, model load, text gen, chat API, context retention) logged to `ultron_master_startup.log` or `ultron.log`
- **Virtual Environment**: Ubuntu users must activate venv: `source venv/bin/activate` before running

## AI Models & LLM
- **Default Model**: `llava:7b` at `http://localhost:11434` (multimodal, vision-enabled)
- **Model Switching**: Update `ultron_config.json` or call `/api/model/switch` endpoint
- **Fallback Models**: `deepseek-r1:14b` (advanced reasoning, may timeout), qwen, AWS Bedrock (opt-in)
- **Context System**: `brain.py` injects memory, tools, capabilities into **all** Ollama models via unified context system

## Tool Development
- **Location**: Place tool classes in `tools/` root (avoid nested folders)
- **Base Class**: Inherit from `ToolInterface` in `tools/tool_interface.py`
- **Required Methods**:
  - `match(command: str) -> bool`: Check if command triggers this tool
  - `execute(command: str, **kwargs) -> str`: Perform tool action with error handling
  - `schema() -> Dict`: Return OpenAI-compatible function calling schema
  - Properties: `name`, `description`
- **Example Pattern**: See `tools/web_search_tool.py` for multi-engine search with caching
- **Logging**: Use `log_info("tool_name", msg)`, `log_error()`, `log_ai_decision()` from `utils/ultron_logger`
- **Diagnostics**: Decorate `execute()` with `@diagnostic_wrapper("tool_name", track_performance=True)`

## Event System
- **Subscribe/Publish**: Import from `utils/event_system.py`; supports priority-based subscribers
- **Common Events**: `command_start`, `command_complete`, `tool_executed`, `voice_realtime_text`, `model_switched`
- **Pattern**: `await event_system.emit("event_name", {"data": value})`; subscribers async-safe

## Logging & Security
- **Helpers**: `log_info(component, msg)`, `log_error()`, `log_ai_decision(component, msg, ai_model, confidence_score)`, `log_file_operation(component, msg, file_path, action)`
- **Sanitization**: Always use `security_utils.sanitize_log_input()` before logging user input
- **Secret Handling**: Never log raw API keys; `ultron_config.json` uses `USE_ENV_*` to reference environment vars

## Async/Concurrency
- **Default Pattern**: Favor async flows; `agent_core.py` initialization is fully async
- **Sync Wrappers**: Only add when GUI threads (e.g., Tkinter) require blocking calls
- **Event Loop**: Main loop in `agent_core.py`; avoid blocking with long-running sync ops

## GUI Development
- **Location**: `gui/ultron_enhanced/web/*` (Pokédex-themed interface)
- **Voice Safeguard**: **Never** auto-enable voice; `handleStartupAnnouncement()` in `app.js` must force `voiceEnabled = false`
- **Audio Queue**: Respect `dequeueSpeech()` early returns to prevent feedback loops (see `FIXES_SUMMARY_2025-10-24.md`)
- **Styling**: Do not modify `#app` centering styles; maintain existing layout

## Testing
- **Command**: `pytest --maxfail=1 --strict-markers`
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.network`
- **Setup**: `conftest.py` sets `ULTRON_TEST_MODE=1` env var
- **Best Practice**: Run fast unit tests first; mark integration tests requiring Ollama/external services

## MCP Integration
- **Config**: `.cursor/mcp.json` registers MCP servers (Langflow, browser, GitHub, filesystem, postgres, puppeteer)
- **Tools**: `tools/mcp_integration_tool.py`, `tools/mcp_enhanced_tool.py` provide programmatic access
- **Example**: Langflow MCP at `http://localhost:7860/api/v1/mcp` with API key injection

## Service Ports
- **Ollama**: 11434 (LLM backend)
- **API Server**: 5000 (`api_server.py`)
- **Web GUI**: 8080 (`web_gui_server.py`)
- **Chat**: 8000 (planned)
- **Mobile**: 8001 (planned)
- **SSH**: 2222 (opt-in)

## Diagnostics & Troubleshooting
- **Startup Logs**: `ultron_master_startup.log` (run.bat health checks)
- **AI Activity**: `logs/ai_activities.log` (model decisions, reasoning)
- **File Changes**: `logs/file_changes.log` (automated file operations)
- **Docs**: Start with `SYSTEM_ARCHITECTURE.md` (service topology), `DOCUMENTATION_HUB.md` (all guides), `VOICE_MICROPHONE_DOCUMENTATION.md` (audio setup)
