# Ultron Agent 2.0 File Descriptions

## Files

### agent_core.py
Main entry point, orchestrates subsystems (memory, voice, vision, tools). Supports voice, console, and GUI modes.

### api_server.py
Flask API server with `/status`, `/command`, and `/settings` endpoints, secured with JWT.

### brain.py
Handles reasoning with Ollama (`llama3.2:latest`) and OpenAI, includes response caching and model switching.

### config.py
Loads configuration from `ultron_config.json` and decrypts `keys.txt` using `VAULT_ENC_KEY`.

### gui.py
Enhanced Tkinter GUI with command input, response display, and settings panel.

### keys.txt
Encrypted API keys (OpenAI, Ollama, ElevenLabs, Supabase, Gemini), decrypted at runtime.

### main.py
Placeholder initialization script.

### memory.py
Manages short-term (list) and long-term (FAISS) memory.

### package.json
Node.js dependencies for `ultron.js`, including ElevenLabs.

### README.md
Setup and usage instructions.

### requirements.txt
Python dependencies.

### run.bat
Windows script to set up and run the agent.

### run.sh
Linux/Mac script to set up and run the agent.

### setup.py
Installs dependencies and configures environment.

### ultron.js
Node.js agent with Ollama and ElevenLabs integration, includes a web UI.

### ultron_config.json
Configuration with voice, GUI, and API enabled by default.

### ultron-project-461408-ea3a9b103b69.json
Google Cloud service account key.

### vision.py
Screen capture and OCR using `pytesseract` and `PIL`.

### voice.py
Voice input/output with ElevenLabs, Whisper, and pyttsx3 fallback.

### Tools Package
- **base.py**: Base `Tool` class.
- **code_execution_tool.py**: Executes Python code in a sandbox.
- **database_tool.py**: Queries/updates Supabase database.
- **file_tool.py**: File operations (list, read, write).
- **image_generation_tool.py**: Generates images with Gemini API.
- **screen_reader_tool.py**: Screen OCR.
- **system_tool.py**: System control (open apps, shutdown).
- **web_search_tool.py**: Web searches via DuckDuckGo.
