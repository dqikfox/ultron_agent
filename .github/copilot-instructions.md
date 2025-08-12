# Copilot Instructions for ULTRON Agent 3.0

## Project Architecture & Key Components
- **agent_core.py**: Main integration hub. Initializes config, memory, voice, vision, event system, performance monitor, task scheduler, and the modular brain. Handles command routing, tool loading, and system events.
- **brain.py**: Core AI logic. Handles planning, acting, and project analysis. Integrates with tools and memory.
- **voice_manager.py / voice.py**: Multi-engine voice system with fallback logic and thread safety.
- **gui_ultimate.py**: ⚠️ DEPRECATED - Migrating to superior Pokédex-based implementations in `new pokedex/` directory
- **pokedex_ultron_gui.py**: Current working GUI with proper accessibility features and text input fields
- **new pokedex/**: Contains advanced GUI variants optimized for accessibility and disabled user support
- **ollama_manager.py**: Handles AI model management, switching, and status monitoring.
- **config.py**: Loads and manages configuration from `ultron_config.json`.
- **tools/**: All tool plugins. Tools must implement `match` and `execute` methods and be discoverable by `agent_core.py`'s dynamic loader.
- **utils/**: Event system, performance monitor, task scheduler, and startup helpers.

## Developer Workflows
- **Run the agent**: `python main.py` or use `run.bat` for full diagnostics and startup checks.
- **Run tests**: `pytest` (all tests in `tests/`).
- **Debug**: Use log files (`startup.log`, `error.log`, `ultron_gui.log`, `ultron.log`) for diagnostics. GUI migration in progress - check GUI_TRANSITION_NOTES.md. CLI and Pokédex GUI both supported.
- **Configuration**: Edit `ultron_config.json` for API keys, model, and feature toggles. Environment variables can override sensitive values.
- **Model management**: Use Ollama (`ollama run <model>`) for model downloads and switching.

## Project-Specific Patterns & Conventions
- **Tool Loading**: Tools are dynamically discovered from the `tools/` package. Each tool must be a class with `match` and `execute` methods, and a static `schema()` method for metadata.
- **Event System**: Use `EventSystem` for cross-component communication. Subscribe to events like `command_start`, `command_complete`, and `error`.
- **Async/Sync Handling**: Most core logic is async, but sync wrappers are provided for GUI and CLI compatibility.
- **Voice**: Voice system uses a fallback chain: Enhanced → pyttsx3 → OpenAI → Console.
- **GUI**: The GUI runs in a background thread and interacts with the agent via method calls and event system.
- **Testing**: Tests use heavy mocking for config, brain, and tools. See `tests/test_agent_core.py` for patterns.
- **Startup**: `run.bat` performs system checks, diagnostics, and launches the agent.

## Integration Points & External Dependencies
- **Ollama**: Required for model management. Must be running (`ollama serve`).
- **OpenAI**: API key required for some features. Set in `ultron_config.json` or as an environment variable.
- **Python 3.10+**: Required for all features.
- **ShellCheck**: Used for shell script linting (Windows support via bundled binary).

## Examples
- **Add a new tool**: Place a class in `tools/` with `match`, `execute`, and `schema()` methods. It will be auto-discovered.
- **Subscribe to an event**: `self.event_system.subscribe("command_complete", handler_fn)`
- **Run a test**: `pytest tests/test_agent_core.py`

## Key Files
- `agent_core.py`, `brain.py`, `voice_manager.py`, `gui_ultimate.py`, `ollama_manager.py`, `config.py`, `tools/`, `utils/`, `ultron_config.json`, `run.bat`, `tests/`
https://pyautogui.readthedocs.io/en/latest/quickstart.html
https://pyautogui.readthedocs.io/en/latest/mouse.html
https://pyautogui.readthedocs.io/en/latest/keyboard.html
https://pyautogui.readthedocs.io/en/latest/screenshot.html
https://pyautogui.readthedocs.io/en/latest/tests.html

---

If any section is unclear or missing, please provide feedback for further refinement.
