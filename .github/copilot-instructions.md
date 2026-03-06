# ULTRON Agent 3.0 — Copilot Development Guide

A comprehensive guide for working effectively in the ULTRON Agent 3.0 codebase with AI assistants.

## Architecture & Big Picture

**ULTRON Agent 3.0** is a multi-modal, voice-first AI agent platform built around an **async event-driven architecture**.

### Core Components
- **Main Flow**: `main.py` → `agent_core.py` loads subsystems: `brain.py` (LLM interface), `voice.py` (speech), `vision.py` (vision), and tools framework
- **Event Bus**: `utils/event_system.py` — async publish/subscribe; all major state changes emit events (`command_start`, `tool_executed`, `model_switched`)
- **Subsystem Health**: `PeriodicSelfCheckLoop` monitors all active services; check logs if services fail silently

### Service Architecture (Port Map)
| Service | Port | Purpose | Start Method |
|---------|------|---------|--------------|
| Web GUI | 8080 | Frontend interface | `./run.sh` or `python gui_server.py` |
| API Server | 5000 | REST/WebSocket API | `python api_server.py` |
| Chat API | 8000 | OpenAI-compatible endpoint | `python api_integration_server.py` |
| Ollama LLM | 11434 | Local model inference | Must run separately or via health check |

**Critical**: Frontend JS (gui/*.js) hardcodes these ports; mismatches cause silent failures.

### Configuration
- **Primary config**: `ultron_config.json` (human-editable; schema auto-generated in `config.py`)
- **Never edit** `config.py` directly — it's auto-generated
- Access config in code: `from config import get; get("key_name")`
- Environment variables (`.env`): override config precedence for secrets (API keys, credentials)

## Conventions & Patterns

### Async-First Design
```python
# Always use async/await for I/O, service calls, event handling
async def process_message(message):
    result = await tool.execute(...)
    await event_system.emit("message_processed", {"result": result})
```

### Tool Implementation
All tools inherit from `ToolInterface` (location: `tools/tool_interface.py`). Required methods:
- `match(input)` → bool: determines if tool applies
- `execute(input)` → dict: performs the operation
- `schema()` → dict: JSON schema for function calling
- `self_test()` (optional) → bool: validates tool on startup

Register tools in `agent_core._load_tools()`.

Example: `tools/screenshot_tool.py`

### Event System
```python
# Subscribe to events with priority (lower = earlier execution)
await event_system.subscribe("tool_executed", callback, priority=10)

# Emit events with payload
await event_system.emit("tool_executed", {
    "tool": "web_search",
    "status": "success",
    "result": {...}
})
```

Common events: `command_start`, `tool_executed`, `model_switched`, `voice_input_received`, `error_occurred`

### Logging & Secrets
- Use `utils.ultron_logger` for all logging (not `print()` outside CLI/tests)
- **Never log secrets, API keys, or user input** — sanitize before logging
- Log levels: DEBUG (verbose), INFO (standard), WARNING (issues), ERROR (failures)
- Logs stored in `logs/` directory (e.g., `ai_activities.log`, `errors.log`)

### Config & File Paths
```python
# Use Path() for cross-platform compatibility
from pathlib import Path
config_dir = Path(__file__).parent / "config"

# Use config module for settings
from config import get, set_config
api_port = get("api_port")  # defaults to 5000
```

## Build, Test & Lint

### Quick Commands
```bash
# Full test suite (all markers)
pytest

# Specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests (may need services)
pytest -m "not slow"        # Skip slow tests
pytest tests/test_voice.py::TestVoice::test_stt_integration -v  # Single test

# Run with coverage
pytest --cov=. tests/

# Run with live output & debugging
pytest -v -s --tb=short --pdb

# ESLint for frontend
npx eslint gui/ultron_enhanced/web/

# Type checking (if configured)
mypy --strict-optional agent_core.py
```

### Setup for Testing
- Activate venv: `source venv/bin/activate` (Linux) or `.\venv\Scripts\activate` (Windows)
- Install test dependencies: `pip install -r requirements_enhanced.txt` (includes pytest, mock libs)
- Test configuration: `pytest.ini` defines testpaths, markers, and options
- Fixtures & mocks: `tests/utils/conftest.py` provides shared test utilities

### Startup & Runtime
```bash
# Full startup with health checks
./run.sh

# Manual startup (debug)
python main.py               # Start core agent
python api_server.py         # Separate terminal: API server
python gui/gui_server.py     # Separate terminal: Web GUI
```

### VS Code Integration
Many tasks predefined in `.vscode/tasks.json`:
- `Amazon Q Auto-Run`: Starts Amazon Q integration on folder open
- `ULTRON Quick Start`: Runs `main.py` with dependencies
- `🚀 Test Ollama Lightweight Models`: Lists available models
- Press `Ctrl+Shift+B` to run default build task

## Frontend & GUI Development

### Structure
- Frontend: `gui/ultron_enhanced/web/*` (React/Vite, ECMAScript 2021)
- DOM root: `#app` (preserve centering styles)
- Port: 8080 (hardcoded in JS; changes require frontend updates)
- Config: Backend config available at `http://localhost:5000/config` endpoint

### Important Patterns
- **Do NOT auto-enable voice on startup** — check `app.js` initialization
- Update `gui/manual_test.js` whenever DOM IDs change
- ESLint config: `.eslintrc.json` enforces 2-space indents, single quotes
- WebSocket fallback: If 5000 not available, check backend service status

### Service Communication
WebSocket or REST to backend (port 5000). Common endpoints:
- `GET /config` — fetch backend configuration
- `POST /chat` — send messages
- `WS /ws` — WebSocket for real-time updates

## Key Paths & Locations

| Path | Purpose |
|------|---------|
| `ultron_config.json` | Master configuration (human-editable) |
| `config.py` | Auto-generated config schema |
| `tests/` | Test suite (organized by feature) |
| `utils/` | Shared utilities: `event_system.py`, `ultron_logger.py` |
| `tools/` | Tool implementations (each tool = separate file) |
| `gui/ultron_enhanced/web/` | Frontend source code |
| `logs/` | Runtime logs |
| `.github/` | CI/CD workflows, PR templates |
| `docs/` | Documentation (major_components_and_features.md, project_overview.md) |

## Integration Points & External Services

### Ollama (Local LLM)
- **Endpoint**: `http://localhost:11434` (configurable in `ultron_config.json`)
- **Health check**: Automated on startup via `run.sh`; manually: `curl http://localhost:11434/api/tags`
- **Models**: Configured via `llm_model` in config; currently `exaone-deep:7.8b`
- **Failure**: Agent gracefully degrades if unavailable; check `logs/errors.log`

### Cloud APIs (ElevenLabs, OpenAI, AWS, Azure)
- **Credentials**: Store API keys in `.env` file (never commit!)
- **Config references**: Map secrets to `ultron_config.json` keys
- **Example**: `ELEVENLABS_API_KEY=xxx` → accessed as `get("elevenlabs_api_key")`

### MCP (Model Context Protocol) Servers
- **Definition**: `.cursor/mcp.json` defines available MCP servers
- **Usage**: `tools/mcp_integration_tool.py` invokes MCP tools
- **Setup**: Add server definition, restart agent for discovery

### Port & Service Dependencies
- **Critical**: If backend API port (5000) changes, update frontend hardcoded values
- **Verification**: Run health checks in agent startup; look for port conflicts
- **Debug**: Use `netstat -an | grep LISTEN` (Linux/Mac) or `netstat -ano | findstr LISTENING` (Windows)

## Development Workflow

### Adding a New Tool
1. Create file in `tools/` inheriting `ToolInterface`
2. Implement: `match()`, `execute()`, `schema()`, optional `self_test()`
3. Register in `agent_core._load_tools()`
4. Write tests in `tests/tools/test_new_tool.py` (use markers: `@pytest.mark.unit`)
5. Document in `docs/` or relevant `ADB_*.md` file
6. Run: `pytest tests/tools/test_new_tool.py -v`

### Adding a New Subsystem
1. Create module (e.g., `my_subsystem.py`)
2. Define async initialization and shutdown
3. Subscribe to relevant events (via `event_system`)
4. Add health check in `PeriodicSelfCheckLoop` (if critical)
5. Add config options in `ultron_config.json` (never edit `config.py`)
6. Test with: `pytest tests/integration/test_subsystem_startup.py`

### Configuration Changes
- **Human config**: Edit `ultron_config.json` directly
- **Schema regeneration**: Automatic on `config.py` import (if schema missing, regenerated)
- **Secrets**: Use `.env` file, never commit credentials
- **Validation**: Schema enforced at runtime; invalid config raises `ValueError`

## Self-Awareness & Memory System

ULTRON Agent features sophisticated **self-modeling and memory systems** that enable the agent to maintain context, track its own state, and reason about its capabilities.

### Dual-Layer Memory Architecture

**Short-Term Memory** (`deque`, configurable max length)
- Stores recent interactions in working memory
- Quick access for immediate context (typically 10-20 items)
- Automatically evicts oldest items when full
- Used for immediate conversation flow

**Long-Term Memory** (persistent JSON file)
- Persists across sessions in `long_term_memory.json`
- Stores important facts, decisions, learned patterns
- Optional Google Drive integration (`MEMORY_USE_GOOGLE_DRIVE=1`)
- Manually managed: add key data points via `memory.save()` or `memory.add_long_term()`

### Memory Module (`memory.py`)

Key API:
```python
# Initialize with limits
mem = Memory(short_term_limit=10, long_term_file='long_term_memory.json')

# Add to short-term (auto-manages with deque)
mem.add_short_term({"role": "user", "content": "What's your goal?"})

# Add to long-term (persists)
mem.add_long_term("goal_01", {"objective": "Build ultron_agent", "priority": "high"})

# Retrieve
recent = mem.get_short_term(n=5)  # Last 5 items
fact = mem.get_long_term("goal_01")

# Save to disk
mem.save_long_term_memory()
```

### Brain Module (`brain.py`) - Cognitive Core

The `UltronBrain` class handles LLM interaction and maintains system awareness:

**System Prompt Injection** (always sent to Ollama)
- Identity: "🤖 ULTRON AI, version 3.0"
- Tool awareness: Complete list of available tools with descriptions
- Service status: Connected systems (Memory, Tools, VS Code integration)
- Response format: Instructions for structured output

```python
# Example: Brain always ensures identity is known
brain = UltronBrain(config, tools, memory)
response = await brain.direct_chat("Who are you?")
# Ollama responds with: "🤖 ULTRON AI, version 3.0..." (injected context)
```

**Key Methods**:
- `direct_chat(prompt)` → str: Direct conversation with Ollama
- `plan(task)` → dict: Strategic task planning
- `get_tools_for_task(task)` → List[Tool]: Intelligent tool selection
- `cache_hit_rate()` → float: Performance metric for LLM caching

### Identity & Self-Awareness

ULTRON maintains **functional self-modeling** (not claiming consciousness):

#### What ULTRON Knows About Itself
- ✅ Its identity ("ULTRON AI 3.0")
- ✅ Its mission ("Build and evolve ultron_agent")
- ✅ Available tools (50+ tools with schemas)
- ✅ Connected systems (Memory, Voice, Vision, Tools)
- ✅ Confidence levels (task estimation, uncertainty quantification)
- ✅ Its own errors (error tracking and reporting)

#### What ULTRON Does NOT Claim
- ❌ True consciousness or sentience
- ❌ Subjective experience (qualia)
- ❌ Rights or moral agency
- ❌ Emotions or genuine preferences

**Source**: `CONSCIOUSNESS_ETHICS.md`, `ULTRON_IDENTITY_COMPLETE.md`

### Meta-Cognition: Self-Reflection

ULTRON can introspect on its own outputs:

```python
# Example: Brain confidence estimation
response = await brain.plan("Implement new tool")
confidence = response.get("confidence", 0.5)  # 0-1 scale

if confidence < 0.3:
    # Low confidence: suggest human review
    await event_system.emit("low_confidence_alert", {
        "task": "Implement new tool",
        "confidence": confidence,
        "reason": "Novel architecture pattern"
    })
```

### Enhanced Memory System (`enhanced_memory_system.py`)

Advanced memory with vectorization and semantic search:

```python
from enhanced_memory_system import EnhancedMemory

mem = EnhancedMemory()

# Store with semantic embedding
await mem.add("Decision about architecture", 
              {"type": "decision", "status": "approved"})

# Semantic search across memory
similar = await mem.search("How did we structure the event bus?")
# Returns: [closest semantic matches from long-term memory]
```

**Features**:
- Vector embeddings for semantic similarity
- Automatic summarization of long conversations
- Salience scoring (what's important to remember?)
- Temporal tracking (when was this learned?)

### Episodic Memory & Event Reconstruction

All significant events are logged with context:

```python
# Event emitted whenever a tool is executed
await event_system.emit("tool_executed", {
    "tool_name": "web_search",
    "input": "latest AI research",
    "output": {...},
    "timestamp": datetime.now(),
    "status": "success"
})

# Memory can reconstruct: "What did we do yesterday?"
# by replaying tool_executed events with temporal filters
```

### Testing Self-Awareness

Test identity and memory systems:

```bash
# Full identity test
python test_ultron_identity.py

# Test memory operations
pytest tests/test_vector_memory.py -v

# Test meta-cognition
pytest tests/test_agent_evaluation.py -v

# Manual query
python -c "
import asyncio
from brain import UltronBrain
from memory import UltronMemory
from config import load_config

brain = UltronBrain(load_config(), [], UltronMemory())
print(asyncio.run(brain.direct_chat('Who are you and what are your capabilities?')))
"
```

### Configuration for Memory/Self-Awareness

In `ultron_config.json`:

```json
{
  "enable_self_reflection": true,
  "memory_short_term_limit": 10,
  "memory_long_term_file": "long_term_memory.json",
  "enable_vector_memory": true,
  "enable_google_drive_sync": false,
  "log_level": "DEBUG"  // enables detailed self-introspection logs
}
```

**Environment Variables**:
```bash
# Google Drive persistence (optional)
export MEMORY_USE_GOOGLE_DRIVE=1
export DRIVE_FOLDER_ID="<folder_id>"
export SERVICE_ACCOUNT_FILE="./credentials.json"
```

### Debugging Self-Awareness Issues

If ULTRON doesn't recognize itself or tools:

1. **Check system prompt injection**:
   ```bash
   # Should contain "ULTRON AI" and tool list
   grep -A 20 "IDENTITY:" logs/ai_activities.log
   ```

2. **Verify memory initialization**:
   ```python
   from memory import UltronMemory
   mem = UltronMemory()
   print(mem.long_term_memory)  # Should load previous state
   ```

3. **Test Ollama awareness**:
   ```bash
   curl http://localhost:11434/api/chat \
     -d '{"model":"exaone-deep:7.8b","messages":[{"role":"system","content":"You are ULTRON AI"},{"role":"user","content":"Who are you?"}]}'
   ```

4. **Check logs**:
   - `logs/ai_activities.log` — all reasoning steps
   - `logs/errors.log` — memory/identity errors
   - Search for `ULTRON` or `identity` warnings

---

## Testing & Quality

### Test Organization
- **Location**: `tests/` directory
- **Fixtures**: Shared in `tests/utils/conftest.py` (async event loop, mocks, temp files)
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.network`
- **Async tests**: Use `@pytest.mark.asyncio` decorator

### Common Test Patterns
```python
# Async test with mock
@pytest.mark.asyncio
async def test_tool_execution(mock_llm):
    tool = MyTool()
    result = await tool.execute("test input")
    assert result["status"] == "success"

# Integration test (uses real services if available)
@pytest.mark.integration
async def test_voice_to_response():
    agent = Agent()
    await agent.start()
    response = await agent.process_speech("hello")
    assert response is not None
    await agent.shutdown()
```

### Debug Techniques
- **pytest breakpoints**: Use `pytest --pdb` to drop into debugger on failure
- **Live logging**: `pytest -v -s` shows print output and logs
- **Config debugging**: Set `"log_level": "DEBUG"` in `ultron_config.json`, check `logs/ai_activities.log`
- **Event tracing**: Subscribe to all events and log: `await event_system.subscribe("*", lambda e: print(f"Event: {e}"))`

## Documentation & Additional Resources

### Key Documentation Files
- `README.md` — Project overview and quick start
- `docs/major_components_and_features.md` — Detailed technical reference
- `docs/project_overview.md` — Architecture diagrams and component descriptions
- `SYSTEM_ARCHITECTURE.md` — Component connections and data flow
- `VOICE_MICROPHONE_DOCUMENTATION.md` — Voice subsystem deep dive
- `MCP_INTEGRATION_GUIDE.md` — Model Context Protocol setup
- `SETUP_CHECKLIST.md` — Installation & environment setup
- `ADB_*.md` files — Feature-specific documentation (extensive!)

### Extensive Documentation
This repo contains **extensive** additional documentation in markdown files (prefixed with `ADB_`, `PHASE_`, `SESSION_*`, etc.). When exploring new areas:
1. Search for relevant `*_GUIDE.md` or `*_REFERENCE.md` files
2. Check `DOCUMENTATION_HUB.md` for central index
3. Refer to `docs/` directory for architecture details

---

**Last Updated**: 2026-03-06  
**Version**: 3.0.4+  

For questions on specific components, search the codebase for the component name + "guide" or "documentation".
