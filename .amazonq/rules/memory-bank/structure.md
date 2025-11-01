# Project Structure - ULTRON Agent 3.0

## Directory Organization

### Core Components
```
ultron_agent/
├── agent_core.py              # Main integration hub - initializes all systems
├── brain.py                   # Core AI logic with Ollama integration
├── main.py                    # Application entry point
├── config.py                  # Configuration loader
├── ultron_config.json         # Primary configuration file
└── run.bat                    # Master launcher with health checks
```

### Tool Ecosystem
```
tools/                         # Modular tool plugins (50+ tools)
├── mobile_web_interface_tool.py    # Flask-based mobile web interface
├── enhanced_ocr_tool.py            # Advanced OCR with image preprocessing
├── windows_system_tool.py          # Windows automation with NLU
├── browser_mcp_tool.py             # Browser automation via MCP
├── aws_bedrock_tool.py             # AWS Bedrock AI integration
├── database_tool.py                # SQLite database operations
├── voice_aws_tool.py               # AWS voice services integration
├── pyautogui_tool.py               # GUI automation
├── web_search_tool.py              # Web search integration
└── [45+ additional tools]
```

### GUI Interfaces
```
gui/
├── ultron_enhanced/web/            # Primary Pokédex GUI (port 8080)
│   ├── index.html                  # Main interface
│   ├── ultron_avatar_game_ultimate.html  # Avatar RPG game
│   └── [CSS/JS assets]
├── ultron_pokedex_complete/        # Complete Pokédex implementation
└── [legacy GUI variants]
```

### Utilities & Infrastructure
```
utils/
├── ultron_logger.py           # Centralized JSON logging system
├── model_awareness.py         # AI model validation and switching
├── event_system.py            # Pub/sub event communication
├── performance_profiler.py    # Real-time performance monitoring
├── port_manager.py            # Port conflict resolution
└── idle_monitor.py            # Idle detection and auto-analysis
```

### Voice & Vision Systems
```
voice_manager.py               # Multi-engine voice system coordinator
voice.py                       # Voice processing implementation
vision.py                      # Vision system with OCR support
enhanced_voice_tool.py         # Enhanced voice capabilities
```

### Server Components
```
web_gui_server.py              # Web GUI server (port 8080)
avatar_game_server.py          # Avatar game server (port 8002)
frontend_server.py             # Frontend UI server (port 5175)
api_server.py                  # REST API server (port 5000)
nvidia_enhanced_ultron.py      # AI chat server (port 8000)
adb_backend_enhanced.py        # ADB device control (port 5003)
```

### AI & Model Management
```
ollama_manager.py              # Ollama model management
model_awareness_validator.py   # Model validation script
ensemble.py                    # Multi-model ensemble system
avatar_db.py                   # Avatar conversation database
ultron_avatar_bridge.py        # ULTRON agent integration bridge
```

### AWS Integration
```
aws_integration/
├── cloudformation/            # Infrastructure as Code templates
├── lambda_functions/          # Serverless functions
├── deployment/                # Deployment scripts
└── monitoring/                # CloudWatch integration
```

### Documentation
```
docs/                          # Technical documentation
├── DOCUMENTATION_HUB.md       # Central documentation index
├── SYSTEM_ARCHITECTURE.md     # Architecture overview
├── AVATAR_GAME_GUIDE.md       # Avatar game documentation
├── AWS_QUICKSTART.md          # AWS integration guide
└── [100+ documentation files]
```

### Configuration & Rules
```
.amazonq/rules/                # Amazon Q AI assistant rules
├── amazon_Q_Rules.md          # Core development principles
├── write.md                   # Code writing guidelines
└── memory-bank/               # Project memory bank (this file)

.continue/                     # Continue extension configuration
├── config.yaml                # Multi-model LLM configuration
├── rules/                     # Development rules
└── agents/                    # AI agent definitions

.github/
└── copilot-instructions.md    # GitHub Copilot integration guide
```

### Testing & Validation
```
tests/                         # Test suite
├── test_auto_analysis_integration.py
├── test_auto_patch_manager.py
└── test_idle_monitor.py

test_*.py                      # 50+ test files in root
verify_setup.bat               # 24-point system diagnostic
setup_requirements.bat         # Automated dependency installer
```

### Logs & Data
```
logs/                          # Centralized log storage
├── agent_core.log             # Main agent logs
├── brain.log                  # AI reasoning logs
├── voice.log                  # Voice system logs
├── ai_activities.log          # AI decision tracking
├── file_operations.log        # File modification logs
└── [50+ component-specific logs]

cache/                         # Temporary data storage
├── voice/                     # Voice cache
├── web_search/                # Search results cache
└── model_awareness_cache.json # Model validation cache

memory/
└── context.db                 # Long-term memory database

data/
└── ultron_data.db             # Application data
```

### Additional Components
```
assistant/                     # AI Assistant Web Application
├── ai-assistant/              # React TypeScript web app
└── main.py                    # Python backend integration

ultron_assistant/              # Standalone assistant variant
├── frontend/                  # Web frontend
├── app.py                     # Flask application
└── automation.py              # Automation features

Avatar/                        # 3D avatar assets
├── Unity_Ultron/              # Unity integration
└── [3D models and viewers]

Oracle_JDK-24/                 # Java Development Kit
pokedex-portfolio/             # Pokédex portfolio project
scout-demo-service/            # Scout demo service
```

## Architectural Patterns

### Modular Plugin System
- Tools dynamically discovered from `tools/` directory
- Standardized `match()` and `execute()` interface
- Auto-loading on startup via `agent_core.py`

### Event-Driven Communication
- Pub/sub pattern via `utils/event_system.py`
- Cross-component communication without tight coupling
- Real-time event propagation for GUI updates

### Multi-Service Architecture
- Independent services on dedicated ports
- FastAPI/Flask for REST APIs
- Socket.IO for real-time communication
- Unified single-port architecture option

### Layered Configuration
- JSON configuration file (`ultron_config.json`)
- Environment variable overrides for sensitive data
- Runtime configuration validation
- Hot-reload support for development

### Centralized Logging
- Component-specific log files in `logs/`
- Structured JSON format for analysis
- AI decision tracking with confidence scores
- File operation logging for audit trail

## Key Relationships

### Agent Core → Components
- Initializes config, memory, voice, vision, event system
- Loads and manages tool plugins
- Coordinates service lifecycle
- Handles command routing

### Brain → AI Models
- Interfaces with Ollama for local inference
- Supports multiple models (llava, qwen, deepseek)
- Implements streaming responses
- Manages model switching and validation

### Voice Manager → TTS/STT Engines
- Coordinates multiple voice engines
- Implements fallback chain
- Handles wake word detection
- Manages voice cache

### GUI → Backend Services
- WebSocket connections for real-time updates
- REST API calls for commands
- Event system integration for notifications
- Voice command routing

### Tools → External Services
- AWS SDK for cloud services
- Ollama API for AI inference
- Browser automation via Selenium/MCP
- Database connections via SQLite

## Port Allocation

| Port | Service | Purpose |
|------|---------|---------|
| 5000 | API Server | REST API endpoints |
| 5003 | ADB Backend | Android device control |
| 8000 | AI Chat Server | NVIDIA enhanced chat |
| 8001 | Mobile Interface | Mobile web interface |
| 8002 | Avatar Game | Interactive RPG game |
| 8080 | Web GUI | Primary Pokédex interface |
| 8081 | AutoGen Studio | Multi-agent orchestration |
| 5175 | Frontend UI | Modern frontend interface |
| 11434 | Ollama | Local AI model inference |
