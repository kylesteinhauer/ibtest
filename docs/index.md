# IBTest Documentation

Welcome to the IBTest documentation!

## Overview

IBTest is a Python package for testing and interacting with Interactive Brokers API.

## Installation

```bash
pip install ibtest
```

## Quick Start

```python
from ibtest import hello_world

# Basic usage
message = hello_world()
print(message)  # Output: Hello from IBTest!
```

## API Reference

### Functions

#### `hello_world()`

Returns a simple greeting message.

**Returns:**
- `str`: A greeting message

**Example:**
```python
from ibtest import hello_world

result = hello_world()
print(result)  # "Hello from IBTest!"
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/kylesteinhauer/ibtest.git
cd ibtest

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src tests
black src tests

# Run type checking
mypy src
```

## Contributing

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

