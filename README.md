# IBTest

[![CI](https://github.com/kylesteinhauer/ibtest/actions/workflows/ci.yml/badge.svg)](https://github.com/kylesteinhauer/ibtest/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kylesteinhauer/ibtest/branch/main/graph/badge.svg)](https://codecov.io/gh/kylesteinhauer/ibtest)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for testing and interacting with Interactive Brokers API.

## Features

- 🚀 Modern Python package structure
- 🧪 Comprehensive testing with pytest
- 🔧 Code quality tools (black, ruff, mypy)
- 📚 Documentation with MkDocs
- 🔄 CI/CD with GitHub Actions
- 📦 Ready for PyPI distribution

## Installation

### From PyPI (when published)

```bash
pip install ibtest
```

### From Source

```bash
git clone https://github.com/kylesteinhauer/ibtest.git
cd ibtest
pip install -e .
```

## Quick Start

```python
from ibtest import hello_world

# Basic usage
message = hello_world()
print(message)  # Output: Hello from IBTest!
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/kylesteinhauer/ibtest.git
cd ibtest

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_main.py
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Type checking
mypy src

# Run all quality checks
make lint
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Project Structure

```
ibtest/
├── src/
│   └── ibtest/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── docs/
│   └── index.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── requirements-dev.txt
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
├── README.md
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- 📖 [Documentation](docs/index.md)
- 🐛 [Issue Tracker](https://github.com/kylesteinhauer/ibtest/issues)
- 💬 [Discussions](https://github.com/kylesteinhauer/ibtest/discussions)

