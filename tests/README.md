# ULTRON Agent Tests

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_brain.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run verbose
pytest -v
```

## Test Structure

- `test_template.py` - Template for new tests
- `test_*.py` - Individual test modules
- `conftest.py` - Shared fixtures (in project root)

## Writing Tests

1. Copy `test_template.py` to `test_yourmodule.py`
2. Import module to test
3. Write test cases using pytest
4. Run tests to verify

## Coverage Goals

- Core modules: >80% coverage
- Tools: >60% coverage
- GUI: >40% coverage
