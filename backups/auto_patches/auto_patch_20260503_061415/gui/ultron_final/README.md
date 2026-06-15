# 🔴 ULTRON AI Assistant - Complete Package

## Overview
ULTRON is a comprehensive AI assistant system with voice recognition, computer vision, system automation, and intelligent file management. This package provides a fully functional local AI system with multiple interfaces.

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or download the ULTRON package
cd ultron_final

# Run setup (installs dependencies and creates directories)
python setup.py

# Or install dependencies manually
pip install -r requirements.txt
```

### 2. Configuration
Edit `config.json` to customize settings:
- Add your OpenAI API key for advanced AI features
- Configure voice, vision, and system settings
- Set web interface port and other preferences

### 3. Launch ULTRON
```bash
# Easy launcher with menu
python start_ultron.py

# Or launch directly:
python main.py --mode gui      # GUI interface
python main.py --mode console  # Console interface
python main.py --mode async    # Background with web interface
```

### 4. Test System
```bash
python test_ultron.py
```

## 🎯 Features

### 🎤 Voice Recognition
- **Multiple engines**: Google Speech API, offline Sphinx
- **Wake word detection**: "ultron", "hello", "computer"
- **Noise reduction**: Advanced audio processing
- **Text-to-speech**: Natural voice responses

### 🤖 AI Brain
- **OpenAI GPT integration**: Advanced conversational AI
- **Local fallback**: Works without internet
- **Context awareness**: Remembers conversation history
- **Command processing**: Natural language commands

### 👁️ Vision System
- **Screenshot capture**: Automated screen capture
- **OCR text extraction**: Tesseract-based text recognition
- **Image enhancement**: Preprocessing for better accuracy
- **Real-time analysis**: Live screen monitoring

### ⚙️ System Control
- **Process management**: List, monitor, control processes
- **Power management**: Shutdown, restart, sleep
- **System monitoring**: CPU, memory, disk usage
- **Application launcher**: Safe application launching

### 📁 File Management
- **AI-powered sorting**: Intelligent file categorization
- **Duplicate detection**: SHA-256 hash comparison
- **Backup system**: Automatic backup before sorting
- **Real-time monitoring**: Watch folders for changes

### 🌐 Web Interface
- **Modern UI**: Responsive web interface
- **REST API**: Complete API for integration
- **Real-time updates**: Live system monitoring
- **Remote control**: Web-based command execution

### 🖥️ GUI Interface
- **Native desktop app**: Tkinter-based interface
- **Real-time monitoring**: System metrics and logs
- **Voice controls**: Integrated voice commands
- **Visual feedback**: Status indicators and alerts

## 🎮 Usage Examples

### Voice Commands
- "Take a screenshot"
- "What's my system status?"
- "Sort files in downloads"
- "Open calculator"
- "What time is it?"
- "Shutdown computer"

### Text Commands
- `screenshot` - Capture and analyze screen
- `system info` - Display system metrics
- `sort files` - Organize files by type
- `open notepad` - Launch applications
- `time` - Get current time

### Web API
```bash
# Get system status
GET http://localhost:3000/api/status

# Execute command
POST http://localhost:3000/api/command
{"command": "take screenshot"}

# Sort files
POST http://localhost:3000/api/files/sort
{"source_dir": "/path/to/directory"}
```

## 📂 Project Structure

```
ultron_final/
├── main.py                 # Main entry point
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script
├── start_ultron.py       # Quick launcher
├── test_ultron.py        # Test suite
├── README.md             # This file
│
├── core/                 # Core modules
│   ├── __init__.py
│   ├── voice_engine.py   # Voice recognition/synthesis
│   ├── vision_system.py  # Computer vision/OCR
│   ├── ai_brain.py       # AI conversation engine
│   ├── system_control.py # System automation
│   ├── file_manager.py   # File sorting/management
│   └── web_interface.py  # Web server/API
│
├── gui/                  # GUI interface
│   ├── __init__.py
│   └── ultron_gui.py     # Desktop GUI
│
├── web/                  # Web interface
│   └── index.html        # Web UI
│
├── logs/                 # Log files (created on first run)
├── screenshots/          # Screenshots (created on first run)
└── managed_files/        # Sorted files (created on first run)
    ├── documents/
    ├── images/
    ├── videos/
    ├── audio/
    ├── archives/
    ├── code/
    ├── executables/
    ├── other/
    └── backup/
```

## 🔧 Configuration

### config.json Options
```json
{
  "voice": {
    "enabled": true,
    "wake_words": ["ultron", "hello", "computer"],
    "tts_rate": 150,
    "recognition_timeout": 5
  },
  "ai": {
    "openai_api_key": "your-api-key-here",
    "model": "gpt-4",
    "use_local": false
  },
  "system": {
    "admin_required": true,
    "safe_commands_only": true,
    "log_activities": true
  },
  "web": {
    "enabled": true,
    "port": 3000,
    "host": "localhost"
  },
  "vision": {
    "enabled": true,
    "auto_enhance": true,
    "ocr_language": "eng"
  },
  "files": {
    "auto_sort": true,
    "watch_downloads": true,
    "backup_before_sort": true
  }
}
```

## 📋 Requirements

### Python Dependencies
- Python 3.8+
- speech_recognition
- pyttsx3
- opencv-python
- pytesseract
- Pillow
- numpy
- psutil
- pyautogui
- Flask
- openai (optional)

### System Dependencies
- **Tesseract OCR** (for vision system)
  - Windows: Download from GitHub
  - Linux: `sudo apt-get install tesseract-ocr`
  - macOS: `brew install tesseract`

### Hardware Requirements
- Microphone (for voice recognition)
- Webcam/Screen (for vision system)
- Admin privileges (for system control)

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_ultron.py
```

Tests include:
- Module imports
- Dependency availability
- Core functionality
- Component integration
- Error handling

## 🛠️ Development

### Adding New Features
1. Create new module in `core/`
2. Add to main.py imports
3. Update configuration schema
4. Add tests to test_ultron.py
5. Update documentation

### API Extension
Add new endpoints in `core/web_interface.py`:
```python
@self.app.route('/api/custom')
def custom_endpoint():
    return jsonify({"result": "custom response"})
```

### Voice Commands
Add new commands in `main.py` process_command method:
```python
elif "custom command" in command_lower:
    response = "Custom response"
```

## 🔒 Security

- Safe command whitelist
- Admin privilege checks
- File permission validation
- Input sanitization
- Secure API endpoints

## 📊 Performance

- Async/await for I/O operations
- Background processing threads
- Efficient file operations
- Memory usage optimization
- Response time monitoring

## 🐛 Troubleshooting

### Common Issues

**Voice recognition not working:**
- Check microphone permissions
- Verify audio drivers
- Test with different recognition engines

**OCR failing:**
- Install Tesseract OCR
- Check image quality
- Verify language packs

**Web interface not accessible:**
- Check firewall settings
- Verify port availability
- Check console for errors

**High resource usage:**
- Disable unused features
- Reduce processing frequency
- Check for background tasks

### Debug Mode
```bash
python main.py --debug --mode console
```

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

1. Test your changes with the test suite
2. Update documentation
3. Follow existing code style
4. Add appropriate error handling

## 🔗 Links

- OpenAI API: https://openai.com/api/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- Speech Recognition: https://pypi.org/project/SpeechRecognition/

---

**🔴 ULTRON - Where Voice Meets Intelligence 🔴**
