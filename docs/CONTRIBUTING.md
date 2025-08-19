# Contributing to File Difference Analyzer

Thank you for your interest in contributing to the File Difference Analyzer project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Questions and Discussions](#questions-and-discussions)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

- Use the GitHub issue tracker
- Include a clear and descriptive title
- Provide detailed steps to reproduce the bug
- Include system information (OS, Python version, etc.)
- Include error messages and stack traces
- Provide sample files if applicable

### Suggesting Enhancements

- Use the GitHub issue tracker with the "enhancement" label
- Describe the problem you're trying to solve
- Explain why this enhancement would be useful
- Provide examples of how it would work

### Pull Requests

- Fork the repository
- Create a feature branch
- Make your changes
- Add tests for new functionality
- Ensure all tests pass
- Update documentation if needed
- Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Installation

1. Fork and clone the repository:
```bash
git clone https://github.com/your-username/file-diff-analyzer.git
cd file-diff-analyzer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .[dev]
```

### Alternative Setup with Make

```bash
make install-dev
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 88 characters (Black default)
- Use type hints for all function parameters and return values
- Use docstrings for all public functions and classes
- Follow Google docstring style

### Code Formatting

We use Black for code formatting:

```bash
make format
# or
black src/ tests/
```

### Linting

We use flake8 and mypy for code quality:

```bash
make lint
# or
flake8 src/ tests/
mypy src/
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test files
pytest tests/test_analyzer.py

# Run specific test functions
pytest tests/test_analyzer.py::TestFileDiffAnalyzer::test_initialization
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Use fixtures for common test data
- Aim for high test coverage
- Test both success and failure cases

### Test Structure

```python
def test_function_name():
    """Test description"""
    # Arrange
    # Act
    # Assert
```

## Pull Request Process

### Before Submitting

1. Ensure all tests pass
2. Run linting checks
3. Update documentation if needed
4. Add changelog entry if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

### Review Process

1. Automated checks must pass
2. At least one maintainer must approve
3. All conversations must be resolved
4. Changes must be up to date with main branch

## Documentation

### Code Documentation

- Use Google-style docstrings
- Include type hints
- Document all public APIs
- Provide usage examples

### User Documentation

- Update README.md for user-facing changes
- Add examples for new features
- Update API reference if needed

## Release Process

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

### Creating a Release

1. Update version in `__init__.py`
2. Update changelog
3. Create git tag
4. Build and publish to PyPI

## Getting Help

### Questions and Discussions

- Use GitHub Discussions for questions
- Use GitHub Issues for bugs and features
- Join our community chat (if available)

### Communication Channels

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and general discussion
- GitHub Pull Requests: Code contributions

## Recognition

Contributors will be recognized in:

- GitHub contributors list
- Project README
- Release notes
- Documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to File Difference Analyzer! 🚀
