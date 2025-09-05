# ULTRON Agent Installation Guide

This guide provides detailed installation instructions for ULTRON Agent 3.0 across different operating systems and deployment scenarios.

## 📋 System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **Python**: 3.10 or higher
- **Memory**: 4 GB RAM (8 GB recommended)
- **Storage**: 2 GB available disk space
- **Network**: Internet connection for AI model downloads and API access

### Recommended Requirements

- **Memory**: 16 GB RAM for optimal performance
- **Storage**: 10 GB available disk space (for local models)
- **CPU**: Multi-core processor (4+ cores recommended)
- **GPU**: NVIDIA GPU with CUDA support (optional, for local AI models)

## 🖥 Platform-Specific Installation

### Windows

#### Method 1: Using pip (Recommended)

```powershell
# Check Python version
python --version

# Clone repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install ULTRON Agent
pip install -e ".[gui,ml]"

# Copy configuration files
copy ultron_config.json.example ultron_config.json
copy .env.example .env
```

#### Method 2: Using Chocolatey

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python and Git
choco install python git

# Follow Method 1 steps above
```

#### Windows-Specific Dependencies

```powershell
# Install audio dependencies for voice features
pip install pyaudio

# If PyAudio installation fails, install from wheel
pip install https://github.com/intxcc/pyaudio_portaudio/raw/master/pyaudio-0.2.11-cp310-cp310-win_amd64.whl

# For development with GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### macOS

#### Method 1: Using Homebrew (Recommended)

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python@3.11 git

# Clone repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install ULTRON Agent
pip install -e ".[gui,ml]"

# Copy configuration files
cp ultron_config.json.example ultron_config.json
cp .env.example .env
```

#### macOS-Specific Dependencies

```bash
# Install audio dependencies
brew install portaudio
pip install pyaudio

# For M1/M2 Macs with Apple Silicon
pip install torch torchvision torchaudio

# For Intel Macs with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python, pip, and development tools
sudo apt install python3.10 python3.10-pip python3.10-venv git build-essential

# Install system dependencies for audio
sudo apt install portaudio19-dev python3-pyaudio libasound2-dev

# For GUI support
sudo apt install python3-tk

# Clone repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install ULTRON Agent
pip install -e ".[gui,ml]"

# Copy configuration files
cp ultron_config.json.example ultron_config.json
cp .env.example .env
```

### Linux (CentOS/RHEL/Fedora)

```bash
# For CentOS/RHEL 8+
sudo dnf install python3.10 python3.10-pip python3.10-devel git gcc gcc-c++

# For older versions
sudo yum install python3 python3-pip python3-devel git gcc gcc-c++

# Install audio dependencies
sudo dnf install portaudio-devel alsa-lib-devel  # or yum for older versions

# Follow Ubuntu installation steps from here
```

## 🐳 Docker Installation

### Using Pre-built Image

```bash
# Pull the latest image
docker pull dqikfox/ultron-agent:latest

# Run with volume mounts for configuration
docker run -d \
  --name ultron-agent \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  dqikfox/ultron-agent:latest
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Build Docker image
docker build -t ultron-agent .

# Run container
docker run -d \
  --name ultron-agent \
  -p 8000:8000 \
  -v $(pwd)/ultron_config.json:/app/ultron_config.json \
  -v $(pwd)/.env:/app/.env \
  ultron-agent
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ultron-agent:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./ultron_config.json:/app/ultron_config.json
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - ULTRON_LOG_LEVEL=INFO
    restart: unless-stopped

  # Optional: Local Ollama instance
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

```bash
# Start services
docker-compose up -d
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (required for cloud services)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NVIDIA_API_KEY=your_nvidia_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional Settings
ULTRON_LOG_LEVEL=INFO
ULTRON_GUI_MODE=pokedex
ULTRON_VOICE_ENGINE=enhanced
ULTRON_DEBUG=false

# Database (if using persistent storage)
DATABASE_URL=sqlite:///./ultron.db

# Security
SECRET_KEY=your-secret-key-for-sessions
JWT_SECRET=your-jwt-secret-for-api-auth
```

### Main Configuration File

Edit `ultron_config.json`:

```json
{
  "models": {
    "ollama": {
      "enabled": true,
      "host": "http://localhost:11434",
      "model": "llama3.2:latest",
      "timeout": 60
    },
    "openai": {
      "enabled": true,
      "model": "gpt-4o",
      "max_tokens": 4000
    },
    "anthropic": {
      "enabled": false,
      "model": "claude-3-sonnet-20240229"
    },
    "nvidia": {
      "enabled": false,
      "model": "meta/llama-3.1-70b-instruct"
    }
  },
  "voice": {
    "enabled": true,
    "engine": "enhanced",
    "fallback_chain": ["pyttsx3", "openai", "console"],
    "language": "en-US",
    "rate": 200,
    "volume": 0.8
  },
  "gui": {
    "enabled": true,
    "theme": "dark",
    "accessibility_mode": true,
    "default_interface": "pokedex"
  },
  "logging": {
    "level": "INFO",
    "file_enabled": true,
    "console_enabled": true,
    "max_file_size": "10MB",
    "backup_count": 5
  },
  "security": {
    "encrypt_keys": true,
    "validate_inputs": true,
    "rate_limiting": true,
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"]
  }
}
```

