# Contributing to IBTest

Thank you for your interest in contributing to IBTest! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ibtest.git
   cd ibtest
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install the package in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Making Changes

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. **Make your changes** following the coding standards below

3. **Write or update tests** for your changes

4. **Run the test suite** to ensure everything works:
   ```bash
   pytest
   ```

5. **Run code quality checks**:
   ```bash
   black src tests
   ruff check src tests
   mypy src
   ```

### Coding Standards

- **Code Style**: We use [Black](https://black.readthedocs.io/) for code formatting
- **Linting**: We use [Ruff](https://docs.astral.sh/ruff/) for linting
- **Type Hints**: We use [MyPy](https://mypy.readthedocs.io/) for type checking
- **Docstrings**: Use Google-style docstrings for all public functions and classes

### Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage (>90%)
- Use descriptive test names that explain what is being tested

Example test:
```python
def test_hello_world_returns_correct_message():
    """Test that hello_world returns the expected greeting message."""
    result = hello_world()
    assert result == "Hello from IBTest!"
```

### Documentation

- Update documentation for any new features or API changes
- Use clear, concise language
- Include code examples where appropriate
- Update the README.md if necessary

## Submitting Changes

### Pull Request Process

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with:
   - A clear, descriptive title
   - A detailed description of the changes
   - References to any related issues
   - Screenshots or examples if applicable

3. **Ensure all checks pass**:
   - All tests must pass
   - Code coverage should not decrease
   - All quality checks must pass

4. **Respond to feedback** from reviewers promptly

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Code coverage maintained or improved

## Checklist
- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated if necessary
- [ ] Changes generate no new warnings
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Error messages (if any)

### Feature Requests

When requesting features, please include:
- Clear description of the feature
- Use case or motivation
- Possible implementation approach (if you have ideas)

## Development Commands

### Useful Make Commands

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run all quality checks
make lint

# Format code
make format

# Build documentation
make docs

# Clean build artifacts
make clean
```

### Manual Commands

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src

# Build package
python -m build

# Install in development mode
pip install -e ".[dev]"
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `src/ibtest/__init__.py`
2. Update `CHANGELOG.md`
3. Create a new release on GitHub
4. The CI pipeline will automatically publish to PyPI

## Questions?

If you have questions about contributing, please:
- Check existing issues and discussions
- Create a new issue with the "question" label
- Reach out to the maintainers

Thank you for contributing to IBTest! 🎉

