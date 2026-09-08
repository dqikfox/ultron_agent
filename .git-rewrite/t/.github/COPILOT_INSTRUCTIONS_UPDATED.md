# Copilot Instructions — ULTRON Agent (cleaned)

This file is a concise, developer-focused reference describing where key components live and how they interact. It's intentionally short — for full details see the files referenced below.

## Quick overview

- agent_core.py — main integration hub (load config, memory, voice, event system, brain, tools).
- brain.py — perception → plan → act loop. Use `brain.perceive()`, `brain.plan()`, `brain.act()`.
- voice_manager.py / voice.py — TTS/STT with fallbacks; tests mock these engines.
- pokedex_ultron_gui.py — current production GUI (hooks into EventSystem; preferred over deprecated `gui_ultimate.py`).
- utils/event.py — `EventSystem` implementation (subscribe/publish callbacks used across components).
- ollama_manager.py — local model management (Ollama). Use OpenAI only for cloud models.

## GUI & EventSystem

- Use `pokedex_ultron_gui.py` for production UIs. It subscribes to agent events and calls agent APIs where needed.
- `EventSystem` lives in `utils/event.py`. It provides a small pub/sub API used by GUI, tools, and core systems. Typical usage:

  ```py
  # subscribe
  event_system.subscribe('command_complete', handler_fn)

  # publish
  event_system.publish('command_start', payload)
  ```

## Models: Ollama vs OpenAI

- Ollama: prefer for local/inferred models (e.g. `llama3`, `mistral`) — run locally with `ollama serve` or `ollama run <model>`.
- OpenAI: use for cloud-hosted models (GPT-4 family). Requires `OPENAI_API_KEY`.

Choose Ollama for offline/local workloads, OpenAI for cloud-scale/managed models.

## Voice testing

- Unit tests should mock TTS and STT. See `tests/test_voice_manager.py` for examples that patch engines and assert behavior without real audio devices.

## Brain & tools

- `brain.py` implements the main control loop: perception → planning → execution. Tools are injected at runtime and matched by `brain.plan()` via each tool's `schema()` metadata.

Recommended tool class pattern:

```py
class ToolName:
    def match(self, query) -> bool:
        ...
    def execute(self, query) -> Any:
        ...
    @staticmethod
    def schema() -> dict:
        return {"name": "ToolName", "description": "..."}
```

## Config precedence

- Runtime environment variables (for example `OPENAI_API_KEY`) override values in `ultron_config.json`.

## Tests & debugging

- Run tests with `pytest`.
- Use `python -m py_compile <file>` to validate syntax for changed modules.
- Logs: `startup.log`, `error.log`, `ultron_gui.log`, `ultron.log`.

## Quick notes

- `gui_ultimate.py` is deprecated — avoid new work against it.
- If you want me to merge these clarifications into the canonical `.github/copilot-instructions.md`, I can do a careful merge (non-destructive).
