# Windows Deployment Guide

## System Requirements
- Windows 10 Build 26100 or later
- Node.js 18+ (for development)
- Visual Studio Build Tools 2019+ (for native modules)
- Python 3.8+ (for native compilation)

## Pre-Deployment Setup

### 1. Install Build Dependencies
```powershell
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2019.BuildTools

# Install Python
winget install Python.Python.3.11

# Install Node.js
winget install OpenJS.NodeJS
```

### 2. Configure Environment
```powershell
# Set environment variables
$env:PYTHON_PATH = "C:\\Python311\\python.exe"
$env:GYP_MSVS_VERSION = "2019"

# Restart PowerShell after installation
```

## Build Process

### 1. Clone and Setup
```powershell
git clone <repository>
cd ultron-agent-command-center
npm install
```

### 2. Production Build
```powershell
# Build application
npm run build

# Create Windows installer
npm run electron:dist
```

### 3. Output Files
- `release/Ultron Agent Command Center Setup.exe` - Windows installer
- `release/win-unpacked/` - Portable application folder

## Installation Options

### Option 1: Use Installer (Recommended)
1. Run `Ultron Agent Command Center Setup.exe`
2. Follow installation wizard
3. Desktop and Start Menu shortcuts created automatically

### Option 2: Portable Version
1. Copy `win-unpacked` folder to desired location
2. Run `Ultron Agent Command Center.exe`
3. Create shortcuts manually if needed

## Post-Installation Setup

### 1. Install Ollama
```powershell
# Download and install Ollama
winget install Ollama.Ollama

# Start Ollama service
ollama serve

# Pull recommended models
ollama pull llama3:latest
ollama pull qwen2.5vl:latest
ollama pull qwen2.5-coder:7b-instruct
ollama pull hermes3:8b
```

### 2. Configure ElevenLabs (Optional)
1. Get API key from https://elevenlabs.io
2. Set environment variable: `ELEVENLABS_API_KEY=your_key_here`
3. Restart application

### 3. Windows Firewall
If prompted, allow application through Windows Firewall for:
- Ollama communication (port 11434)
- WebSocket server (port 8080)

## Troubleshooting

### Build Issues

**SQLite3 Build Error**
```powershell
# Install windows-build-tools
npm install -g windows-build-tools

# Rebuild sqlite3
npm rebuild sqlite3
```

**Missing Visual Studio Tools**
```powershell
# Install Visual Studio Build Tools
npm install -g @vscode/vsce
npm config set msvs_version 2019
```

### Runtime Issues

**Application Won't Start**
- Check Windows version compatibility
- Run as Administrator
- Check Event Viewer for error details

**Ollama Connection Failed**
- Verify Ollama is running: `ollama serve`
- Check Windows firewall settings
- Ensure no antivirus blocking

**Voice Features Not Working**
- Grant microphone permissions
- Check audio device settings
- Verify ElevenLabs API key

## Security Considerations

### Code Signing (Production)
```powershell
# Get code signing certificate
# Update package.json build config:
{
  "win": {
    "certificateFile": "path/to/certificate.p12",
    "certificatePassword": "password"
  }
}
```

### Windows SmartScreen
- New applications may trigger SmartScreen warnings
- Users should click "More info" → "Run anyway"
- Code signing resolves this issue

## Distribution

### Internal Distribution
1. Share installer file directly
2. Provide installation instructions
3. Include system requirements

### Microsoft Store (Future)
1. Convert to MSIX package
2. Submit to Microsoft Store
3. Enable automatic updates

## Auto-Updates

### Enable Auto-Updates
```javascript
// In main.ts
import { autoUpdater } from 'electron-updater'

autoUpdater.checkForUpdatesAndNotify()
```

### Update Server Setup
1. Host update files on CDN
2. Configure update URL in package.json
3. Implement update notifications

## Performance Optimization

### System Requirements
- **Minimum**: 8GB RAM, 4-core CPU
- **Recommended**: 16GB RAM, 8-core CPU, GPU acceleration
- **Storage**: 2GB free space + model storage

### Model Optimization
- Use quantized models for better performance
- Cache frequently used models
- Monitor system resources

## Deployment Checklist

- [ ] Visual Studio Build Tools installed
- [ ] Python 3.8+ available
- [ ] Node.js 18+ installed
- [ ] All dependencies resolve correctly
- [ ] Application builds without errors
- [ ] Installer creates successfully
- [ ] Application starts and connects to Ollama
- [ ] Voice features work (if ElevenLabs configured)
- [ ] All UI components render correctly
- [ ] Tool execution works in safe mode
- [ ] Session persistence functions
- [ ] Windows security warnings addressed

## Support

For deployment issues:
1. Check build logs for specific errors
2. Verify all system requirements
3. Test on clean Windows installation
4. Contact support with error details

---

**Deployment Guide by MiniMax Agent**  
*Ensuring smooth Windows deployment*
