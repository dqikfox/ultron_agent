# Ultron Agent Command Center

> A sophisticated AI command center with Ultron-inspired aesthetics for managing local Ollama models with voice integration.

## Overview

The Ultron Agent Command Center is a production-ready desktop application that provides a futuristic interface for interacting with local AI models. Built with Electron, React, and TypeScript, it features real-time voice integration via ElevenLabs and comprehensive model management for Ollama.

## Key Features

### 🤖 AI Model Management
- **Auto-Discovery**: Automatically detects all local Ollama models
- **Hot-Swapping**: Switch between models without restart
- **Capability Detection**: Identifies Vision, Code, and Chat models
- **Performance Monitoring**: Real-time metrics and status indicators

### 🎤 Voice Integration
- **Speech-to-Text**: Real-time voice recognition with Web Speech API
- **Text-to-Speech**: Premium ElevenLabs voices with fallbacks
- **Waveform Visualization**: 32-bar real-time audio display
- **Push-to-Talk**: Space bar activation with visual feedback

### 🎨 Ultron Theme
- **Dark Aesthetic**: Metallic surfaces with neon accents
- **Holographic Effects**: Glowing panels and interactive elements
- **Real-time Animations**: Pulse effects and dynamic visualizations
- **Professional Layout**: Modular grid-based interface

### 🔧 System Monitoring
- **Resource Tracking**: CPU, GPU, and RAM usage
- **Connection Status**: Ollama and ElevenLabs service monitoring
- **Performance Metrics**: Response times and model statistics

## Quick Start

### Prerequisites
- Windows 10 (Build 26100+)
- [Ollama](https://ollama.ai) installed and running
- ElevenLabs API key for voice features
- Microphone and speakers for voice interaction

### Installation

1. **Download the Application**
   ```
   Download: Ultron-Agent-Command-Center-Windows-v1.0.0.zip
   Extract to desired location
   ```

2. **Set Up Ollama**
   ```bash
   # Pull recommended models
   ollama pull llama3:latest
   ollama pull qwen2.5vl:latest  # For vision
   ollama pull hermes3:8b        # For chat
   ollama pull starcoder2:7b     # For code
   
   # Start Ollama service
   ollama serve
   ```

3. **Launch Application**
   ```
   Double-click: Ultron Agent Command Center.exe
   ```

### First-Time Setup

1. Enter your ElevenLabs API key when prompted
2. Grant microphone permissions for voice input
3. Select your preferred voice from the dropdown
4. The Model Navigator will auto-detect your Ollama models

## Architecture

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Electron 28 + Node.js
- **Styling**: Custom CSS with Ultron theme
- **APIs**: Ollama HTTP API, ElevenLabs REST API
- **Storage**: Electron Store for persistent settings

### Core Services
- **OllamaService**: Model discovery and chat management
- **ElevenLabsService**: Voice synthesis and recognition
- **DatabaseService**: Local data persistence
- **SystemMetricsService**: Performance monitoring

## Development

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Package for distribution
npm run electron:dist
```

### Project Structure
```
src/
├── components/          # React components
│   ├── ModelNavigator.tsx
│   ├── VoiceTerminal.tsx
│   └── SystemStatusBar.tsx
├── services/           # Frontend services
├── hooks/              # Custom React hooks
├── types/              # TypeScript definitions
└── styles/             # Ultron theme styles

electron/
├── main.ts             # Electron main process
├── preload.ts          # IPC bridge
└── services/           # Backend services
    ├── ollama-service.ts
    ├── elevenlabs-service.ts
    └── database-service.ts
```

## API Integration

### Ollama API
```typescript
// Model discovery
GET /api/tags → Model list

// Chat completion
POST /api/chat {
  model: "llama3:latest",
  messages: [...],
  stream: true
}
```

### ElevenLabs API
```typescript
// Text-to-Speech
POST /v1/text-to-speech/{voice_id} {
  text: "Hello, world!",
  model_id: "eleven_flash_v2_5"
}

// Voice listing
GET /v1/voices
```

## Configuration

### Settings Location
- **Windows**: `%APPDATA%\ultron-agent-command-center\config.json`
- **macOS**: `~/Library/Application Support/ultron-agent-command-center/config.json`
- **Linux**: `~/.config/ultron-agent-command-center/config.json`

### Key Settings
```json
{
  "elevenLabsApiKey": "your-api-key",
  "selectedVoice": "voice-id",
  "ollamaUrl": "http://localhost:11434",
  "theme": "ultron-dark",
  "audioSettings": {
    "inputDevice": "default",
    "outputDevice": "default"
  }
}
```

## Troubleshooting

### Common Issues

**Models not detected**
- Verify Ollama is running: `ollama serve`
- Check models are installed: `ollama list`
- Ensure firewall allows localhost connections

**Voice features not working**
- Verify ElevenLabs API key
- Check microphone permissions
- Test with browser speech recognition fallback

**Performance issues**
- Monitor resource usage in status bar
- Use smaller models for better performance
- Ensure adequate GPU memory for large models

### Debug Mode
- Press `Ctrl+Shift+I` to open developer tools
- Check console for error messages
- Monitor network requests and responses

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- TypeScript strict mode enabled
- ESLint + Prettier for code formatting
- React functional components with hooks
- Comprehensive error handling

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- **Ollama** for local LLM inference
- **ElevenLabs** for high-quality voice synthesis
- **Electron** for cross-platform desktop development
- **React** for the user interface framework

---

**Built with ⚡ by MiniMax Agent**

*Experience the future of AI interaction with Ultron Agent Command Center*