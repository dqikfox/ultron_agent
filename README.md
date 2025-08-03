# 🤖 ULTRON Agent 3.0 - Ultimate AI Assistant

> *"I was designed to save the world. People would look to the sky and see hope."* - Vision

**ULTRON Agent 3.0** is a cutting-edge, fully autonomous AI assistant featuring advanced voice processing, real-time vision capabilities, stunning GUI interface, and deep system integration. Built with enterprise-grade architecture and professional startup experience.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com/windows)
[![Ollama](https://img.shields.io/badge/AI-Ollama-orange.svg)](https://ollama.ai)

## 🚀 **Professional Quick Start**

### **🎯 One-Click Launch**
```batch
# Simply double-click run.bat for professional startup experience!
.\run.bat
```

The enhanced startup script automatically handles:
- ✅ **System Diagnostics** - Complete hardware detection
- ✅ **Python Verification** - Version compatibility checking  
- ✅ **Ollama Integration** - Service detection with model inventory
- ✅ **GPU Detection** - NVIDIA & Intel graphics enumeration
- ✅ **Network Validation** - Connectivity testing
- ✅ **Process Management** - Intelligent conflict resolution

---

## 🎨 **Stunning Features**

### 🎤 **Advanced Voice System**
- **Multi-Engine Fallback Chain**: Enhanced → pyttsx3 → OpenAI → Console
- **Thread-Safe Processing**: Eliminates audio conflicts
- **Real-Time Recognition**: Multiple STT engines with smart fallbacks
- **Organization API Support**: Professional OpenAI integration

### 🤖 **Intelligent Model Management**  
- **10+ AI Models**: qwen2.5, llama3.2, hermes3, phi-3-mini, and more
- **Smart Model Switching**: One-click model changes via `ollama run`
- **Real-Time Status**: Live model monitoring and performance tracking
- **Automatic Model Pulling**: Seamless model downloading when needed

### 🖥️ **Professional GUI Interface**
- **Cyberpunk Theme**: Ultron-inspired visual design
- **Real-Time Monitoring**: CPU, Memory, GPU, Network status
- **Interactive Controls**: Voice testing, model switching, system diagnostics
- **Professional Logging**: Timestamped conversation history

### 🔧 **Enterprise System Integration**
- **Hardware Detection**: NVIDIA RTX 3050 + Intel UHD Graphics support
- **Network Monitoring**: Real-time connectivity and performance tracking
- **Process Management**: Smart conflict detection and resolution
- **Enhanced Logging**: Comprehensive error tracking and diagnostics

---

## 📋 **System Requirements**

| Component | Requirement | Status |
|-----------|-------------|---------|
| **OS** | Windows 10+ | ✅ Tested on 10.0.26120.5722 |
| **Python** | 3.10+ | ✅ Confirmed working |
| **Memory** | 8GB+ RAM | ✅ Required for AI models |
| **GPU** | NVIDIA RTX (optional) | ✅ Detected RTX 3050 |
| **Network** | Internet connection | ✅ Required for API access |
| **Storage** | 10GB+ free space | ✅ For AI models |

---

## 🛠️ **Installation Guide**

### **Method 1: Professional Setup (Recommended)**
```batch
# 1. Clone or extract ULTRON Agent 3.0
# 2. Double-click run.bat
# 3. Follow automated setup prompts
# 4. Enjoy your AI assistant!
```

### **Method 2: Manual Setup**
```bash
# Install Python 3.10+
python --version

# Install Ollama
# Download from: https://ollama.ai
ollama run qwen2.5:latest

# Install Python dependencies
pip install -r requirements.txt

# Configure API keys in ultron_config.json
# Run the agent
python main.py
```

---

## 🎯 **Usage Examples**

### **Voice Commands**
```
"Hey ULTRON, what model are you?"
"Switch to qwen2.5 model"
"Take a screenshot"
"Show system information"
"Test voice output"
```

### **GUI Operations**
- 🔊 **Voice Testing**: Click "Test Voice" for multi-engine verification
- 🤖 **Model Switching**: Use dropdown to change AI models instantly  
- 📊 **System Monitor**: Real-time hardware and network status
- 🖼️ **Screenshots**: Instant screen capture with timestamping
- 📁 **File Manager**: Quick access to project directory

### **API Access**
```bash
# Web Interface
http://127.0.0.1:5000

# Network Access  
http://192.168.1.118:5000

# REST API Endpoints
curl http://localhost:5000/api/status
```

---

## 🏗️ **Architecture Overview**

```
ULTRON Agent 3.0
├── 🎤 Voice System (voice_manager.py)
│   ├── Enhanced Voice Engine
│   ├── Multi-Engine Fallbacks  
│   └── Thread-Safe Processing
├── 🤖 AI Integration (ollama_manager.py)
│   ├── Model Management
│   ├── Smart Switching
│   └── Status Monitoring
├── 🖥️ GUI Interface (gui_compact.py)
│   ├── Cyberpunk Theme
│   ├── Real-Time Monitoring
│   └── Interactive Controls
├── 🔧 System Core (agent_core.py)
│   ├── Process Management
│   ├── Error Handling
│   └── Integration Hub
└── 🚀 Enhanced Startup (run.bat)
    ├── System Diagnostics
    ├── Hardware Detection
    └── Professional Logging
```

---

## 🎨 **Available AI Models**

| Model | Size | Specialty | Status |
|-------|------|-----------|---------|
| **qwen2.5:latest** | 4.7GB | General Purpose | ✅ Default |
| **llama3.2:latest** | 2.0GB | Conversational | ✅ Ready |
| **hermes3:latest** | 4.7GB | Advanced Reasoning | ✅ Ready |
| **phi-3-mini** | 2.8GB | Efficient Processing | ✅ Ready |
| **qwen3:0.6b** | 522MB | Lightweight | ✅ Ready |
| **mxbai-embed** | 669MB | Embeddings | ✅ Ready |

*And 4 more specialized models available for advanced operations*

---

## 🔧 **Configuration**

### **ultron_config.json**
```json
{
  "openai_api_key": "sk-proj-...",
  "openai_organization": "org-...",
  "openai_project": "proj_...",
  "llm_model": "qwen2.5:latest",
  "voice_engine": "pyttsx3",
  "use_gui": true,
  "use_voice": true
}
```

### **Environment Variables**
```bash
# Set OpenAI API key
set OPENAI_API_KEY=sk-proj-...

# Optional: Organization settings
set OPENAI_ORG=org-...
set OPENAI_PROJECT=proj_...
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

| Issue | Solution | 
|-------|----------|
| 🔇 **No Voice Output** | Check voice test button - fallback to console working |
| 🤖 **Ollama Not Found** | Install from https://ollama.ai and run `ollama serve` |
| 🐍 **Python Errors** | Ensure Python 3.10+ and run `pip install -r requirements.txt` |
| 🔑 **API Key Issues** | Update ultron_config.json with valid OpenAI credentials |
| 🖥️ **GUI Problems** | Check startup.log for detailed error information |

### **Log Files**
- 📄 **startup.log**: Professional startup diagnostics
- 📄 **error.log**: Detailed error tracking  
- 📄 **ultron_gui.log**: GUI operations and status
- 📄 **ultron.log**: Core system operations

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/dqikfox/ultron_agent.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Start development server
python main.py --debug
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 **Achievements**

- ✅ **Professional Startup**: Enterprise-grade initialization system
- ✅ **Hardware Detection**: Complete GPU and system enumeration  
- ✅ **Voice Excellence**: Multi-engine fallback with 100% reliability
- ✅ **AI Model Mastery**: 10+ models with seamless switching
- ✅ **GUI Perfection**: Cyberpunk-themed professional interface
- ✅ **Organization API**: Advanced OpenAI integration support
- ✅ **Windows Integration**: Advanced CMD features and monitoring

---

**🎉 Experience the future of AI assistance with ULTRON Agent 3.0!**

*Built with ❤️ for the AI community*

---

## 📞 **Support**

- 📧 **Email**: [Your Support Email]
- 💬 **Discord**: [Your Discord Server]
- 🐛 **Issues**: [GitHub Issues](https://github.com/dqikfox/ultron_agent/issues)
- 📖 **Documentation**: [Wiki](https://github.com/dqikfox/ultron_agent/wiki)
