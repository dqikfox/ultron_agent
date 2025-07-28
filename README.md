# Ultron Agent 2.0

Ultron Agent 2.0 is a modular, autonomous AI assistant with voice, vision, GUI, and deep system integration. It features a plugin-based tool system, a modular LLM "brain" (see `brain.py`), and a robust architecture for extensibility and security.

## Setup Instructions

1. **Extract the Package**:
   - Extract `ultron_agent_2.zip` to a directory (e.g., `C:\ultron_agent_2` or `~/ultron_agent_2`).

2. **Install Dependencies**:
   - Install Python 3.8+ (https://www.python.org/downloads/).
   - Install Node.js (https://nodejs.org) for the `ultron.js` component.
   - Install Ollama (https://ollama.ai) and run:
     ```bash
     ollama run llama3.2:latest
     ```
   - Run the setup script:
     ```bash
     python3 setup.py
     ```

3. **Encrypt Keys** (optional):
   - Run the provided `encrypt_keys.py` script to encrypt your `keys.txt` using `VAULT_ENC_KEY`:
     ```bash
     python3 encrypt_keys.py
     ```

4. **Run the Agent**:
   - On Windows: Double-click `run.bat`.
   - On Linux/Mac: Run `chmod +x run.sh && ./run.sh`.
   - For Node.js component:
     ```bash
     node ultron.js
     ```

5. **Usage**:
   - Use voice commands (e.g., "search for AI news", "generate image of a futuristic city").
   - Use the GUI to input commands and adjust settings.
   - Access the API at `http://localhost:5000` (if enabled).

## Features

- Voice recognition (multi-engine, wake word)
- Text-to-speech (pyttsx3)
- LLM integration (OpenAI, Ollama, local models)
- Vision/OCR (Tesseract)
- Pokedex-style GUI
- System monitoring
- File system AI sorting
- System automation
- Robust error handling
- Security (MAC whitelist, safe mode)
- Extensible plugin-based tools (see `tools/`)
- Modular brain module (see `brain.py`)
- Vector-based long-term memory (optional)

## Documentation

See the `docs/` folder for:
- `ultron_agent_2_architecture.md`: Advanced architecture and design plan
- Setup instructions, design notes, and module documentation

For details on the modular brain and plugin system, see `brain.py` and the `tools/` package.

## Troubleshooting
- Check `logs/ultron.log` for errors.
- Ensure Ollama is running and API keys are correctly set.
- Update `ultron_config.json` for custom settings (e.g., model, voice).
