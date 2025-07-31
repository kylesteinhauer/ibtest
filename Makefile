.PHONY: help install install-dev test test-cov lint format type-check clean build docs docs-serve

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term-missing

lint:  ## Run all linting and formatting checks
	ruff check src tests
	ruff format --check src tests
	mypy src
	black --check src tests

format:  ## Format code with black and ruff
	black src tests
	ruff format src tests
	ruff check --fix src tests

type-check:  ## Run type checking with mypy
	mypy src

clean:  ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

docs:  ## Build documentation
	mkdocs build

docs-serve:  ## Serve documentation locally
	mkdocs serve

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

setup-dev:  ## Set up development environment
	python -m venv venv
	@echo "Activate the virtual environment with:"
	@echo "  source venv/bin/activate  # On Linux/Mac"
	@echo "  venv\\Scripts\\activate     # On Windows"
	@echo "Then run: make install-dev"

