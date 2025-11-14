# ULTRON Agent 3.0 - Technology Stack

## Programming Languages

### Python 3.10+
**Primary Language** - All core components and services
- **Version**: 3.10.0+ (verified in setup)
- **Usage**: Backend services, AI integration, automation, tools
- **Key Features**: Async/await, type hints, dataclasses, pattern matching

### JavaScript/TypeScript
**Frontend & Web Components**
- **Usage**: Web GUI, Avatar Game, interactive interfaces
- **Frameworks**: React, Vite, vanilla JS for Pokédex GUI
- **Features**: ES6+, async/await, WebSocket communication

### Batch/PowerShell
**Windows Automation**
- **Usage**: Launcher scripts, system diagnostics, setup automation
- **Files**: run.bat, setup_requirements.bat, verify_setup.bat
- **Features**: Process management, health checks, error handling

### HTML/CSS
**User Interfaces**
- **Usage**: Web GUI, Avatar Game, mobile interface
- **Styling**: Custom CSS, retro gaming themes, responsive design
- **Features**: Flexbox, Grid, animations, particle effects

## Core Frameworks & Libraries

### AI & Machine Learning

#### Ollama (Primary LLM Backend)
- **Version**: Latest (local installation)
- **Endpoint**: http://localhost:11434
- **Models**: llava:7b (primary), qwen3-coder:480b-cloud, deepseek-r1:14b
- **Usage**: Local AI model inference, vision processing, chat

#### LangChain 0.2.17
- **Purpose**: AI orchestration and chaining
- **Features**: Prompt templates, chains, agents, memory
- **Integration**: Langflow workflows, tool calling

#### Transformers 4.36.2
- **Purpose**: Hugging Face model integration
- **Usage**: Model loading, tokenization, inference
- **Models**: GPT-J, GPT-NeoX, custom fine-tuned models

#### PyTorch 2.1.2
- **Purpose**: Deep learning framework
- **Configuration**: CUDA support with CPU fallback
- **Features**: Float16 precision, int8 quantization
- **Usage**: Model inference, custom neural networks

### Web Frameworks

#### FastAPI 0.104.1
- **Purpose**: REST API server (port 5000)
- **Features**: Async support, automatic OpenAPI docs, WebSocket
- **Usage**: API endpoints, real-time communication, function calling

#### Flask 3.0.0
- **Purpose**: Web GUI server (port 8080), mobile interface (port 8001)
- **Features**: Lightweight, flexible routing, template rendering
- **Usage**: Pokédex GUI, Avatar Game, mobile web interface

#### Socket.IO
- **Purpose**: Real-time bidirectional communication
- **Usage**: Live chat, system monitoring, event broadcasting
- **Integration**: Agent core, web GUI, avatar game

### Voice & Audio

#### ElevenLabs 1.2.0
- **Purpose**: Primary TTS/STT engine
- **Features**: Neural voice synthesis, voice cloning, streaming
- **Configuration**: API key via environment variable
- **Fallback**: pyttsx3 → OpenAI TTS → Web Speech → Console

#### SpeechRecognition
- **Purpose**: Local STT fallback
- **Engines**: Google Speech, Sphinx, Whisper
- **Usage**: Wake word detection, voice commands

#### pyttsx3
- **Purpose**: Offline TTS fallback
- **Engines**: SAPI5 (Windows), nsss (macOS), espeak (Linux)
- **Usage**: Voice output when cloud services unavailable

### Vision & OCR

#### Tesseract OCR
- **Purpose**: Text extraction from images
- **Installation**: Multiple path detection (Program Files, AppData)
- **Usage**: Screenshot analysis, document processing

#### PyAutoGUI
- **Purpose**: Screen capture and automation
- **Features**: Screenshot, mouse/keyboard control, image recognition
- **Usage**: System automation, GUI testing, OCR input

#### Pillow (PIL)
- **Purpose**: Image processing
- **Features**: Format conversion, resizing, filtering
- **Usage**: Screenshot preprocessing, image analysis

