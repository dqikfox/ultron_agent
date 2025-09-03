# ULTRON Agent API Reference

Auto-generated API documentation from source code analysis.

## Table of Contents

- [voice_manager.py](#voice-manager)
- [memory.py](#memory)
- [main.py](#main)

---

## voice_manager.py


Enhanced Voice System Integration for ULTRON Agent 3.0
Fixes all threading and API issues with proper fallback mechanisms


### Class: `UltronVoiceManager`

Unified voice manager that handles all voice operations for ULTRON

#### `__init__(self, config)`


#### `_initialize_engines(self)`

Initialize all available voice engines


#### `speak(self, text, async_mode)`

Main speak function with comprehensive fallback


#### `_speak_async(self, text)`

Async voice output


#### `_speak_sync(self, text)`

Synchronous voice output with fallback chain


#### `_try_engine(self, engine_name, text)`

Try specific engine


#### `_speak_openai(self, text)`

OpenAI TTS implementation


#### `_start_voice_worker(self)`

Start voice worker thread


#### `_voice_worker(self)`

Voice worker thread


#### `test_voice(self)`

Test voice system


#### `shutdown(self)`

Shutdown voice system


### Function: `get_voice_manager(config)`

Get global voice manager

### Function: `speak(text, async_mode)`

Global speak function

### Function: `test_voice_system(config)`

Test voice system

## memory.py

### Class: `Memory`

#### `__init__(self, short_term_limit, long_term_file)`


#### `load_long_term_memory(self, file_path)`


#### `save_long_term_memory(self, file_path)`


#### `add_to_short_term(self, item)`


#### `add_to_long_term(self, item)`


#### `retrieve_short_term(self)`


#### `retrieve_long_term(self)`


#### `clear_short_term(self)`


#### `clear_long_term(self)`


#### `get_recent_memory(self, limit)`

Get recent memory items for agent network queries


#### `search_memory(self, query)`

Search memory for relevant items


## main.py


Ultron Agent 3.0 - Main entry point


### Function: `setup_signal_handlers()`

Setup graceful shutdown on signals.

### Function: `main()`

Main entry point.
