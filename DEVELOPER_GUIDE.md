# 🤖 ULTRON Agent 3.0 - Developer Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.12 recommended)
- Git
- Optional: NVIDIA GPU for enhanced AI features

### Installation
```bash
# Clone the repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Install dependencies  
pip install -r requirements_consolidated.txt

# Optional: Install with extras
pip install -e .[nvidia,gui,dev]

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration
1. **API Keys**: Add your API keys to `.env`
   ```bash
   OPENAI_API_KEY=your_key_here
   NVIDIA_API_KEY=your_nvidia_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_key_here
   ```

2. **Voice Setup**: Configure voice settings
   ```bash
   VOICE_ENABLED=true
   VOICE_ENGINE=enhanced  # enhanced, pyttsx3, openai, console
   ```

3. **GUI Options**: Choose your interface
   ```bash
   GUI_THEME=ultron
   GUI_WIDTH=1200
   GUI_HEIGHT=800
   ```

## 🏗️ Architecture Overview

### Core Components

#### 1. **Agent Core** (`agent_core.py`)
- Main orchestration hub
- FastAPI + Socket.IO web server
- NVIDIA API integration
- Event system coordination

#### 2. **Brain** (`brain.py`)
- AI reasoning and decision-making
- Multi-model support (OpenAI, NVIDIA, local models)
- Context management and memory

#### 3. **Configuration** (`config_enhanced.py`)
- Secure environment-based configuration
- Pydantic validation
- Legacy compatibility

#### 4. **Voice System** (`voice_manager.py`)
- Multi-engine voice support
- Fallback chain: Enhanced → pyttsx3 → OpenAI → Console
- Real-time speech processing

#### 5. **GUI Systems**
- **Current**: `pokedex_ultron_gui.py` (Pokédx-based)
- **Legacy**: `gui_ultimate.py` (being phased out)
- **Web**: Web GUI server for browser-based interface

### 🛠️ Tool System

Tools are dynamically loaded from the `tools/` directory. Each tool must implement:

```python
class MyTool:
    @staticmethod
    def match(command: str) -> bool:
        """Return True if this tool should handle the command"""
        return "my_keyword" in command.lower()
    
    @staticmethod  
    def execute(command: str, **kwargs) -> str:
        """Execute the tool and return result"""
        return "Tool executed successfully"
    
    @staticmethod
    def schema() -> dict:
        """Return tool metadata"""
        return {
            "name": "my_tool",
            "description": "Description of what this tool does",
            "parameters": {...}
        }
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python test_runner_enhanced.py

# Run specific test categories
python test_runner_enhanced.py --security
python test_runner_enhanced.py --unit
python test_runner_enhanced.py --integration

# Using pytest directly
pytest test_security.py -v
pytest --cov=. --cov-report=html
```

### Test Categories
- **Security**: `test_security.py`, validation tests
- **Unit**: Core functionality tests  
- **Integration**: Component interaction tests
- **Performance**: Load and speed tests

## 🔧 Development Workflow

### 1. Setup Development Environment
```bash
# Install with development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run code quality checks
black .
ruff check .
mypy .
```

### 2. Making Changes
1. **Create Feature Branch**: `git checkout -b feature/my-feature`
2. **Make Changes**: Follow coding standards
3. **Run Tests**: Ensure all tests pass
4. **Commit**: Pre-commit hooks will run automatically
5. **Push & PR**: Create pull request

### 3. Code Quality Standards
- **Formatting**: Black (88 character line length)
- **Linting**: Ruff with security rules
- **Type Checking**: MyPy for static analysis
- **Security**: Bandit security scanning
- **Testing**: 80%+ test coverage goal

## 📦 Deployment

### Local Development
```bash
# Start the agent
python main.py

# Web GUI mode
python main.py --web

# CLI mode (no GUI)
python main.py --cli
```

### Production Deployment
```bash
# Using Docker (recommended)
docker build -t ultron-agent .
docker run -p 8080:8080 --env-file .env ultron-agent

# Direct deployment
uvicorn agent_core:app --host 0.0.0.0 --port 8080
```

## 🔒 Security

### Best Practices
1. **Never commit API keys** - Use environment variables
2. **Validate all inputs** - Use security utilities  
3. **Log security events** - Enable comprehensive logging
4. **Regular updates** - Keep dependencies updated

### Security Features
- Input sanitization for all user inputs
- XSS prevention in web components
- Path traversal protection
- API key validation
- Rate limiting on API endpoints

## 🎛️ Configuration Options

### Environment Variables
```bash
# API Configuration
OPENAI_API_KEY=your_key
NVIDIA_API_KEY=your_key
ELEVENLABS_API_KEY=your_key

# AI Settings
PRIMARY_MODEL=gpt-4
AI_TEMPERATURE=0.7
MAX_TOKENS=2048

# Voice Settings
VOICE_ENABLED=true
VOICE_ENGINE=enhanced
VOICE_RATE=200

# GUI Settings  
GUI_THEME=ultron
GUI_WIDTH=1200
GUI_HEIGHT=800

# Security Settings
REQUIRE_ADMIN_CONFIRMATION=true
LOG_ALL_COMMANDS=true
DANGEROUS_COMMANDS_ENABLED=false

# Logging
LOG_LEVEL=INFO
LOG_FILE_ENABLED=true
```

## 📚 Advanced Topics

### Adding New AI Models
1. Extend `AIConfig` in `config_enhanced.py`
2. Add model handling in `brain.py`
3. Update model selection logic
4. Add tests for new model

### Custom GUI Themes
1. Create theme in `gui/themes/`
2. Register in theme manager
3. Add CSS/styling rules
4. Update theme selection logic

### Plugin Development
1. Create plugin in `tools/` directory
2. Implement required interface
3. Add plugin metadata
4. Register with tool loader

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Check virtual environment and dependencies
2. **API Key Issues**: Verify keys in `.env` file
3. **Voice Not Working**: Check audio system and permissions
4. **GUI Crashes**: Check display settings and dependencies

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py --debug

# Check logs
tail -f logs/ultron.log
```

## 📈 Performance Optimization

### Best Practices
1. **Async/Await**: Use async patterns for I/O operations
2. **Connection Pooling**: Reuse HTTP connections
3. **Caching**: Cache expensive operations
4. **Memory Management**: Monitor memory usage

### Monitoring
- Health check endpoint: `http://localhost:8080/health`
- Metrics endpoint: `http://localhost:8080/metrics`  
- Performance logs in `logs/performance.log`

## 🤝 Contributing

### Getting Started
1. Fork the repository
2. Clone your fork
3. Install development dependencies
4. Make changes and test
5. Submit pull request

### Code Style
- Follow PEP 8 standards
- Use type hints where possible
- Document complex functions
- Write tests for new features

### Pull Request Process
1. Ensure tests pass
2. Update documentation
3. Add changelog entry
4. Request review

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dqikfox/ultron_agent/issues)
- **Documentation**: [Project Wiki](https://github.com/dqikfox/ultron_agent/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/dqikfox/ultron_agent/discussions)