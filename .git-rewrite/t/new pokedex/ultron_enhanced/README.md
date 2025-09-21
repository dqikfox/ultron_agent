# ULTRON AI - Advanced Voice-Controlled Assistant

A comprehensive AI system with voice recognition, GPT integration, OCR capabilities, intelligent file sorting, and an authentic Pokedex-style interface.

## 🔴 Features

### 🎤 **Advanced Voice Recognition**
- **Optimized Speech Recognition** with noise reduction and Voice Activity Detection (VAD)
- **Wake Word Detection** ("ultron", "hello", "speak", etc.)
- **Multiple Recognition Engines** (Google, Vosk offline, Sphinx fallback)
- **Adaptive Microphone Sensitivity** with ambient noise calibration
- **Real-time Audio Processing** with WebRTC VAD and noise suppression

### 🤖 **AI Integration**
- **OpenAI GPT-4** integration with conversation context management
- **Local LLM Fallback** for offline operation (DialoGPT, LLaMA support)
- **Intelligent Response Caching** for faster repeated queries
- **Context-Aware Conversations** with memory management
- **Automatic Fallback Chain** (Cloud → Local → Error handling)

### 👁️ **Computer Vision & OCR**
- **Advanced OCR** with Tesseract optimization and preprocessing
- **Screen Analysis** with AI-powered image understanding
- **Text Recognition** with confidence scoring and error correction
- **Image Enhancement** (denoising, deskewing, contrast adjustment)
- **Real-time Screen Monitoring** with change detection

### 📁 **Intelligent File Sorting**
- **AI-Powered Classification** using machine learning
- **Content Analysis** for ambiguous file types
- **Malware Detection** with heuristic scanning
- **Duplicate Detection** using SHA-256 hashing
- **Automatic Organization** into categorized folders
- **Real-time Directory Monitoring**

### ⚙️ **System Automation**
- **Process Management** (list, kill, start, monitor)
- **Power Control** (shutdown, restart, sleep, hibernate)
- **Performance Monitoring** with real-time metrics
- **Security Features** with MAC address filtering
- **Activity Logging** for audit trails
- **Desktop Automation** with custom scripts

### 🌐 **Web Interface**
- **Authentic Pokedex Design** with LED animations and sound effects
- **Real-time System Monitoring** with live metrics
- **Interactive Controls** (D-pad navigation, A/B buttons)
- **WebSocket Support** for real-time updates
- **Comprehensive API** for all system functions
- **Mobile-Responsive Design**

### 🔒 **Security & Privacy**
- **Encrypted Configuration Storage** using OS key vaults
- **MAC Address Trust Lists** for device authentication
- **Admin Privilege Management** with secure escalation
- **Audit Logging** for all system activities
- **Offline Mode Support** for privacy-conscious users

### 📊 **Performance & Diagnostics**
- **Real-time Performance Metrics** (CPU, memory, disk, network)
- **Voice Recognition Timing** and accuracy statistics
- **OCR Processing Speed** and confidence tracking
- **AI Response Time Monitoring**
- **System Health Diagnostics**

## 🚀 Installation

### Prerequisites
- **Python 3.8+** (3.10+ recommended)
- **Windows 10/11** (Linux support available)
- **4GB+ RAM** (8GB+ recommended for local LLMs)
- **Admin privileges** (for system automation features)

### Quick Install
```bash
# Clone or download the ULTRON system
git clone <repository-url>
cd ultron_enhanced

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Tesseract OCR for enhanced text recognition
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr

# Setup ULTRON directories and configuration
python launch_ultron.py --setup-only
```

### Configuration
1. **Edit `D:/ULTRON/config.json`** with your settings:
```json
{
  "openai_api_key": "your-openai-api-key-here",
  "voice_gender": "male",
  "theme": "red",
  "offline_mode": false,
  "vision_enabled": true,
  "web_port": 3000,
  "auto_sort_enabled": true,
  "security_enabled": true,
  "performance_monitoring": true
}
```

2. **Optional: Configure trusted devices** by adding MAC addresses to the config.

## 🎮 Usage

### Starting ULTRON

#### Full System (Voice + Web + AI)
```bash
python launch_ultron.py
```

#### Web Interface Only
```bash
python launch_ultron.py --web-only
```

#### Debug Mode
```bash
python launch_ultron.py --debug
```

### Voice Commands
Once started, ULTRON listens for wake words:
- "**Ultron**" - Activate voice assistant
- "**Hello**" - General greeting and activation
- "**Speak**" - Request voice response

#### Example Voice Commands:
- "What time is it?"
- "Take a screenshot"
- "Analyze the screen"
- "Sort my files"
- "What's my CPU usage?"
- "Shutdown the computer"
- "Open calculator"

### Web Interface
Access the Pokedex-style interface at: `http://localhost:3000`

#### Interface Sections:
- **🖥️ CONSOLE** - Command interface and conversation
- **⚙️ SYSTEM** - Real-time system monitoring
- **👁️ VISION** - Screen capture and analysis
- **📋 TASKS** - Task management
- **📁 FILES** - File system browser and sorting
- **🔧 CONFIG** - System configuration

#### Controls:
- **D-Pad** - Navigate between sections
- **A Button** - Select/Execute
- **B Button** - Back/Cancel
- **System Buttons** - Power, volume, settings

### API Endpoints

The web server provides comprehensive REST API:

#### System Status
```bash
GET /api/status
GET /api/system
GET /api/system/metrics
GET /api/diagnostics
```