### Database & Storage

#### SQLite3
- **Purpose**: Persistent conversation storage
- **Database**: avatar_game.db
- **Schema**: Conversations, relationship scores, message history
- **Usage**: Cross-session memory, avatar interactions

#### JSON
- **Purpose**: Configuration and data storage
- **Files**: ultron_config.json, model_avatars.json, llm_models.json
- **Usage**: Settings, model metadata, tool schemas

### Cloud Services

#### AWS SDK (boto3)
- **Services**: Bedrock, Lambda, S3, Polly, Secrets Manager, Config
- **Region**: us-east-1 (configurable)
- **Authentication**: Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- **Usage**: Cloud AI, storage, voice synthesis, secrets management

#### Azure SDK
- **Services**: Cognitive Services, Logic Apps, Automation, Functions
- **Authentication**: Environment variables
- **Usage**: LUIS, Text Analytics, Speech Services

#### Google Cloud SDK
- **Services**: Cloud AI, Storage, Functions
- **Authentication**: Service account JSON
- **Usage**: Cloud integration, API access

## Development Tools

### Package Management

#### pip (Python)
- **File**: requirements.txt (59 packages)
- **Total Size**: ~2.5GB
- **Install Time**: 15-25 minutes
- **Virtual Environment**: .venv/ (recommended)

#### npm/pnpm (JavaScript)
- **File**: package.json
- **Workspace**: assistant/ai-assistant
- **Package Manager**: pnpm@10.12.4
- **Usage**: React assistant, frontend dependencies

### Version Control

#### Git
- **Repository**: https://github.com/dqikfox/ultron_agent.git
- **Branches**: main, development, feature branches
- **Ignore**: .gitignore (build/, logs/, cache/, .env)

### IDE Integration

#### VS Code
- **Extensions**: Amazon Q, GitHub Copilot, Continue, Sixth AI
- **Configuration**: .vscode/settings.json
- **Features**: AI-optimized workspace, proposed APIs, auto-approval

#### Amazon Q
- **Purpose**: AWS AI coding assistant
- **Features**: ULTRON architecture awareness, auto-approval
- **Rules**: .amazonq/rules/ (amazon_Q_Rules.md, write.md)

#### GitHub Copilot
- **Purpose**: AI pair programmer
- **Features**: ULTRON pattern recognition, context-aware suggestions
- **Integration**: Copilot + Amazon Q bridge

#### Continue Extension
- **Purpose**: Multi-model LLM integration
- **Configuration**: .continue/config.yaml
- **Features**: MCP orchestration, codebase documentation
- **Models**: Ollama, OpenAI, Anthropic, custom endpoints

### Testing

#### pytest
- **Configuration**: pytest.ini, conftest.py
- **Coverage**: .coverage, htmlcov/
- **Tests**: tests/ (50+ test files)
- **Usage**: Unit tests, integration tests, GUI validation

#### unittest
- **Purpose**: Standard library testing
- **Usage**: Legacy tests, simple test cases

## Build & Deployment

### Automation Scripts

#### setup_requirements.bat
- **Purpose**: One-command dependency installer
- **Features**: AWS CLI verification, Python validation, venv setup
- **Duration**: 15-25 minutes
- **Output**: Comprehensive installation log

#### verify_setup.bat
- **Purpose**: 24-point system diagnostic
- **Checks**: Windows version, disk space, Python, packages, ports
- **Output**: Real-time pass/fail reporting

#### run.bat
- **Purpose**: Master launcher with health checks
- **Features**: Process cleanup, Ollama startup, service launch
- **Health Checks**: 5 automated tests (service, model, generation, chat, context)
- **Ports**: 11434 (Ollama), 8080 (GUI), 5000 (API)

### Containerization

#### Docker
- **File**: Dockerfile
- **Compose**: docker-compose.yml, docker-compose-sd.yml
- **Images**: Python 3.10, Ollama, Stable Diffusion
- **Networks**: Bridge networking, DNS resolution

### Cloud Deployment