## 🤖 AI Model Setup

### Ollama (Local Models)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Or on Windows/Mac, download from https://ollama.ai/

# Start Ollama service
ollama serve

# Download and run models
ollama pull llama3.2:latest
ollama pull codellama:latest
ollama pull mistral:latest

# Test model
ollama run llama3.2:latest "Hello, how are you?"
```

### OpenAI Setup

1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an API key
3. Add to your `.env` file: `OPENAI_API_KEY=your_key_here`

### Anthropic Setup

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Add to your `.env` file: `ANTHROPIC_API_KEY=your_key_here`

### NVIDIA NIM Setup

1. Visit [NVIDIA AI Foundation](https://build.nvidia.com/)
2. Get API access
3. Add to your `.env` file: `NVIDIA_API_KEY=your_key_here`

## 🎤 Voice Setup

### Audio System Configuration

#### Windows
```powershell
# Install Windows audio dependencies
pip install pyaudio

# If installation fails, try:
pip install pipwin
pipwin install pyaudio
```

#### macOS
```bash
# Install PortAudio
brew install portaudio

# Install Python audio dependencies
pip install pyaudio
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install portaudio19-dev python3-pyaudio pulseaudio

# CentOS/RHEL
sudo dnf install portaudio-devel pulseaudio-libs-devel
```

### ElevenLabs Voice Setup (Optional)

1. Sign up at [ElevenLabs](https://elevenlabs.io/)
2. Get your API key from settings
3. Add to `.env`: `ELEVENLABS_API_KEY=your_key_here`

## 🌐 Web Interface Setup

### Development Mode

```bash
# Install Node.js dependencies (if using React components)
cd web_gui
npm install

# Start development server
npm run dev

# In another terminal, start ULTRON Agent
cd ..
python main.py --web
```

### Production Deployment

```bash
# Build frontend assets
cd web_gui
npm run build

# Start production server
cd ..
python -m uvicorn agent_core:app --host 0.0.0.0 --port 8000
```

## 🔧 Verification

### Test Installation

```bash
# Test basic functionality
python -c "from ultron_agent import UltronAgent; print('Installation successful!')"

# Run system diagnostics
python main.py --diagnose

# Test voice system (if configured)
python main.py --test-voice

# Test web interface
curl http://localhost:8000/health
```

### Run Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run test suite
pytest

# Run with coverage
pytest --cov=ultron_agent
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version

# If version is < 3.10, install newer version
# Ubuntu/Debian
sudo apt install python3.11

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

#### 2. PyAudio Installation Failures

**Windows:**
```powershell
# Try binary wheel
pip install https://github.com/intxcc/pyaudio_portaudio/raw/master/pyaudio-0.2.11-cp310-cp310-win_amd64.whl
```

**macOS:**
```bash
# Install build dependencies
xcode-select --install
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt install portaudio19-dev python3-dev
pip install pyaudio
```

#### 3. Permission Errors

```bash
# Linux/macOS: Add user to audio group
sudo usermod -a -G audio $USER

# Restart shell or logout/login
```

#### 4. Firewall Issues

```bash
# Windows: Allow Python through firewall
# Linux: Allow port 8000
sudo ufw allow 8000

# macOS: Allow in System Preferences > Security & Privacy
```

#### 5. Memory Issues

```bash
# Increase virtual memory (Linux/macOS)
sudo sysctl vm.overcommit_memory=1

# Monitor memory usage
python main.py --monitor-memory
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](FAQ.md)
2. Search [GitHub Issues](https://github.com/dqikfox/ultron_agent/issues)
3. Run diagnostics: `python main.py --diagnose`
4. Create a new issue with:
   - Operating system and version
   - Python version
   - Error messages and logs
   - Steps to reproduce

## 🔄 Updates and Maintenance

### Updating ULTRON Agent

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -e ".[gui,ml]" --upgrade

# Update models (Ollama)
ollama pull llama3.2:latest

# Restart services
python main.py --restart
```

### Backup and Recovery

```bash
# Backup configuration
cp ultron_config.json ultron_config.json.backup
cp .env .env.backup

# Backup logs and data
tar -czf ultron_backup_$(date +%Y%m%d).tar.gz logs/ cache/ ultron_config.json .env
```

---

**Installation complete! You're ready to use ULTRON Agent 3.0.** 🚀

For next steps, see the [Usage Guide](USAGE.md) and [API Documentation](docs/API.md).