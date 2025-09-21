# UltronSysAgent 🤖

**Fully Autonomous AI Voice Assistant for Windows 11**

UltronSysAgent is a comprehensive, always-listening AI assistant designed specifically for Windows 11 systems with advanced capabilities including voice interaction, system automation, file processing, and extensible plugin architecture.

## 🌟 Features

### 🎙️ Voice Interface
- **Always-listening** voice activation (no wake word required)
- **Real-time STT** using Whisper or DeepSeek
- **Streaming TTS** with pyttsx3 or ElevenLabs integration
- **Voice Activity Detection** for natural conversation flow

### 🧠 AI Brain
- **Multi-model routing**: OpenAI GPT-4, DeepSeek, or local Phi-3 Mini
- **Intelligent fallback** system with automatic model switching
- **Contextual memory** with short-term and long-term storage
- **Streaming responses** for real-time interaction

### ⚙️ System Automation
- **Full admin access** for system-level operations
- **File operations**: Create, copy, move, delete with safety checks
- **Registry editing** and Windows service management
- **Process control** and network operations
- **Security auditing** with comprehensive command logging

### 🖥️ GUI Interface
- **Ultron-themed** dark interface with crimson accents
- **Real-time chat log** with voice and text input
- **File drop zone** for document processing
- **System monitoring** with CPU/RAM display
- **Admin mode toggle** with security controls

### 📁 File Processing
- **Document extraction**: PDF, DOCX, TXT, JSON, CSV
- **OCR capabilities** for image text extraction
- **File indexing** for quick search and retrieval
- **Drag-and-drop** file processing

### 👁️ Vision System
- **Camera integration** with OpenCV
- **Real-time image analysis** and face detection
- **Screenshot capture** and screen automation
- **OCR processing** for visual text extraction

### 🔧 Extensibility
- **Plugin system** for custom tool development
- **Event-driven architecture** with pub/sub messaging
- **Memory integration** for knowledge persistence
- **Custom command mapping** and automation workflows

### 🛡️ Security & Safety
- **Admin mode protection** for dangerous operations
- **Command confirmation** for destructive actions
- **Comprehensive logging** for security auditing
- **Offline mode** support for privacy protection

## 🚀 Quick Start

### Prerequisites
- **Windows 11** (MSI Thin 15 B13UC or compatible)
- **Python 3.10+** 
- **NVIDIA RTX 3050** (for GPU acceleration)
- **Admin privileges** (for full functionality)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-repo/UltronSysAgent.git
cd UltronSysAgent
```

2. **Run the setup script** (as Administrator):
```bash
python scripts/setup_windows.py
```

3. **Configure API keys** in `config/.env`:
```env
OPENAI_API_KEY=your_openai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

4. **Start UltronSysAgent**:
```bash
python main.py
```

### Manual Installation

If you prefer manual setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p logs data/{memory,cache,models} plugins

# Copy and edit configuration
cp config/config.json config/config.local.json
# Edit config.local.json with your preferences

# Run UltronSysAgent
python main.py
```

## 📖 Usage Guide

### Voice Commands

UltronSysAgent responds to natural language commands:

```
"Create a file called test.txt with hello world"
"Show me system information"
"Take a screenshot"
"Search for PDF files containing 'report'"
"Schedule a reminder for 2 PM today"
"What's my CPU usage?"
```

### GUI Controls

- **Mute Button**: Toggle voice listening on/off
- **Admin Mode**: Enable/disable administrative privileges
- **File Drop Zone**: Drag files for automatic processing
- **Chat Log**: View conversation history and system responses

### Configuration

Edit `config/config.json` to customize:

```json
{
  "voice": {
    "always_listening": true,
    "stt_provider": "whisper",
    "tts_provider": "pyttsx3"
  },
  "ai": {
    "primary_model": "gpt-4",
    "temperature": 0.7
  },
  "security": {
    "require_admin_confirmation": true,
    "log_all_commands": true
  }
}
```

## 🔌 Plugin Development

Create custom plugins by adding files to the `plugins/` directory:

```python
# plugins/my_plugin.py
class MyPlugin:
    def __init__(self, config, event_bus):
        self.config = config
        self.event_bus = event_bus
    
    async def handle_command(self, command):
        # Your plugin logic here
        return "Plugin response"
```

## 🏗️ Architecture

### Core Components

- **Application**: Main orchestrator and lifecycle management
- **EventBus**: Pub/sub messaging between modules
- **ConfigManager**: Centralized configuration handling
- **Logger**: Multi-level logging with security auditing

### Modules

- **VoiceEngine**: STT/TTS processing and audio I/O
- **AIBrain**: Model routing and conversation management
- **SystemAutomation**: Windows system control and automation
- **MemoryManager**: Short/long-term memory with vector search
- **FileManager**: Document processing and file operations
- **VisionSystem**: Camera and image processing
- **Scheduler**: Task scheduling and automation

### Data Flow

```
Voice Input → STT → AI Brain → Response Generation → TTS → Audio Output
     ↓                ↓              ↓
File Drop → Processing → Memory Storage → Context Retrieval
     ↓                ↓              ↓
System Commands → Validation → Execution → Logging
```

## 🛠️ Development

### Project Structure

```
UltronSysAgent/
├── main.py                 # Entry point
├── src/
│   ├── core/              # Core system components
│   ├── modules/           # Feature modules
│   └── gui/               # User interface
├── config/                # Configuration files
├── plugins/               # Plugin directory
├── scripts/               # Setup and utility scripts
├── data/                  # Runtime data storage
├── logs/                  # Application logs
└── assets/                # Static assets
```

### Running Tests

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Formatting

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/
```

## 🔧 Troubleshooting

### Common Issues

**Voice not working**:
- Check microphone permissions
- Verify `sounddevice` installation
- Test audio devices: `python -c "import sounddevice; print(sounddevice.query_devices())"`

**AI models not responding**:
- Verify API keys in `.env` file
- Check internet connection (unless in offline mode)
- Review logs in `logs/ultron_agent.log`

**Admin features not working**:
- Ensure running as Administrator
- Check `admin_mode` setting in configuration
- Review security logs in `logs/commands.log`

**GPU acceleration not working**:
- Install CUDA toolkit
- Verify PyTorch GPU support: `python -c "import torch; print(torch.cuda.is_available())"`

### Log Files

- **Main Log**: `logs/ultron_agent.log`
- **Error Log**: `logs/errors.log`
- **Command Log**: `logs/commands.log`
- **Voice Activity**: `logs/voice_activity.log`

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-repo/UltronSysAgent.git
cd UltronSysAgent

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and Whisper
- **Microsoft** for Windows integration APIs
- **OpenCV** community for computer vision tools
- **Python** ecosystem for foundational libraries

## ⚡ Performance Notes

### Recommended System Requirements

- **CPU**: Intel i5-12500H or equivalent
- **RAM**: 16GB+ (32GB recommended for local models)
- **GPU**: NVIDIA RTX 3050+ with 4GB+ VRAM
- **Storage**: 10GB+ free space for models and data

### Optimization Tips

- Use **GPU acceleration** for local model inference
- Enable **memory caching** for frequently accessed data
- Configure **voice activity detection** threshold for your environment
- Use **offline mode** when privacy is critical

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/UltronSysAgent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/UltronSysAgent/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/UltronSysAgent/wiki)

---

**UltronSysAgent** - Your intelligent, autonomous AI assistant for Windows 11 🤖✨
