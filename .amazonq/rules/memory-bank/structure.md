# ULTRON Agent 3.0 - Project Structure

## Directory Organization

### Core Application Files (Root)
```
ultron_agent/
├── main.py                    # Application entry point
├── agent_core.py              # Main integration hub (FastAPI/Socket.IO)
├── brain.py                   # Core AI logic with Ollama integration
├── voice_manager.py           # Multi-engine voice system
├── voice.py                   # Voice processing implementation
├── vision.py                  # Vision and OCR processing
├── config.py                  # Configuration loader
├── memory.py                  # Memory management system
├── ultron_config.json         # Primary configuration file
└── requirements.txt           # Python dependencies
```

### Service Servers
```
├── web_gui_server.py          # Pokédex GUI server (port 8080)
├── avatar_game_server.py      # Avatar Game server (port 8002)
├── api_server.py              # REST API server (port 5000)
├── frontend_server.py         # Frontend UI server (port 5175)
├── nvidia_enhanced_ultron.py  # AI chat server (port 8000)
└── ssh_server.py              # SSH remote access (port 2222)
```

### Launcher & Automation
```
├── run.bat                    # Master launcher with health checks
├── start_avatar_game.bat      # Avatar Game launcher
├── launch_autonomous.bat      # Autonomous mode launcher
├── setup_requirements.bat     # Automated dependency installer
└── verify_setup.bat           # 24-point system diagnostic
```

### Configuration & Rules
```
.amazonq/
└── rules/
    ├── amazon_Q_Rules.md      # Amazon Q development guidelines
    ├── write.md               # Code writing standards
    └── memory-bank/           # Project memory documentation
        ├── product.md
        ├── structure.md
        ├── tech.md
        └── guidelines.md

.continue/
├── config.yaml                # Continue extension configuration
└── rules/                     # Continue AI rules and patterns
```

### Tools & Plugins
```
tools/
├── base.py                    # Tool base class
├── agent_network.py           # Multi-agent coordination
├── mobile_web_interface_tool.py
├── ocr_screenshot_analyzer.py
├── windows_system_tool.py
├── browser_mcp_tool.py
├── memory_context_tool.py
└── [15+ additional tools]
```

### Utilities
```
utils/
├── ultron_logger.py           # Centralized logging system
├── model_awareness.py         # AI model awareness checks
├── event_system.py            # Event communication
├── performance_monitor.py     # System monitoring
└── task_scheduler.py          # Background task management
```

### GUI Components
```
gui/
├── ultron_enhanced/
│   └── web/
│       ├── index.html         # PRIMARY GUI (Pokédex interface)
│       ├── ultron_avatar_game_ultimate.html
│       ├── app.js
│       ├── dnd_system.js      # RPG rules engine
│       └── styles.css
└── ultron_ultimate/
    └── main.py                # Legacy GUI (deprecated)
```

### Documentation
```
docs/
├── README.md                  # Main documentation
├── DOCUMENTATION_HUB.md       # Central documentation index
├── AVATAR_GAME_GUIDE.md       # Avatar Game documentation
├── MODEL_AVATARS_GUIDE.md     # AI personality system
├── AWS_QUICKSTART.md          # AWS integration guide
├── CONTINUE_INTEGRATION_COMPLETE.md
├── MCP_INTEGRATION_GUIDE.md
└── STARTUP_HEALTH_CHECKS.md
```

### Testing
```
tests/
├── conftest.py                # Test configuration
├── test_agent_features.py
├── test_voice_integration.py
├── test_avatar_game.py
├── test_ollama_integration.py
└── [50+ test files]
```

### Logs & Data
```
logs/
├── agent_core.log             # Component-specific logs
├── brain.log
├── voice.log
├── ai_activities.log          # AI decision tracking
├── file_changes.log           # File modification history
└── ultron_master_startup.log  # Startup diagnostics

memory/                        # Conversation memory storage
data/                          # Application data
cache/                         # Voice and model cache
models/                        # AI model storage
```

### Cloud Integration
```
aws_integration/
├── EnableAWSConfig.yml        # CloudFormation template
└── aws_solutions_integration.py

azure_automation/
├── azure_automation_setup.py
├── azure_automation_config.json
└── azure_template.json

aws_lambda/                    # Lambda function code
azure_functions/               # Azure function code
```

### Game & Interactive
```
dnd_game/                      # D&D game system
Avatar/                        # Avatar assets
game/                          # Game components
UnityGame/                     # Unity integration
unity_cloud_code/              # Unity cloud code
```

### Development Tools
```
scripts/                       # Utility scripts
diagnostics/                   # Diagnostic tools
automated_files/               # Auto-generated files
generated_scripts/             # Generated automation scripts
```

## Core Component Relationships

### Agent Core (agent_core.py)
**Central Hub** - Initializes and coordinates all components:
- Config → Memory → Voice → Vision → Event System
- Performance Monitor → Task Scheduler → Brain
- Tool Loading → Command Routing → System Events
- FastAPI/Socket.IO → Real-time Communication

### Brain (brain.py)
**AI Reasoning Engine**:
- Ollama Integration (llava:7b, qwen3-coder, deepseek-r1)
- NVIDIA API Integration (Claude, GPT, Mistral, Gemini)
- Planning → Acting → Project Analysis
- Streaming Responses → Async Chat → Fallback Mechanisms

### Voice System (voice_manager.py + voice.py)
**Multi-Engine Voice Processing**:
- ElevenLabs TTS/STT (primary)
- Fallback Chain: pyttsx3 → OpenAI TTS → Web Speech → Console
- Wake Word Detection → Intent Classification → Command Processing
- Context Awareness → Conversation Memory

