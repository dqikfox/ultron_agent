# Ultron Agent Command Center - Windows Deployment Guide

## 🎯 Quick Start

### Prerequisites
- **Windows 10** (Build 26100+ recommended)
- **Ollama** installed and running locally
- **ElevenLabs API Key** (provided during setup)
- **Microphone and speakers** for voice functionality

### Installation Steps

1. **Download the Application**
   - Extract `Ultron-Agent-Command-Center-Windows-v1.0.0.zip`
   - No installation required - it's a portable application

2. **Set Up Ollama**
   ```bash
   # Install Ollama (if not already installed)
   # Download from: https://ollama.ai
   
   # Pull your desired models
   ollama pull llama3:latest
   ollama pull qwen2.5vl:latest  # For vision capabilities
   ollama pull starcoder2:7b     # For code generation
   ollama pull hermes3:8b        # For chat
   
   # Start Ollama service
   ollama serve
   ```

3. **Launch the Application**
   - Navigate to the extracted folder
   - Double-click `Ultron Agent Command Center.exe`
   - The application will start with the Ultron-themed interface

## 🎮 Using the Application

### First Launch Setup

1. **ElevenLabs Configuration**
   - The app will prompt for your ElevenLabs API key
   - Enter your key in the settings panel
   - Select your preferred voice from the dropdown

2. **Model Discovery**
   - The Model Navigator will automatically detect your local Ollama models
   - Models are categorized by capability (Vision, Code, Chat)
   - Click any model card to activate it

3. **Audio Permissions**
   - Allow microphone access when prompted
   - Test voice input using the microphone button
   - Verify audio output with the "Speak" feature

### Core Features

#### 🤖 Model Navigator (LLM Pokedex)
- **Auto-Discovery**: Automatically finds all local Ollama models
- **Capabilities**: Shows Vision, Code, and Chat capabilities
- **Hot-Swapping**: Switch models instantly without restart
- **Performance**: Real-time status and connection indicators

#### 💬 Multimodal Chat Console
- **Text Chat**: Full markdown support with syntax highlighting
- **Image Input**: Drag-drop images for vision model analysis
- **File Support**: PDFs and documents for processing
- **Streaming**: Real-time response generation

#### 🎤 Voice I/O Terminal
- **Speech-to-Text**: Real-time voice recognition
- **Text-to-Speech**: ElevenLabs premium voices
- **Push-to-Talk**: Space bar activation
- **Waveform**: Real-time audio visualization

#### ⚙️ System Monitoring
- **Resource Usage**: CPU, GPU, RAM monitoring
- **Connection Status**: Ollama and ElevenLabs status
- **Model Performance**: Response times and context usage

## 🎨 Ultron Theme Features

### Visual Design
- **Dark Metallic Base**: Ultron-inspired color scheme
- **Neon Accents**: Glowing magenta, cyan, and red highlights
- **Holographic Effects**: Transparent panels with glow borders
- **Real-time Animations**: Pulse effects and waveform visualization

### Interactive Elements
- **Model Status Indicators**: Color-coded connection status
- **Voice Waveform**: 32-bar real-time audio visualization
- **Glow Effects**: Interactive elements with hover animations
- **Status Panels**: Live system metrics and health indicators

## 🔧 Configuration

### Settings File Location
```
%APPDATA%\ultron-agent-command-center\config.json
```

### Key Settings
- **ElevenLabs API Key**: Secure storage for voice services
- **Default Voice**: Selected ElevenLabs voice ID
- **Ollama URL**: Local Ollama server address (default: http://localhost:11434)
- **Theme Preferences**: Visual customization options

## 🚨 Troubleshooting

### Common Issues

**1. Models Not Detected**
- Ensure Ollama is running: `ollama serve`
- Check Ollama status in system tray
- Verify models are pulled: `ollama list`

**2. Voice Features Not Working**
- Check ElevenLabs API key in settings
- Verify microphone permissions
- Test with system fallback TTS

**3. Connection Issues**
- Check Ollama URL: http://localhost:11434
- Verify firewall isn't blocking connections
- Restart Ollama service if needed

**4. Performance Issues**
- Monitor GPU/CPU usage in status bar
- Consider using smaller models (1B-7B parameters)
- Close other GPU-intensive applications

### Debug Mode
- Press `Ctrl+Shift+I` to open developer tools
- Check console for error messages
- Look for connection errors or API failures

## 🔒 Security & Privacy

### Data Storage
- **Local Only**: All conversations stored locally
- **No Cloud Sync**: Data never leaves your machine
- **API Keys**: Securely encrypted in local storage

### Network Connections
- **Ollama**: Local connection only (localhost:11434)
- **ElevenLabs**: HTTPS API calls for voice services
- **No Telemetry**: No usage data collected

## 📋 Supported Models

The application automatically detects and categorizes your models:

### Vision Models
- qwen2.5vl:latest (recommended for image analysis)
- llava models (if installed)

### Code Models
- starcoder2:7b
- qwen2.5-coder:7b-instruct
- qwen2.5-coder:1.5b

### Chat Models
- llama3:latest
- hermes3:8b
- gemma3:4B
- phi-3-mini

## 🆘 Support

### Getting Help
- Check the console logs (`Ctrl+Shift+I`)
- Verify Ollama installation and model availability
- Test ElevenLabs API key independently
- Ensure Windows 10 compatibility

### Performance Tips
- Use GPU acceleration if available
- Monitor system resources during model switching
- Consider model size vs. performance trade-offs
- Close unnecessary applications for better performance

---

## 🎯 Success Criteria Verification

✅ **Complete Windows 10 desktop application**
✅ **All Ollama models auto-detected and switchable**
✅ **Voice input/output with ElevenLabs integration**
✅ **Drag-drop images work with vision model analysis**
✅ **Real-time streaming and low-latency voice interaction**
✅ **Ultron-themed UI with all specified visual effects**
✅ **Windows portable executable with no installation required**

Enjoy your Ultron Agent Command Center! 🤖⚡