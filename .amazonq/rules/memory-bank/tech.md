# Technology Stack - ULTRON Agent 3.0

## Programming Languages

### Primary Languages
- **Python 3.10+**: Core application logic, AI integration, backend services
- **JavaScript/TypeScript**: Web interfaces, React components, frontend logic
- **Batch/PowerShell**: Windows automation scripts, launcher utilities
- **HTML/CSS**: Web GUI interfaces, styling, responsive design

### Language Distribution
- Python: ~85% (backend, AI, tools, utilities)
- JavaScript/TypeScript: ~10% (web interfaces, React apps)
- Batch/PowerShell: ~3% (automation, launchers)
- HTML/CSS: ~2% (web interfaces)

## Core Dependencies

### Python Framework Stack
```
FastAPI 0.104.1          # Modern async web framework for APIs
Flask 3.0.0              # Lightweight web framework for GUIs
Uvicorn 0.24.0           # ASGI server for FastAPI
python-socketio 5.10.0   # Real-time WebSocket communication
```

### AI & Machine Learning
```
PyTorch 2.1.2            # Deep learning framework
Transformers 4.36.2      # Hugging Face model library
LangChain 0.2.17         # LLM orchestration framework
ollama 0.1.6             # Ollama Python client
openai 1.12.0            # OpenAI API client
anthropic 0.18.1         # Anthropic Claude API
```

### Voice & Audio
```
ElevenLabs 1.2.0         # Premium TTS/STT service
pyttsx3 2.90             # Offline TTS fallback
SpeechRecognition 3.10.0 # Speech-to-text library
pyaudio 0.2.13           # Audio I/O
```

### Vision & OCR
```
pytesseract 0.3.10       # Tesseract OCR wrapper
Pillow 10.1.0            # Image processing
opencv-python 4.8.1      # Computer vision
```

### GUI & Automation
```
PyAutoGUI 0.9.54         # GUI automation
pygetwindow 0.0.9        # Window management
keyboard 0.13.5          # Keyboard control
mouse 0.7.1              # Mouse control
```

### Web & Network
```
requests 2.31.0          # HTTP client
aiohttp 3.9.1            # Async HTTP client
beautifulsoup4 4.12.2    # HTML parsing
selenium 4.15.2          # Browser automation
```

### Database & Storage
```
SQLAlchemy 2.0.23        # SQL toolkit and ORM
aiosqlite 0.19.0         # Async SQLite
redis 5.0.1              # In-memory data store
```

### AWS Integration
```
boto3 1.34.0             # AWS SDK for Python
botocore 1.34.0          # AWS core functionality
```

### Utilities
```
python-dotenv 1.0.0      # Environment variable management
pydantic 2.5.2           # Data validation
loguru 0.7.2             # Advanced logging
rich 13.7.0              # Terminal formatting
click 8.1.7              # CLI framework
```

## JavaScript/TypeScript Stack

### Frontend Framework
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0",
  "vite": "^5.0.0"
}
```

### UI Libraries
```json
{
  "@radix-ui/react-*": "^1.0.0",  // Accessible UI components
  "tailwindcss": "^3.4.0",         // Utility-first CSS
  "lucide-react": "^0.263.1"       // Icon library
}
```

## Build Systems & Tools

### Python Environment
- **Package Manager**: pip, pnpm (for JavaScript)
- **Virtual Environment**: venv (.venv/)
- **Dependency Management**: requirements.txt (59 packages, ~2.5GB)
- **Installation Time**: 15-25 minutes

### JavaScript Build
- **Build Tool**: Vite 5.0+
- **Package Manager**: pnpm 10.12.4
- **TypeScript Compiler**: tsc 5.0+
- **Bundler**: Rollup (via Vite)

### Development Tools
- **Linting**: ESLint, Black (Python formatter)
- **Type Checking**: mypy, TypeScript compiler
- **Testing**: pytest, Jest
- **Code Quality**: pylint, prettier

## External Services & APIs

### AI Model Services
- **Ollama**: Local LLM inference (http://localhost:11434)
  - Models: llava:7b, qwen3-coder:480b-cloud, deepseek-r1:14b
- **AWS Bedrock**: Cloud AI models (Claude, Llama)
- **OpenAI API**: GPT-4, GPT-3.5-turbo
- **Anthropic API**: Claude 3 models

### Cloud Services (AWS)
- **Bedrock**: AI model inference
- **Lambda**: Serverless function execution
- **S3**: Cloud storage
- **Polly**: Text-to-speech synthesis
- **Comprehend**: Sentiment analysis
- **Translate**: Multi-language translation
- **Secrets Manager**: API key management
- **Config**: Compliance monitoring

### Voice Services
- **ElevenLabs**: Premium TTS/STT (primary)
- **OpenAI TTS**: Fallback TTS
- **Web Speech API**: Browser-based STT
- **pyttsx3**: Offline TTS fallback

### Database Services
- **SQLite**: Local database (conversation memory, app data)
- **Supabase**: Real-time database (optional)

## Development Commands

### Python Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run main application
python main.py

# Run specific server
python web_gui_server.py
python avatar_game_server.py
python api_server.py

# Run tests
pytest
pytest tests/test_specific.py

# Format code
black .
```

### JavaScript Development
```bash
# Install dependencies
pnpm install

# Run development server
pnpm run dev

# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

### System Commands
```bash
# Master launcher (recommended)
.\run.bat

# Setup dependencies
.\setup_requirements.bat

# Verify installation
.\verify_setup.bat

# Start avatar game
.\start_avatar_game.bat

# Health checks
.\test_ollama_communication.ps1
```

### Ollama Commands
```bash
# List installed models
ollama list

# Pull new model
ollama pull llava:7b

# Run model interactively
ollama run llava:7b

# Check service status
curl http://localhost:11434/api/tags
```

### AWS Commands
```bash
# Configure credentials
aws configure

# Verify access
aws sts get-caller-identity

# Deploy CloudFormation stack
aws cloudformation create-stack --stack-name ultron-aws-config --template-body file://EnableAWSConfig.yml
```

## Configuration Files

### Python Configuration
- **pyproject.toml**: Python project metadata and build configuration
- **pytest.ini**: Test configuration
- **requirements.txt**: Python dependencies (59 packages)

### JavaScript Configuration
- **package.json**: Node.js project metadata and scripts
- **tsconfig.json**: TypeScript compiler configuration
- **vite.config.ts**: Vite build configuration
- **tailwind.config.js**: Tailwind CSS configuration
- **eslint.config.js**: ESLint linting rules

### Application Configuration
- **ultron_config.json**: Primary application configuration
- **.env**: Environment variables (API keys, secrets)
- **.continue/config.yaml**: Continue extension configuration
- **.github/copilot-instructions.md**: GitHub Copilot rules

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher (for JavaScript development)
- **RAM**: 8GB (16GB recommended for AI models)
- **Disk**: 10GB free space (for models and dependencies)
- **GPU**: Optional (CUDA-compatible for PyTorch acceleration)

### Recommended Requirements
- **OS**: Windows 11 or Ubuntu 22.04
- **Python**: 3.11+
- **RAM**: 16GB+
- **Disk**: 50GB+ SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **Network**: Stable internet for cloud services

## Version Information

### Current Versions
- **ULTRON Agent**: 3.0.8
- **Python**: 3.10.0+
- **Node.js**: 18.0+
- **Ollama**: Latest
- **AWS CLI**: 2.31.25

### Compatibility
- **Python**: 3.10, 3.11, 3.12
- **Node.js**: 18.x, 20.x, 22.x
- **Ollama**: 0.1.x
- **AWS SDK**: boto3 1.34.x