### GUI System
**Primary Interface** (gui/ultron_enhanced/web/index.html):
- Real-time Voice Interaction
- Multi-Model AI Chat
- System Monitoring Dashboard
- File Processing & Web Search
- Productivity Suite (notes, tasks, reminders)

### Tool Ecosystem
**Dynamic Discovery**:
- Tools auto-discovered from `tools/` package
- Each tool implements: `match()`, `execute()`, `schema()`
- Standardized logging and error handling
- Plugin architecture for easy extension

### Event System (utils/event_system.py)
**Pub/Sub Communication**:
- Cross-component event broadcasting
- Async event handling
- Command lifecycle tracking
- System state synchronization

### Logging System (utils/ultron_logger.py)
**Centralized Logging**:
- Component-specific log files
- Structured JSON format
- AI decision tracking with confidence scores
- File operation logging
- Error history with context

### Model Awareness (utils/model_awareness.py)
**Safety System**:
- Pre-modification file checks
- Recent change tracking (7-day window)
- System stability monitoring
- Concurrent change detection
- Dependency relationship mapping

## Architectural Patterns

### Modular Design
- **Separation of Concerns**: Each service runs independently
- **Plugin Architecture**: Tools dynamically loaded at runtime
- **Event-Driven**: Components communicate via event system
- **Async/Await**: Non-blocking I/O for all network operations

### Configuration Management
- **Primary Config**: ultron_config.json (not config.py stub)
- **Environment Variables**: Override sensitive values (API keys)
- **Dynamic Loading**: Tools auto-discovered from tools/ package
- **Service Ports**: 8000 (AI Chat), 8080 (Web GUI), 5000 (API)

### Error Handling
- **Error Boundaries**: Comprehensive try/catch with logging
- **Circuit Breaker**: Automatic failure detection and recovery
- **Graceful Degradation**: Fallback mechanisms for all services
- **Resource Cleanup**: Proper shutdown handling

### Security Patterns
- **Input Sanitization**: All user inputs validated
- **API Key Management**: Environment variables for sensitive data
- **Error Logging**: Sanitized messages without sensitive data
- **Network Security**: Timeout and retry logic for external APIs

### Performance Optimization
- **Caching**: Response caching in brain.py for repeated queries
- **Async Operations**: Non-blocking I/O for all network calls
- **Memory Management**: Monitoring via performance utilities
- **Background Processing**: Task scheduler for long-running tasks

## Integration Points

### AI Services
- **Ollama**: Primary LLM backend (http://localhost:11434)
- **OpenAI**: Fallback API integration
- **ElevenLabs**: Voice synthesis and recognition
- **AWS Bedrock**: Cloud AI models (Claude, Llama)
- **NVIDIA NIM**: Multi-model API routing

### External Services
- **Ollama Server**: Must run locally on port 11434
- **ElevenLabs API**: Requires API key for voice features
- **AWS Services**: Bedrock, Lambda, S3, Polly, Secrets Manager
- **Azure Services**: Cognitive Services, Logic Apps, Functions

### Development Tools
- **VS Code**: Primary IDE with AI assistant integration
- **Amazon Q**: Deep ULTRON architecture awareness
- **GitHub Copilot**: Pattern-trained suggestions
- **Continue Extension**: Multi-model coordination
- **MCP Servers**: Browser automation, memory operations

## Data Flow

### Command Processing Flow
```
User Input (Voice/GUI/CLI/API)
    ↓
Agent Core (command routing)
    ↓
Brain (AI reasoning)
    ↓
Tool Selection & Execution
    ↓
Event System (broadcast results)
    ↓
Response Generation
    ↓
Output (Voice/GUI/API)
```

### Voice Command Flow
```
Microphone Input
    ↓
Wake Word Detection
    ↓
Speech-to-Text (ElevenLabs/Whisper)
    ↓
Intent Classification
    ↓
Context Resolution
    ↓
Command Execution
    ↓
Text-to-Speech Response
```

### AI Decision Flow
```
User Query
    ↓
Model Selection (Ensemble/Single)
    ↓
Context Retrieval (Memory)
    ↓
Model Inference (Ollama/API)
    ↓
Response Streaming
    ↓
Logging (AI Activities)
    ↓
User Feedback
```

## File Modification Guidelines

### Critical Files (Extra Caution Required)
- **agent_core.py**: Main integration hub - changes affect everything
- **brain.py**: Core AI logic - changes affect all reasoning
- **config.py**: Configuration system - breaking changes affect startup
- **voice_manager.py**: Voice system - changes affect accessibility
- **gui/ultron_enhanced/web/index.html**: Primary GUI - user experience impact

### Before Modifying Any File
1. Check Model Awareness: `should_modify_file(file_path, "edit", "amazon_q")`
2. Log Decision: `log_ai_decision("amazon_q", f"Modifying {file_path}")`
3. Review Recent Changes: Check `logs/file_changes.log`
4. Consider Dependencies: Review related files and integration points
5. Test Integration: Verify changes work with existing systems

### Safe Modification Areas
- **tools/**: New tool plugins (follow base.py pattern)
- **utils/**: Utility functions (maintain interfaces)
- **docs/**: Documentation updates
- **tests/**: Test additions and updates
- **scripts/**: Automation scripts

## Deployment Structure

### Production Files
- **run.bat**: Master launcher with health checks
- **ultron_config.json**: Production configuration
- **requirements.txt**: Dependency specification
- **logs/**: Runtime logs and diagnostics

### Development Files
- **.vscode/**: VS Code workspace settings
- **tests/**: Test suite
- **diagnostics/**: Diagnostic tools
- **.continue/**: Continue extension config

### Cloud Deployment
- **aws_integration/**: AWS CloudFormation templates
- **azure_automation/**: Azure deployment scripts
- **docker-compose.yml**: Container orchestration
- **Dockerfile**: Container image definition
