# ULTRON Agent 3.0 — Codex Editor Instructions

Complete development guide for working with ULTRON in Codex (powered by Amazon Q, OpenAI, and local models).

## Quick Start

**Codex Configuration**: `.codex/config.yaml` defines models, prompts, and orchestration.

**Key Models**:
- **Amazon Q** (primary) — Local Ollama orchestration with Qwen 2.5 Coder
- **Ultron (GPT-4)** — Enhanced reasoning and refactoring
- **Local Models** — Qwen 2.5 (coding), DeepSeek-R1 (reasoning)

---

## Architecture & System Context

**ULTRON Agent 3.0** is a multi-modal, voice-first AI agent platform with:

### Core Architecture
- **Main Entry**: `main.py` → `agent_core.py` loads subsystems
- **Event Bus**: `utils/event_system.py` (async pub/sub for all state changes)
- **Brain Module**: `brain.py` (LLM interface with Ollama, system prompt injection)
- **Memory**: Dual-layer (short-term deque + long-term persistent JSON)
- **Tools**: 50+ tools in `tools/` directory, each inheriting `ToolInterface`

### Service Architecture
| Service | Port | Purpose | Start |
|---------|------|---------|-------|
| Web GUI | 8080 | React/Vite frontend | `./run.sh` or `python gui_server.py` |
| API Server | 5000 | REST/WebSocket API | `python api_server.py` |
| Chat API | 8000 | OpenAI-compatible endpoint | `python api_integration_server.py` |
| Ollama LLM | 11434 | Local model inference | Must run separately |

### Configuration
- **Primary Config**: `ultron_config.json` (human-editable, schema auto-generated)
- **Never Edit**: `config.py` (auto-generated from schema)
- **Secrets**: Store in `.env` (API keys, credentials)
- **Access Config**: `from config import get; get("key_name")`

---

## Codex Workflows for ULTRON Development

### ⚠️ BEFORE YOU START: Known Issues

**ULTRON 3.0 is sophisticated but fragmented:**
- Multiple entry points (main.py, web_gui_server.py, api_server.py)
- Multiple GUI implementations (web_gui, gui_ultimate, pokedex_gui)
- Multiple API servers and memory systems
- 80+ tools but unclear coverage/maintenance
- 300+ docs but many outdated

**Expect some silent failures** due to import conflicts or version mismatches. When something breaks, check:
1. Which entry point/GUI is running?
2. Are multiple versions conflicting (agent_core.py locations)?
3. Which logger is being used (ultron_logger vs loguru)?

### Workflow 1: Code Refactoring (Ultron Model)

**Use Case**: Improve code structure, performance, or readability

```yaml
# In Codex, select code block and use:
Model: Ultron (GPT-4)
Prompt: "Ultron Edit"
Temperature: 0.85 (creative but focused)
```

**What It Does**:
- Rewrite for performance & clarity
- No explanations, code-only output
- Respects ULTRON patterns (async, event-driven)
- Maintains error handling & logging

**Best For**:
- Refactoring Python functions
- Optimizing async/await patterns
- Improving tool implementations
- Code cleanup & consolidation

### Workflow 2: Local Model Orchestration (Amazon Q)

**Use Case**: Fast, local inference without API calls

```yaml
# In Codex, select code block and use:
Model: Amazon Q
Prompt: "Amazon Q Orchestrate"
Temperature: 0.2 (deterministic)
```

**What It Does**:
- Routes to appropriate local model (Qwen for coding, DeepSeek-R1 for reasoning)
- Executes via `auto_orchestrator.py`
- Returns results without leaving your machine
- Respects `.codex/config.yaml` model selection

**Best For**:
- Quick completions while coding
- Testing code without API costs
- Local-only development (offline)
- Batch processing

### Workflow 3: Code Analysis & Reasoning

**Use Case**: Understanding complex patterns, debugging, design decisions

```yaml
# In Codex, select code block and use:
Model: Ultron (GPT-4)
Prompt: Custom reasoning prompt
Temperature: 0.85
```

**Example Prompt**:
```
Analyze this code and explain:
1. What event types are emitted?
2. How does error handling work?
3. What edge cases should we test?
Respond with markdown analysis + code examples.
```

**Best For**:
- Debugging complex async flows
- Understanding tool interactions
- Design pattern analysis
- Performance bottleneck identification

---

