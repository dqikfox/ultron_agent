# Ultron Assistant

A sophisticated AI assistant with voice interaction, automation capabilities, and a sleek dark-themed web interface. Built with FastAPI, Socket.IO, and integrated with Ollama for local AI processing.

## Features

### 🤖 AI Chat Interface
- **Real-time conversation** with Ollama-powered AI models
- **Streaming responses** for immediate feedback
- **Dark theme** with Ultron-inspired design
- **Message history** and conversation management

### 🎤 Voice Interaction
- **Speech-to-text** using Google's speech recognition
- **Text-to-speech** with configurable voice options
- **Push-to-talk** and continuous listening modes
- **Voice commands** for hands-free operation

### 🔧 System Automation
- **Application launching** (Notepad, Calculator, Chrome, etc.)
- **Text input simulation** and keyboard shortcuts
- **Screenshot capture** with automatic saving
- **Volume control** and system management
- **Web search** integration
- **Window management** (minimize, maximize, close)

### 🖥️ Multiple Interfaces
- **Web interface** accessible from any browser
- **Desktop app** using PySide6/Qt WebEngine
- **Mobile-responsive** design for tablets and phones
- **PWA support** for app-like experience

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running ([Download here](https://ollama.ai/download))
3. **Microphone** (optional, for voice features)

### Installation

1. **Clone or extract** the Ultron Assistant to your project:
```bash
cd c:\Projects\ultron_agent_2\ultron_assistant
```

2. **Install dependencies** (auto-install available):
```bash
python run_ultron_assistant.py --install-deps
```

3. **Ensure Ollama is running** with a model:
```bash
ollama serve
ollama pull llama3.2  # Download default model
```

4. **Launch Ultron Assistant**:
```bash
python run_ultron_assistant.py
```

The system will automatically:
- ✅ Check all dependencies
- ✅ Verify Ollama connectivity  
- ✅ Start the FastAPI server
- ✅ Open the desktop GUI or web browser

## Usage

### Web Interface
- Access at `http://127.0.0.1:8000` in any browser
- Type messages in the input field
- Click the microphone button for voice input
- Use quick action buttons for common tasks

### Voice Commands
- **"Take screenshot"** - Captures and saves a screenshot
- **"Open calculator"** - Launches the calculator app
- **"Search for [query]"** - Opens Google search
- **"Type hello world"** - Types the specified text
- **"Volume up/down"** - Adjusts system volume
- **"What time"** - Gets current time
- **"System info"** - Shows system information

### Keyboard Shortcuts
- **Ctrl+Enter** - Send message
- **Ctrl+K** - Clear chat
- **Ctrl+M** - Voice input
- **Esc** - Stop voice input

## Configuration

### Command Line Options
```bash
# Basic usage
python run_ultron_assistant.py

# Custom host/port
python run_ultron_assistant.py --host 0.0.0.0 --port 8080

# Server only (no GUI)
python run_ultron_assistant.py --no-gui

# Check system only
python run_ultron_assistant.py --check-only

# Install missing dependencies
python run_ultron_assistant.py --install-deps
```

### Ollama Models
The system defaults to `llama3.2` but supports any Ollama model:
```bash
ollama pull llama3.1        # Alternative model
ollama pull codellama       # Code-focused model
ollama pull mistral         # Lightweight option
```

Edit `ollama_client.py` to change the default model.

## Integration with Main Ultron Agent

The assistant can integrate with your existing Ultron Agent project:

1. **Auto-detection** - If placed in the ultron_agent_2 project, it will automatically use existing components
2. **Shared configuration** - Uses the main project's config.py if available  
3. **Brain integration** - Routes complex queries through the main UltronBrain
4. **Fallback system** - Works standalone if main project is unavailable

## Architecture

```
ultron_assistant/
├── app.py                 # FastAPI server + Socket.IO
├── ollama_client.py       # Ollama API integration
├── automation.py          # System automation commands  
├── voice.py              # Speech recognition & synthesis
├── run_ultron_assistant.py # Launcher script
├── static/
│   ├── css/ultron.css    # Dark theme styling
│   └── js/chat.js        # Client-side chat logic
└── templates/
    └── index.html        # Main web interface
```

### Key Components

- **FastAPI Backend** - Async HTTP server with WebSocket support
- **Socket.IO** - Real-time bidirectional communication
- **Ollama Client** - Streaming AI model integration
- **Voice System** - Cross-platform speech I/O
- **Automation Engine** - Natural language → system actions
- **PySide6 GUI** - Native desktop application wrapper

## Troubleshooting

### Common Issues

**"Ollama not found"**
- Install Ollama from https://ollama.ai/download
- Ensure `ollama serve` is running
- Check if `ollama` command is in PATH

**"No microphone detected"**
- Check microphone permissions
- Install pyaudio: `pip install pyaudio`
- On Windows, may need pre-built wheel

**"Import errors"**
- Run: `python run_ultron_assistant.py --install-deps`
- Ensure Python 3.8+ is being used
- Check virtual environment activation

**"PySide6 GUI won't start"**
- Falls back to web browser automatically
- Install PySide6: `pip install PySide6`
- Try `--no-gui` flag for server-only mode

### Debug Mode
Add logging for troubleshooting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- **Local processing** - AI runs locally via Ollama
- **No data transmission** - Conversations stay on your machine
- **Automation limits** - Basic commands only, easily extensible
- **Network binding** - Defaults to localhost only

## Development

### Extending Automation
Add new commands in `automation.py`:
```python
def run_command(command: str) -> str:
    cmd = command.lower().strip()
    
    if cmd.startswith("my new command"):
        # Your automation logic here
        return "Command executed successfully"
```

### Customizing UI
- Edit `static/css/ultron.css` for styling
- Modify `templates/index.html` for layout
- Update `static/js/chat.js` for client behavior

### Adding AI Models
Edit the model in `ollama_client.py`:
```python
async def ollama_chat(messages, model="your-model-name"):
    # Model will be used for all conversations
```

## Performance

- **Memory usage** - ~100-200MB (excluding AI model)
- **CPU usage** - Minimal when idle, depends on AI model
- **Network** - WebSocket for real-time, HTTP for voice
- **Storage** - Screenshots saved to ~/Pictures/UltronScreenshots

## License

Part of the ULTRON Agent 2.0 project. See main project license.

## Support

For issues related to:
- **Ollama** - Visit https://ollama.ai/docs
- **Speech recognition** - Check microphone setup
- **FastAPI** - See https://fastapi.tiangolo.com/
- **General bugs** - Check the main project repository

---

**Built with ❤️ and Python for the ULTRON Agent ecosystem**
