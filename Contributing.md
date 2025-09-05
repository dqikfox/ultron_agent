# Contributing to ULTRON Agent

Thank you for your interest in contributing to ULTRON Agent! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/ultron_agent.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Make** your changes and commit: `git commit -m 'Add amazing feature'`
5. **Push** to your fork: `git push origin feature/amazing-feature`
6. **Submit** a Pull Request

## 🛠 Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm (for web components)
- Git
- Docker (optional, for containerized development)

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/dqikfox/ultron_agent.git
cd ultron_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,gui,ml]"

# Install pre-commit hooks
pre-commit install

# Copy configuration templates
cp ultron_config.json.example ultron_config.json
cp .env.example .env
```

### Running the Development Environment

```bash
# Start the agent in development mode
python main.py --debug

# Run tests
pytest

# Start the web interface
python web_gui_server.py

# Run linting
ruff check .
black --check .
mypy .
```

## 📝 Coding Standards

### Python Code Style

We use the following tools to maintain code quality:

- **[Black](https://black.readthedocs.io/)**: Code formatting
- **[Ruff](https://ruff.rs/)**: Fast Python linter
- **[MyPy](https://mypy.readthedocs.io/)**: Static type checking
- **[isort](https://isort.readthedocs.io/)**: Import sorting

### Code Guidelines

1. **Type Hints**: Use comprehensive type annotations
```python
from typing import Dict, List, Optional, Union

def process_data(items: List[str], config: Dict[str, Any]) -> Optional[str]:
    """Process data with proper type hints."""
    pass
```

2. **Docstrings**: Use Google-style docstrings
```python
def my_function(param1: str, param2: int) -> bool:
    """Summary of the function.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When parameter validation fails.
    """
    pass
```

3. **Error Handling**: Implement robust exception handling
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

4. **Logging**: Use structured logging
```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("Processing file", extra={"filename": filename, "size": file_size})

# Avoid
print(f"Processing {filename}")
```

### JavaScript/TypeScript (Web Components)

- Use **ESLint** and **Prettier** for formatting
- Follow **TypeScript** best practices
- Use **modern ES6+** syntax
- Implement proper **error boundaries**

## 🧪 Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # pytest configuration
├── test_agent_core.py       # Core agent tests
├── test_brain.py            # AI reasoning tests
├── test_tools.py            # Tool system tests
├── test_voice_manager.py    # Voice processing tests
└── integration/
    ├── test_api.py          # API endpoint tests
    └── test_workflows.py    # End-to-end tests
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

from ultron_agent.agent_core import UltronAgent

class TestUltronAgent:
    """Test suite for UltronAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        return UltronAgent()
    
    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.status == "initialized"
        assert agent.config is not None
    
    @patch('ultron_agent.agent_core.external_api_call')
    def test_external_api_integration(self, mock_api, agent):
        """Test external API integration with mocking."""
        mock_api.return_value = {"result": "success"}
        
        result = agent.call_external_api("test")
        
        assert result["result"] == "success"
        mock_api.assert_called_once_with("test")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ultron_agent --cov-report=html

# Run specific test file
pytest tests/test_agent_core.py -v

# Run tests matching a pattern
pytest -k "test_voice" -v

# Run tests in parallel
pytest -n auto
```

## 🏗 Architecture Guidelines

### Project Structure

```
ultron_agent/
├── agent_core.py           # Main agent class
├── brain.py                # AI reasoning engine
├── config.py               # Configuration management
├── voice_manager.py        # Voice processing
├── tools/                  # Plugin system
│   ├── __init__.py
│   ├── base_tool.py        # Tool base class
│   └── web_search.py       # Example tool
├── utils/                  # Utilities
│   ├── event_system.py     # Event handling
│   ├── performance.py      # Performance monitoring
│   └── security.py         # Security utilities
├── gui/                    # GUI implementations
├── docs/                   # Documentation
└── tests/                  # Test suite
```

