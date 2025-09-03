# Quality Assurance & Testing Guide

This guide outlines the automated testing and quality assurance enhancements implemented for the ULTRON Agent project.

## 🔧 Development Setup

### Quick Start
```bash
# Set up development environment
make dev-setup

# Or manually:
pip install -e ".[dev]"
pre-commit install
```

### Available Commands
```bash
make help           # Show all available commands
make quick-check    # Run linting, formatting, and unit tests
make check-all      # Run comprehensive quality checks
make ci-local       # Simulate CI pipeline locally
```

## 🧪 Testing Strategy

### Test Categories
- **Unit Tests** (`@pytest.mark.unit`): Fast, isolated tests
- **Integration Tests** (`@pytest.mark.integration`): Component interaction tests  
- **Performance Tests** (`@pytest.mark.performance`): Performance benchmarks
- **Security Tests** (`@pytest.mark.security`): Security-focused tests

### Running Tests
```bash
make test              # All tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-fast         # Parallel execution
make coverage          # With coverage report
```

### Test Configuration
- **pytest.ini**: Test discovery and execution settings
- **pyproject.toml**: Coverage configuration and test markers
- **tox.ini**: Multi-environment testing

## 🔍 Code Quality Tools

### Linting & Formatting
- **Ruff**: Fast Python linter with extensive rule set
- **Black**: Opinionated code formatter
- **isort**: Import statement organizer  
- **mypy**: Static type checking

```bash
make lint          # Check for issues
make lint-fix      # Auto-fix issues
make format        # Format code
make format-check  # Check formatting
make type-check    # Type checking
```

### Security Scanning
- **Bandit**: Security vulnerability scanner for Python
- **Safety**: Dependency vulnerability checker

```bash
make security         # Run security scans
make security-report  # Generate detailed reports
```

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow
The CI pipeline includes:

1. **Code Quality Checks**
   - Linting with ruff
   - Formatting checks with black
   - Import sorting with isort
   - Type checking with mypy

2. **Security Scanning**
   - Vulnerability scanning with bandit
   - Dependency checks with safety

3. **Multi-Platform Testing** 
   - Ubuntu, Windows, macOS
   - Python 3.10, 3.11, 3.12
   - Unit and integration tests

4. **Pre-commit Hooks**
   - Automated formatting and linting
   - Runs on every commit

5. **Build & Distribution**
   - Windows executable generation
   - Artifact creation and storage

### Coverage Reporting
- HTML reports in `htmlcov/`
- XML reports for CI integration
- Codecov integration for PR feedback

## 🔨 Pre-commit Hooks

Pre-commit hooks run automatically on each commit:

- **Code formatting** (black, isort)
- **Linting** (ruff with auto-fix)
- **Security checks** (bandit)
- **General checks** (trailing whitespace, large files, etc.)

```bash
make pre-commit        # Run on all files
make pre-commit-install # Set up hooks
```

## 📊 Quality Metrics & Reporting

### Coverage Goals
- **Unit Tests**: >80% coverage target
- **Integration Tests**: Key workflows covered
- **Critical Paths**: 100% coverage for security-sensitive code

### Quality Gates
- All linting checks must pass
- No security vulnerabilities above medium severity
- Type checking with minimal ignored errors
- All tests pass across supported platforms

### Reporting
- **Coverage Reports**: `htmlcov/index.html`
- **Security Reports**: `bandit-report.json`, `safety-report.json`
- **Test Results**: JUnit XML format for CI integration

## 🛠 Development Workflow

### Recommended Workflow
1. **Start Development**
   ```bash
   git checkout -b feature/your-feature
   make dev-setup
   ```

2. **During Development**
   ```bash
   make quick-check    # After each change
   make test-unit      # Run relevant tests
   ```

3. **Before Committing**
   ```bash
   make check-all      # Comprehensive checks
   make pre-commit     # Verify hooks work
   ```

4. **Before Push**
   ```bash
   make ci-local       # Simulate CI pipeline
   ```

### Troubleshooting

#### Common Issues
- **Import errors**: Check dependencies with `pip list`
- **Test failures**: Run with `-v` flag for detailed output
- **Linting errors**: Use `make lint-fix` to auto-resolve
- **Type errors**: Check with `make type-check`

#### Getting Help
- Check `make help` for available commands
- Review error output for specific guidance
- Test configuration in `pytest.ini` and `pyproject.toml`

## 📝 Configuration Files

- **`.pre-commit-config.yaml`**: Pre-commit hook configuration
- **`pyproject.toml`**: Tool configurations (ruff, black, pytest, etc.)
- **`tox.ini`**: Multi-environment testing configuration
- **`.github/workflows/ci.yml`**: CI/CD pipeline definition
- **`Makefile`**: Development workflow commands

## 🎯 Next Steps

1. **Increase Test Coverage**: Add more unit and integration tests
2. **Performance Testing**: Add automated performance benchmarks
3. **Documentation Testing**: Add docstring and example testing
4. **Advanced Security**: Implement additional security scanning tools
5. **Monitoring**: Add quality metrics dashboards

---

For questions or improvements to this guide, please open an issue or submit a PR.