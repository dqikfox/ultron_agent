# Makefile for ULTRON Agent development workflow

.PHONY: help install-dev clean lint format test test-unit test-integration security coverage pre-commit build check-all

help:  ## Show this help message
	@echo "ULTRON Agent Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install development dependencies
	pip install -e ".[dev]" 
	pre-commit install

clean:  ## Clean build artifacts and cache
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .ruff_cache/ .mypy_cache/ .tox/
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete

lint:  ## Run linting checks
	ruff check . --statistics
	
lint-fix:  ## Run linting and auto-fix issues  
	ruff check . --fix
	
format:  ## Format code with black and isort
	black .
	isort .

format-check:  ## Check code formatting without making changes
	black --check --diff .
	isort --check-only --diff .

type-check:  ## Run type checking with mypy
	mypy ultron_agent/ --ignore-missing-imports

test:  ## Run all tests
	pytest tests/ -v

test-unit:  ## Run unit tests only  
	pytest tests/ -v -m "unit or not (integration or performance or slow)" --tb=short

test-integration:  ## Run integration tests
	pytest tests/ -v -m "integration" --tb=long

test-fast:  ## Run fast tests in parallel
	pytest tests/ -v -n auto --tb=short --disable-warnings

security:  ## Run security scans
	bandit -r . --skip B101 --severity-level medium
	
security-report:  ## Generate detailed security reports
	bandit -r . -f json -o bandit-report.json --skip B101
	safety check --json --output safety-report.json

coverage:  ## Run tests with coverage report
	pytest tests/ --cov=ultron_agent --cov-report=html --cov-report=term-missing

coverage-open:  ## Open coverage report in browser
	python -c "import webbrowser; webbrowser.open('htmlcov/index.html')"

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-install:  ## Install pre-commit hooks
	pre-commit install

build:  ## Build distribution packages
	python -m build

tox:  ## Run tox testing across multiple Python versions
	tox

tox-lint:  ## Run linting via tox
	tox -e lint

tox-security:  ## Run security scans via tox  
	tox -e security

docs:  ## Build documentation (if available)
	@echo "Documentation build not configured yet"

check-all: clean lint format-check type-check security test coverage  ## Run all quality checks

ci-local: check-all  ## Run CI checks locally
	@echo "✅ All CI checks passed locally!"

# Development helpers
dev-setup: install-dev pre-commit-install  ## Set up development environment
	@echo "🎉 Development environment ready!"

quick-check: lint-fix format test-unit  ## Quick development check
	@echo "⚡ Quick checks completed!"

# Docker helpers (if needed)
docker-build:  ## Build Docker image
	@echo "Docker support not configured yet"

# Project status
status:  ## Show project status
	@echo "📊 ULTRON Agent Project Status"
	@echo "==============================="  
	@echo "Python version: $$(python --version)"
	@echo "Pip packages: $$(pip list | wc -l) installed"
	@echo "Git status:"
	@git status --porcelain | head -10
	@echo "Test files: $$(find tests/ -name 'test_*.py' | wc -l)"
	@echo "Source files: $$(find . -name '*.py' -not -path './venv/*' -not -path './.venv/*' | wc -l)"