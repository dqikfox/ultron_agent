# Ultron Agent 2.0

An advanced AI assistant with voice, vision, memory, and tool capabilities, powered by Ollama, OpenAI, ElevenLabs, Supabase, and Google Gemini APIs.

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

3. **Encrypt Keys**:
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
   - Access the API at `http://localhost:5000` with JWT authentication.

## Features
- Voice interaction with ElevenLabs TTS and Whisper STT.
- Enhanced GUI with command input and settings panel.
- Tools for file operations, web search, database queries, image generation, and code execution.
- Ollama integration with model switching and response caching.
- Supabase database integration.
- Google Gemini for image generation.
- Secure API with JWT authentication.
- Cross-platform support.

## Troubleshooting
- Check `logs/ultron.log` for errors.
- Ensure Ollama is running and API keys are correctly encrypted.
- Update `ultron_config.json` for custom settings (e.g., model, voice).