#### Voice Control
```bash
POST /api/command
{"command": "your voice command here"}

GET /api/voice/status
POST /api/voice/test
POST /api/voice/sensitivity {"adjustment": 0.5}
```

#### Vision System
```bash
POST /api/vision/capture
POST /api/vision/analyze
POST /api/vision/ocr {"x": 100, "y": 100, "width": 200, "height": 50}
```

#### File Management
```bash
POST /api/files/sort {"directory": "/path/to/sort"}
GET /api/files/stats
POST /api/files/monitoring {"action": "start"}
```

#### Process Management
```bash
POST /api/system/processes {"action": "list", "target": ""}
POST /api/system/processes {"action": "kill", "target": "notepad.exe"}
```

#### Power Management
```bash
POST /api/power/shutdown
POST /api/power/restart
POST /api/power/sleep
```

## 🧪 Testing & Demo

### Run Comprehensive Demo
```bash
python demo_ultron.py
```

This will test all system components:
- Voice recognition and synthesis
- AI conversation capabilities
- Vision and OCR systems
- File sorting AI
- System automation
- Performance monitoring
- Security features
- Web interface

### Individual Component Testing
```python
# Test voice recognition
from core.voice_processor import VoiceProcessor
voice = VoiceProcessor(config)
voice.test_voice_recognition()

# Test vision system
from core.vision_system import VisionSystem
vision = VisionSystem(config)
await vision.analyze_screen()

# Test file sorting
from core.file_sorter import FileSorter
sorter = FileSorter(config)
await sorter.sort_directory()
```

## 🔧 Advanced Configuration

### Voice Recognition Optimization
```python
# Adjust recognition sensitivity
recognizer.energy_threshold = 4000
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.5
```

### OCR Enhancement
```python
# Configure Tesseract for better accuracy
config = "--oem 3 --psm 6"  # LSTM engine, uniform text block
config = "--oem 3 --psm 7"  # Single text line
```

### Local LLM Setup
1. Download model weights to `D:/ULTRON/models/`
2. Configure model in `ultron_main.py`:
```python
model_name = "microsoft/DialoGPT-small"  # Lightweight
# or
model_name = "huggingface/CodeBERTa-small-v1"  # Code-focused
```

### File Sorting Customization
```python
# Add custom file extensions
extension_rules['.xyz'] = ('Documents', 'Custom')

# Add custom content classification
def custom_classifier(content):
    if 'special_keyword' in content:
        return 'Custom', 'Special'
    return None
```

## 🛠️ Development

### Project Structure
```
ultron_enhanced/
├── ultron_main.py          # Main system core
├── launch_ultron.py        # System launcher
├── demo_ultron.py          # Feature demonstration
├── requirements.txt        # Python dependencies
├── config.json            # System configuration
├── core/                   # Core modules
│   ├── voice_processor.py  # Voice recognition/synthesis
│   ├── vision_system.py    # Computer vision/OCR
│   ├── system_automation.py # System control
│   ├── file_sorter.py      # AI file classification
│   └── web_server.py       # Web interface server
└── web/                    # Web interface files
    ├── index.html          # Pokedex interface
    ├── styles.css          # Pokedex styling
    ├── app.js              # JavaScript controller
    └── assets/             # Audio/image assets
```

### Adding New Features
1. **Voice Commands**: Add to `voice_processor.py`
2. **AI Capabilities**: Extend `ultron_main.py`
3. **System Automation**: Add to `system_automation.py`
4. **Web Interface**: Modify `web/` files
5. **API Endpoints**: Extend `web_server.py`

### Performance Optimization
- **Caching**: Implement response caching for repeated queries
- **Threading**: Use async/await for I/O operations
- **Memory**: Monitor and optimize memory usage
- **Models**: Use quantized models for faster inference

## 🐛 Troubleshooting

### Common Issues

#### Voice Recognition Not Working
```bash
# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
python -c "import speech_recognition as sr; r = sr.Recognizer(); print('Mic test:', r.energy_threshold)"
```

#### OCR Not Working
```bash
# Check Tesseract installation
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Windows: Add Tesseract to PATH or set:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### Web Interface Not Loading
- Check firewall settings for port 3000
- Verify no other services using the port
- Check browser console for JavaScript errors

#### High Memory Usage
- Disable local LLM if not needed: `config["offline_mode"] = False`
- Reduce image processing quality
- Clear conversation history regularly

### Debug Mode
```bash
python launch_ultron.py --debug
```

This enables:
- Detailed logging
- Exception stack traces
- Performance timing
- Component status monitoring

## 📚 Documentation

### Architecture Overview
ULTRON follows a modular architecture:
- **Core System** (`ultron_main.py`) - Central coordinator
- **Voice Processor** - Handles all voice I/O
- **Vision System** - Manages visual processing
- **System Automation** - Controls OS interactions
- **File Sorter** - AI-powered file organization
- **Web Server** - Provides HTTP/WebSocket API

### API Documentation
Full API documentation available at: `http://localhost:3000/api/docs` (when running)

### Configuration Reference
See `config.json` for all available settings and their descriptions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and Whisper speech recognition
- Google for Speech Recognition API
- Tesseract OCR team for text recognition
- Pokemon Company for Pokedex design inspiration
- Open source community for various libraries

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Run the demo script to identify issues
3. Check logs in `D:/ULTRON/logs/`
4. Create an issue with detailed information

---

**🔴 ULTRON AI - Where Voice Meets Intelligence 🔴**