## Codex Models & Temperature Guidelines

### Model Selection

**Amazon Q (Local)**
- ✅ Fast, free, offline
- ✅ Excellent for Python/coding
- ✅ Good for completions & refactoring
- ❌ Limited reasoning, smaller context
- **Use**: Quick edits, completions, local work

**Ultron (GPT-4)**
- ✅ Advanced reasoning & analysis
- ✅ Larger context window (8K)
- ✅ Better at complex architectural decisions
- ❌ API costs, requires network
- **Use**: Design decisions, complex debugging, refactoring

**Local Models** (via Ollama)
- ✅ Zero cost, no API calls
- ✅ Private (stays on machine)
- ✅ Qwen 2.5 Coder excellent for Python
- ✅ DeepSeek-R1 for deep reasoning
- ❌ Slower than cloud, limited reasoning
- **Use**: Initial drafts, testing, offline work

### Temperature & Config

| Task | Model | Temp | Max Tokens | Purpose |
|------|-------|------|-----------|---------|
| Code completion | Amazon Q | 0.2 | 256 | Predictable, focused output |
| Bug fixing | Ultron | 0.3 | 2048 | Deterministic, good reasoning |
| Refactoring | Ultron | 0.85 | 4096 | Creative improvements |
| Brainstorming | Ultron | 0.9 | 4096 | Diverse ideas & patterns |
| Reasoning | DeepSeek-R1 | 0.5 | 4096 | Deep analysis |

---

## ULTRON Development Patterns for Codex

### Pattern 1: Tool Implementation

When creating new tools in `tools/`, Codex should know:

```python
# Required structure:
from tools.tool_interface import ToolInterface

class MyTool(ToolInterface):
    async def match(self, input: str) -> bool:
        """Return True if this tool applies to input"""
        pass
    
    async def execute(self, input: str) -> dict:
        """Execute the tool, return results"""
        pass
    
    def schema(self) -> dict:
        """Return JSON schema for function calling"""
        pass
    
    async def self_test(self) -> bool:
        """Optional: verify tool works on startup"""
        pass

# Tool is AUTO-DISCOVERED by tool_loader.py - NO manual registration needed!
# Just add your file to tools/ and restart agent
```

**How Tool Discovery Works:**
- `agent_core.py` calls `tool_loader.py` during init
- `tool_loader.py` scans `tools/` directory for .py files
- Each file is imported and tools are auto-instantiated
- No manual registration needed (this is new in v3.0!)

**Codex Prompt**:
```
Generate a new tool in tools/ that:
- Inherits ToolInterface
- Implements match(), execute(), schema()
- Handles errors gracefully
- Logs actions via ultron_logger
- Follows async-first patterns
- Include self_test() for validation
Remember: Tool will be auto-discovered by tool_loader.py
```

### Pattern 2: Event System Integration

When emitting events or subscribing to them:

```python
# Emit events:
await event_system.emit("tool_executed", {
    "tool": "my_tool",
    "input": input_data,
    "output": result,
    "timestamp": datetime.now(),
    "status": "success"
})

# Subscribe to events:
await event_system.subscribe("tool_executed", callback, priority=10)

# Common events: command_start, tool_executed, model_switched, 
# voice_input_received, error_occurred, memory_updated
```

**Codex Prompt**:
```
Add event emission to this function:
- Emit on start: command_start
- Emit on success: {event_name}
- Emit on error: error_occurred
Use ultron_logger for logging
Include timestamp and status
```

### Pattern 3: Configuration Management

For config changes:

```python
# Read config:
from config import get, set_config
api_port = get("api_port")  # Get value

# Modify config:
set_config("key", value)  # Set value
# Note: Never edit config.py directly

# Environment override:
import os
api_key = os.getenv("OPENAI_API_KEY") or get("openai_api_key")
```

**Codex Prompt**:
```
Update this code to use config management:
- Read settings from ultron_config.json
- Support environment variable overrides
- Use from config import get, set_config
- Handle missing keys with defaults
- Log config changes via ultron_logger
```

### Pattern 4: Async-First Design

For all I/O operations:

```python
# ✅ Correct:
async def process_data(item):
    result = await tool.execute(item)
    await event_system.emit("processed", {"result": result})
    return result

# ❌ Avoid:
def process_data(item):
    result = tool.execute(item)  # Blocks!
    return result
```