#### AWS CloudFormation
- **Template**: aws_integration/EnableAWSConfig.yml
- **Resources**: Config, S3, IAM roles, Lambda functions
- **Deployment**: aws cloudformation create-stack

#### Azure Resource Manager
- **Template**: azure_automation/azure_template.json
- **Resources**: Logic Apps, Automation accounts, Functions
- **Deployment**: az deployment group create

## Configuration Management

### Environment Variables
```bash
# AI Services
OPENAI_API_KEY
ANTHROPIC_API_KEY
ELEVENLABS_APIKEY
GEMINI_API_KEY

# AWS
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION

# Azure
AZURE_LUIS_ENDPOINT
AZURE_LUIS_KEY
AZURE_SPEECH_KEY
AZURE_TEXT_ANALYTICS_KEY

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS
```

### Configuration Files
- **ultron_config.json**: Primary configuration (150+ settings)
- **.env**: Environment variables (not committed)
- **.env.example**: Template for environment setup
- **ultron_config.json.example**: Template for configuration

## Development Commands

### Setup & Installation
```bash
# Install dependencies
.\setup_requirements.bat

# Verify installation
.\verify_setup.bat

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Running Services
```bash
# Master launcher (recommended)
.\run.bat

# Individual services
python main.py                    # Core agent
python web_gui_server.py          # Web GUI
python avatar_game_server.py      # Avatar Game
python api_server.py              # REST API
python nvidia_enhanced_ultron.py  # AI Chat
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent_features.py

# Run with coverage
pytest --cov=. --cov-report=html

# Health checks
.\test_ollama_communication.ps1
```

### Model Management
```bash
# List installed models
ollama list

# Pull new model
ollama pull llava:7b

# Run model directly
ollama run llava:7b

# Check model status
curl http://localhost:11434/api/tags
```

### Diagnostics
```bash
# Check system status
python ultron_diagnostic.py

# Monitor performance
python resource_monitor.py

# View logs
Get-Content logs\agent_core.log -Tail 50
Get-Content ultron_master_startup.log -Tail 50
```

### Cloud Deployment
```bash
# AWS setup
aws configure
aws cloudformation create-stack --stack-name ultron-aws-config --template-body file://EnableAWSConfig.yml

# Azure setup
az login
az deployment group create --resource-group ultron-rg --template-file azure_template.json

# Docker deployment
docker-compose up -d
docker-compose logs -f
```

## Performance Specifications

### System Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.10.0+
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space (5GB for dependencies, 5GB for models)
- **GPU**: Optional (CUDA support for PyTorch)

### Port Allocation
- **11434**: Ollama AI backend
- **8080**: Web GUI (Pokédex interface)
- **8002**: Avatar Game server
- **8001**: Mobile web interface
- **8000**: AI Chat server (NVIDIA enhanced)
- **5175**: Frontend UI server
- **5000**: REST API server
- **2222**: SSH server

### Performance Metrics
- **Startup Time**: 5-15 seconds (with health checks)
- **Model Load Time**: 3-10 seconds (depends on model size)
- **Response Time**: 1-5 seconds (local models), 2-10 seconds (API models)
- **Voice Latency**: 500ms-2s (ElevenLabs), 1-3s (fallback engines)
- **Memory Usage**: 2-8GB (depends on loaded models)

## Security Considerations

### Authentication
- **API Keys**: Environment variables only (no hardcoded credentials)
- **SSH**: Password authentication with configurable allowed users
- **AWS**: IAM roles and policies, Secrets Manager integration
- **Azure**: Managed identities, Key Vault integration

### Data Protection
- **Logs**: Sanitized error messages without sensitive data
- **Config**: .gitignore excludes .env, credentials, keys
- **Network**: Timeout and retry logic for external APIs
- **Input**: Validation and sanitization for all user inputs

### Compliance
- **NIST Guidelines**: Security best practices implementation
- **AWS Config**: Compliance monitoring and auditing
- **Audit Logging**: All AI decisions tracked with context
- **Error Tracking**: Comprehensive error history with timestamps