### Design Principles

1. **Modularity**: Each component should be loosely coupled
2. **Extensibility**: Easy to add new tools and features
3. **Testability**: All code should be unit testable
4. **Performance**: Async/await for I/O operations
5. **Security**: Validate all inputs, encrypt sensitive data
6. **Accessibility**: Design for users with disabilities

### Adding New Tools

1. Create a new file in `tools/` directory
2. Inherit from `BaseTool` class
3. Implement required methods: `match()`, `execute()`, `schema()`
4. Add comprehensive tests
5. Update documentation

Example:
```python
# tools/my_new_tool.py
from typing import Dict, Any
from .base_tool import BaseTool

class MyNewTool(BaseTool):
    """Description of what this tool does."""
    
    @staticmethod
    def match(user_input: str) -> bool:
        """Check if this tool should handle the input."""
        return "my command" in user_input.lower()
    
    @staticmethod
    def execute(**kwargs) -> Dict[str, Any]:
        """Execute the tool's main functionality."""
        return {"result": "success", "data": "processed"}
    
    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return JSON schema for API documentation."""
        return {
            "name": "my_new_tool",
            "description": "Description for API docs",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input parameter"}
                },
                "required": ["input"]
            }
        }
```

## 📋 Pull Request Process

### Before Submitting

1. **Test**: Ensure all tests pass (`pytest`)
2. **Lint**: Run code quality checks (`ruff check .`, `black --check .`, `mypy .`)
3. **Documentation**: Update relevant documentation
4. **Changelog**: Add entry to `Changelog.md` if applicable

### PR Guidelines

1. **Title**: Use descriptive title (e.g., "Add voice recognition for multiple languages")
2. **Description**: Provide clear description of changes
3. **Testing**: Describe how you tested the changes
4. **Breaking Changes**: Clearly mark any breaking changes
5. **Size**: Keep PRs focused and reasonably sized

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation has been updated
- [ ] Changes generate no new warnings
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment**: OS, Python version, ULTRON Agent version
2. **Steps to Reproduce**: Clear, step-by-step instructions
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Logs**: Relevant log output or error messages
6. **Screenshots**: If applicable

## 💡 Feature Requests

For new features:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Your idea for implementation
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Screenshots, examples, references

## 📚 Documentation

### Writing Documentation

- Use **Markdown** for all documentation
- Follow existing documentation structure
- Include code examples where appropriate
- Keep language clear and concise
- Test all code examples

### Documentation Types

- **API Documentation**: Auto-generated from docstrings
- **User Guides**: Step-by-step instructions
- **Developer Guides**: Technical implementation details
- **Tutorials**: Learning-oriented content

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Give constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code contributions and reviews

## 🏷 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 3.1.2)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Schedule

- **Patch releases**: As needed for critical bugs
- **Minor releases**: Monthly feature releases
- **Major releases**: Quarterly or for significant changes

## 🛡 Security

### Reporting Security Issues

For security vulnerabilities, please:

1. **DO NOT** create a public GitHub issue
2. Email security concerns to the maintainers
3. Provide detailed description of the vulnerability
4. Wait for acknowledgment before public disclosure

### Security Best Practices

- Never commit API keys or secrets
- Validate all user inputs
- Use secure communication protocols
- Implement proper authentication and authorization
- Keep dependencies up to date

## 📞 Getting Help

If you need help:

1. Check the [documentation](docs/)
2. Search existing [GitHub Issues](https://github.com/dqikfox/ultron_agent/issues)
3. Ask in [GitHub Discussions](https://github.com/dqikfox/ultron_agent/discussions)
4. Join our community chat (coming soon)

## 🙏 Recognition

Contributors are recognized in:

- `CREDITS.md` file
- GitHub contributors page
- Release notes for significant contributions

---

**Thank you for contributing to ULTRON Agent! Together, we're building something amazing.** 🚀