**Codex Prompt**:
```
Convert this function to async:
- Make function async def
- Use await for all I/O (tools, services, events)
- Use asyncio.gather() for parallel operations
- Handle cancellation gracefully
- Maintain error handling
```

### Pattern 5: Memory Operations

For persistent state & context:

```python
# Short-term (working memory):
mem.add_short_term({"role": "user", "content": message})
recent = mem.get_short_term(n=5)

# Long-term (persistent):
mem.add_long_term("goal_id", {"objective": "...", "priority": "high"})
fact = mem.get_long_term("goal_id")
mem.save_long_term_memory()

# Semantic search (enhanced memory):
similar = await enhanced_mem.search("How did we structure X?")
```

**Codex Prompt**:
```
Add memory integration to track:
- Conversation history (short-term)
- Important decisions (long-term)
- Allow semantic search for past context
Use memory.py and enhanced_memory_system.py
Include save operations for persistence
```

---

## Debugging with Codex

### Workflow: Debug Production Issue

**Step 1**: Select error in logs or code
```
File: logs/errors.log (or code with bug)
Use Model: Ultron (GPT-4)
```

**Step 2**: Use Codex prompt:
```
Analyze this error and provide:
1. Root cause analysis
2. Code changes needed (if any)
3. Test cases to verify fix
4. Related files to check
Include error logs, stack traces, and context.
```

**Step 3**: Review, apply, test
```bash
# Test fix:
pytest tests/test_module.py -v --pdb

# Run agent:
python main.py

# Check logs:
tail -f logs/errors.log
```

### Workflow: Optimize Performance

**Select code** → Codex:
```
Profile this code for performance:
1. Identify bottlenecks
2. Suggest optimizations (async, caching, etc.)
3. Provide refactored code
4. Include performance metrics

Current: O(n²) → Target: O(n) or better
Constraints: Must maintain event logging, error handling
```

---

## Codex Prompts for Common Tasks

### Add Logging
```
Add comprehensive logging to this function:
- Use ultron_logger instead of print()
- Log inputs (sanitized, no secrets)
- Log decision points
- Log errors with stack trace
- Include performance metrics (duration)
- Use log_level: DEBUG for details
```

### Add Error Handling
```
Enhance error handling:
- Import error handlers from utils.error_handlers
- Handle network timeouts gracefully
- Retry logic for transient failures
- Fall back to local alternatives
- Emit error_occurred events
- Log errors to logs/errors.log
- Return safe defaults
```

### Add Tests
```
Generate comprehensive tests for this function:
- Use pytest with markers (@pytest.mark.unit, .integration)
- Test happy path + edge cases + error cases
- Mock external dependencies
- Use fixtures from tests/utils/conftest.py
- Verify event emission if applicable
- Test async operations properly
- Include performance assertions
```

### Add Documentation
```
Generate docstring and comments:
- Include function purpose and return type
- Document parameters (including types)
- List exceptions that can be raised
- Provide usage examples
- Reference related functions
- Note async behavior
- Document config/environment dependencies
```

---

## Codex Configuration Tips

### Customize Prompts in `.codex/config.yaml`

```yaml
prompts:
  - name: ULTRON Tool Create
    description: "Create new ULTRON tool"
    prompt: |
      Create a new ULTRON tool in tools/ directory:
      - Inherit ToolInterface
      - Implement match(), execute(), schema()
      - Add error handling and logging
      - Include self_test() validation
      - Follow async-first patterns
      - Register in agent_core._load_tools()

  - name: ULTRON Refactor
    description: "Refactor for ULTRON patterns"
    prompt: |
      Refactor this code for ULTRON:
      - Use async/await for all I/O
      - Emit relevant events
      - Add ultron_logger logging
      - Use config.get() for settings
      - Handle errors gracefully
      - Optimize for performance
      - Maintain type hints

  - name: ULTRON Debug
    description: "Debug ULTRON issue"
    prompt: |
      Debug this ULTRON issue:
      1. Analyze error/behavior
      2. Identify root cause
      3. Provide fixed code
      4. Include test cases
      5. Reference related files
      6. Explain event flow
```

### Enable Watcher for Auto-Actions

```yaml
watcher:
  enabled: true
  include: ["tools/**/*.py", "brain.py", "memory.py"]
  exclude: ["**/*.backup", "**/__pycache__"]
  onChange: "ULTRON Refactor"  # Auto-run on file changes
```

