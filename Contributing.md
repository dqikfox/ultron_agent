# Contributing to ULTRON Agent 3.0

Welcome to ULTRON Agent! We're excited that you're interested in contributing to this advanced AI agent project. This document provides guidelines for contributing to help maintain code quality and foster a collaborative environment.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

## Getting Started

ULTRON Agent 3.0 is a modular AI agent with voice, vision, and GUI capabilities. Before contributing:

1. Read the [README.md](README.md) for project overview
2. Review the [Architecture Documentation](ARCHITECTURE_DESIGN.md)
3. Check existing [Issues](https://github.com/dqikfox/ultron_agent/issues) and [Pull Requests](https://github.com/dqikfox/ultron_agent/pulls)
4. Join our community discussions

### Key Components

- **agent_core.py**: Main integration hub
- **brain.py**: Core AI logic and planning
- **voice_manager.py**: Multi-engine voice system
- **gui/**: GUI components (migrating to Pokédex-based implementations)
- **tools/**: Plugin system for extensible functionality
- **utils/**: Event system, performance monitoring, task scheduling

## Development Environment Setup

### Prerequisites

- Python 3.10+
- Ollama (for model management)
- Node.js (for GUI components)
- Git

### Setup Steps

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/ultron_agent.git
   cd ultron_agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   # For development dependencies
   pip install -r requirements_enhanced.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run Initial Setup**
   ```bash
   # Run diagnostics
   ./run.bat  # Windows
   ./run.sh   # Linux/Mac
   ```

6. **Verify Installation**
   ```bash
   python main.py --test
   pytest tests/
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug Reports**: Report issues with detailed reproduction steps
- 🚀 **Feature Requests**: Suggest new features with clear use cases
- 💻 **Code Contributions**: Implement features, fix bugs, improve performance
- 📚 **Documentation**: Improve documentation, add examples, create tutorials
- 🎨 **GUI/UX**: Enhance user interface and experience
- 🧪 **Testing**: Add tests, improve test coverage
- 🔧 **Tools**: Create new tools for the plugin system

### Before Contributing

1. **Check existing work**: Search issues and PRs to avoid duplication
2. **Create an issue**: For new features or major changes, create an issue first
3. **Discuss approach**: Get feedback on your approach before implementation
4. **Keep changes focused**: One feature/fix per PR

### Creating Issues

Use our issue templates:
- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting new features
- **Documentation**: For documentation improvements
- **Question**: For general questions

## Development Workflow

### Branch Strategy

- **main**: Stable release branch (protected)
- **develop**: Development branch for integration
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches
- **hotfix/***: Emergency fixes

### Workflow Steps

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes following our standards**
   - Follow coding standards
   - Write tests
   - Update documentation

3. **Test thoroughly**
   ```bash
   # Run linting
   ruff check .
   black --check .
   
   # Run tests
   pytest tests/
   
   # Test specific components
   python main.py --test
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "type(scope): description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commits format:
```
type(scope): short description

Longer description if needed

- Bullet points for changes
- Reference issues with #123
```

**Types**: feat, fix, docs, style, refactor, test, chore, perf, ci

**Examples**:
- `feat(voice): add new wake word detection`
- `fix(gui): resolve accessibility keyboard navigation`
- `docs(api): update tool development guide`

## Coding Standards

### Python Standards

- **Formatter**: Black (line length: 88)
- **Linter**: Ruff (with flake8 compatibility)
- **Type Checking**: MyPy (strict mode recommended)
- **Import Sorting**: isort

### Code Style Guidelines

1. **File Structure**
   ```python
   """Module docstring."""
   
   import standard_library
   import third_party
   import local_modules
   
   # Constants
   CONSTANT_VALUE = "value"
   
   # Classes and functions
   ```

2. **Tool Development**
   ```python
   class YourTool:
       """Tool for specific functionality."""
       
       @staticmethod
       def match(command: str) -> bool:
           """Check if command matches this tool."""
           return "your_trigger" in command.lower()
       
       async def execute(self, command: str, context: Dict) -> str:
           """Execute the tool command."""
           # Implementation
           return "Result"
       
       @staticmethod
       def schema() -> Dict:
           """Return tool metadata."""
           return {
               "name": "YourTool",
               "description": "Tool description",
               "triggers": ["your_trigger"]
           }
   ```

3. **Error Handling**
   ```python
   try:
       result = await some_operation()
   except SpecificError as e:
       logger.error(f"Operation failed: {e}")
       return f"Error: {e}"
   except Exception as e:
       logger.exception("Unexpected error in operation")
       return "An unexpected error occurred"
   ```

4. **Logging**
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   
   # Use appropriate log levels
   logger.debug("Debug information")
   logger.info("General information")
   logger.warning("Warning message")
   logger.error("Error message")
   ```

### Frontend/GUI Standards

- **HTML**: Semantic HTML5, accessibility attributes
- **CSS**: CSS3 with responsive design, CSS variables for theming
- **JavaScript**: ES6+, modular code, proper error handling
- **Accessibility**: WCAG 2.1 AA compliance

## Testing Guidelines

### Test Types

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **GUI Tests**: Test user interface components

### Testing Structure

```
tests/
├── unit/
│   ├── test_agent_core.py
│   ├── test_brain.py
│   └── test_tools/
├── integration/
│   ├── test_voice_integration.py
│   └── test_gui_integration.py
└── e2e/
    └── test_complete_workflow.py
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

def test_tool_matching():
    """Test tool command matching."""
    tool = YourTool()
    assert tool.match("trigger command")
    assert not tool.match("unrelated command")

@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution."""
    tool = YourTool()
    result = await tool.execute("test command", {})
    assert "expected" in result
```

### Test Requirements

- **Coverage**: Aim for >80% code coverage
- **Mocking**: Mock external dependencies
- **Assertions**: Clear, specific assertions
- **Documentation**: Docstrings for test functions

## Documentation

### Documentation Types

1. **Code Documentation**: Docstrings, inline comments
2. **API Documentation**: Auto-generated from docstrings
3. **User Guides**: How-to guides and tutorials
4. **Architecture**: Design decisions and patterns

### Documentation Standards

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description with more details about the function's
    purpose and behavior.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When operation fails
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
```

### Updating Documentation

- Update docstrings when changing function signatures
- Update README.md for major changes
- Add examples for new features
- Update API documentation

## Community Guidelines

### Code of Conduct

All contributors must follow our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inclusive environment for everyone.

### Communication Channels

- **Issues**: Bug reports, feature requests
- **Discussions**: General questions, ideas
- **Pull Requests**: Code review and discussion
- **Discord**: Real-time community chat (if available)

### Getting Help

- Check the [FAQ](FAQ.md)
- Search existing issues
- Create a new issue with the "question" label
- Join community discussions

### Recognition

We appreciate all contributions! Contributors are recognized in:
- CREDITS.md file
- Release notes
- Community highlights
- GitHub contributor graphs

## Security

### Reporting Security Issues

Do not report security issues in public. Please:

1. Email security concerns to the maintainers
2. Use the GitHub Security Advisory feature
3. Follow responsible disclosure practices

See our [Security Policy](SECURITY.md) for details.

### Security Guidelines

- Never commit API keys or secrets
- Use environment variables for configuration
- Follow security best practices
- Keep dependencies updated

## Release Process

### Version Strategy

We use semantic versioning (semver):
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### Release Workflow

1. Create release branch
2. Update version numbers
3. Update CHANGELOG.md
4. Create pull request
5. Merge and tag release
6. Deploy and announce

## Questions?

If you have questions about contributing:

1. Check this document first
2. Search existing issues and discussions
3. Create a new issue with the "question" label
4. Reach out to maintainers

Thank you for contributing to ULTRON Agent! 🚀

---

**Happy Coding!** ✨