---

## Integration with Other Tools

### Codex + Copilot CLI Sync

Both Codex and Copilot CLI read the same repo:
- ✅ Consistent patterns across tools
- ✅ Both use `.github/copilot-instructions.md`
- ✅ Both respect `.codex/config.yaml`
- ✅ MCP servers available to both

**Workflow**:
1. Codex for rapid edits & refactoring
2. Copilot CLI for architectural decisions
3. Both access same memory, events, tools

### Codex + Local Ollama

Codex can orchestrate local models via `.codex/config.yaml`:

```yaml
models:
  - title: Amazon Q
    orchestration:
      enabled: true
      ollama_url: http://localhost:11434
      local_models:
        primary: qwen2.5-coder:7b      # Coding
        reasoning: deepseek-r1:14b     # Analysis
```

**Benefit**: Fast, offline, free development without API costs

### Codex + VS Code Copilot

Use Codex **and** VS Code Copilot in parallel:
- Codex in editor for refactoring
- Copilot Chat (VS Code) for questions
- Both use same instructions & context

---

## Key Files & Locations

| Path | Purpose |
|------|---------|
| `.codex/config.yaml` | Codex configuration (models, prompts, watcher) |
| `.codex/instructions.md` | This file (Codex-specific guidance) |
| `.github/copilot-instructions.md` | Shared with Copilot & other tools |
| `ultron_config.json` | ULTRON agent configuration |
| `brain.py` | LLM interface (Ollama, system prompts) |
| `memory.py` | Memory system (short/long-term) |
| `tools/` | Tool implementations |
| `utils/event_system.py` | Event bus for all subsystems |
| `utils/ultron_logger.py` | Structured logging |
| `tests/` | Test suite |
| `logs/` | Runtime logs (errors.log, ai_activities.log) |

---

## Troubleshooting

### Codex Can't Connect to Ollama

```bash
# Check Ollama is running:
curl http://localhost:11434/api/tags

# If not, start Ollama:
ollama serve

# Verify config points to correct URL:
grep ollama_url .codex/config.yaml
# Should be: http://localhost:11434
```

### Model Not Responding

```bash
# Check model is pulled:
ollama list
ollama pull qwen2.5-coder:7b
ollama pull deepseek-r1:14b

# Check memory/resources:
ollama ps
# If models are slow, reduce maxTokens in .codex/config.yaml
```

### API Errors (Ultron Model)

```bash
# Verify API key:
grep apiKey .codex/config.yaml
# Update if needed: replace INSERT-YOUR-KEY with actual key

# Check network:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Event Emission Not Working

Check that:
1. `event_system` is imported: `from utils.event_system import event_system`
2. You're using `await`: `await event_system.emit(...)`
3. You're in async context: `async def function():`
4. Event name matches subscribers

---

## Best Practices for Codex

✅ **Do**:
- Use Codex for refactoring & code generation
- Leverage local models for fast feedback
- Customize prompts in `.codex/config.yaml`
- Review Codex output before committing
- Test generated code thoroughly
- Use async-first patterns
- Emit events for all significant actions
- Log decisions and errors

❌ **Don't**:
- Blindly accept Codex output (review it!)
- Use synchronous code for I/O operations
- Hardcode configuration values
- Log sensitive data (API keys, passwords)
- Skip error handling
- Commit untested code
- Modify `config.py` directly (edit `ultron_config.json`)
- Ignore event system patterns

---

## Related Documentation

- **Copilot Instructions**: `.github/copilot-instructions.md` (shared with all tools)
- **Architecture**: `docs/major_components_and_features.md`
- **Self-Awareness**: `.github/copilot-instructions.md` → "Self-Awareness & Memory System" section
- **Tool Framework**: `tools/tool_interface.py`
- **Event System**: `utils/event_system.py`
- **Memory**: `memory.py` + `enhanced_memory_system.py`
- **Configuration**: `config.py` (generated) + `ultron_config.json` (edit this)
- **Logging**: `utils/ultron_logger.py`
- **Consciousness/Ethics**: `CONSCIOUSNESS_ETHICS.md`

---

**Last Updated**: 2026-03-06  
**Codex Version**: Compatible with Codex (Amazon Q, OpenAI, local models)

For questions, search codebase for component names or check `DOCUMENTATION_HUB.md`.
