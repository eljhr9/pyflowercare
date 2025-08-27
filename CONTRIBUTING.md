# Contributing to FlowerCare Python Library

Thank you for your interest in contributing to the FlowerCare Python Library! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment**
4. **Make your changes**
5. **Run tests** and ensure they pass
6. **Submit a pull request**

## 🔧 Development Setup

### Prerequisites

- **Python 3.9+** (3.10 or 3.11 recommended)
- **Poetry** for dependency management
- **Git** for version control
- **FlowerCare device** for testing (optional but recommended)

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pyflowercare.git
cd pyflowercare

# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies (including development dependencies)
poetry install --with dev,docs

# Install pre-commit hooks
poetry run pre-commit install

# Verify installation
poetry run pytest --version
poetry run black --version
```

### Development Environment

The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality

## 📝 Making Changes

### Code Style

The project follows these coding standards:

1. **PEP 8** compliance (enforced by Black)
2. **Type hints** for all public functions
3. **Docstrings** in Google style
4. **Import sorting** with isort
5. **Line length**: 88 characters (Black default)

Example function:
```python
async def read_sensor_data(self, retries: int = 3) -> SensorData:
    """Read current sensor measurements from the device.
    
    Args:
        retries: Number of retry attempts on failure
        
    Returns:
        SensorData object containing current measurements
        
    Raises:
        ConnectionError: If device connection fails
        DeviceError: If device operation fails
        DataParsingError: If sensor data is invalid
    """
    # Implementation here
```

### Testing

Write tests for all new functionality:

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=flowercare

# Run specific test file
poetry run pytest tests/test_device.py

# Run tests matching pattern
poetry run pytest -k "test_connection"
```

### Type Checking

Ensure type hints are correct:

```bash
# Run mypy type checking
poetry run mypy flowercare/

# Check specific file
poetry run mypy flowercare/device.py
```

### Documentation

Update documentation for any public API changes:

```bash
# Build documentation locally
poetry run mkdocs serve

# Build static documentation
poetry run mkdocs build
```

## 🧪 Testing Guidelines

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── test_device.py          # Device class tests
├── test_scanner.py         # Scanner class tests  
├── test_models.py          # Data model tests
├── test_exceptions.py      # Exception handling tests
└── conftest.py            # Pytest configuration
```

### Writing Tests

1. **Use descriptive test names**:
```python
def test_device_connects_successfully_with_valid_mac():
    pass

def test_scanner_finds_devices_within_timeout():
    pass
```

2. **Test both success and failure cases**:
```python
@pytest.mark.asyncio
async def test_device_read_data_success():
    # Test successful data reading
    pass

@pytest.mark.asyncio  
async def test_device_read_data_connection_error():
    # Test connection failure handling
    pass
```

3. **Use fixtures for common setup**:
```python
@pytest.fixture
async def mock_device():
    """Create a mock FlowerCare device for testing."""
    device = Mock()
    device.mac_address = "AA:BB:CC:DD:EE:FF"
    device.name = "Test Device"
    return device
```

### Async Testing

Use `pytest-asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

### Mocking Bluetooth

For tests that don't require real hardware:

```python
from unittest.mock import Mock, AsyncMock, patch

@patch('flowercare.device.BleakClient')
async def test_device_without_hardware(mock_bleak):
    mock_client = AsyncMock()
    mock_bleak.return_value = mock_client
    
    # Test your code here
```

## 📦 Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
```bash
poetry run pytest
```

2. **Check code quality**:
```bash
poetry run black flowercare/ tests/
poetry run isort flowercare/ tests/
poetry run mypy flowercare/
```

3. **Update documentation** if needed
4. **Add your changes** to CHANGELOG.md

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Tested with real FlowerCare device (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated checks** must pass (GitHub Actions)
2. **Code review** by maintainers
3. **Testing** on different platforms if needed
4. **Merge** when approved

## 🐛 Bug Reports

When reporting bugs, include:

1. **Python version** and operating system
2. **Library version**
3. **Minimal code example** that reproduces the issue
4. **Full error traceback**
5. **Device information** (firmware version, battery level)

Example bug report:
```markdown
## Bug Description
Device connection fails intermittently

## Environment
- OS: Ubuntu 22.04
- Python: 3.11.2
- Library version: 0.1.0
- Device: FlowerCare (firmware 3.2.9)

## Code to Reproduce
```python
import asyncio
from flowercare import FlowerCareScanner

async def main():
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices()
    # Fails here sometimes
    
asyncio.run(main())
```

## Error Message
```
ConnectionError: Device not found after 10s timeout
```

## Additional Context
Happens about 30% of the time, device is 2 meters away.
```

## 💡 Feature Requests

For feature requests, describe:

1. **Use case** - why this feature is needed
2. **Proposed solution** - how you envision it working
3. **Alternatives considered** - other ways to solve the problem
4. **Implementation ideas** - if you have technical suggestions

## 🔄 Release Process

For maintainers:

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new version
3. **Create release tag**: `git tag v0.1.0`
4. **Push tag**: `git push origin v0.1.0`
5. **GitHub Actions** will automatically build and publish to PyPI

## 📋 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code:

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Focus on the issue**, not the person
- **Accept responsibility** and apologize for mistakes
- **Learn from feedback** and help others learn

## 🆘 Getting Help

If you need help contributing:

1. **Read the documentation** thoroughly
2. **Check existing issues** for similar questions
3. **Ask in GitHub Discussions** for general questions
4. **Create an issue** for specific problems

## 🏷️ Labels and Organization

We use these labels for issues and PRs:

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority-high**: Critical issues
- **platform-specific**: Platform-specific problems

## 🧑‍💻 Development Tips

### Local Testing with Real Devices

```python
# Create test configuration
TEST_DEVICE_MAC = "AA:BB:CC:DD:EE:FF"  # Your device MAC

async def test_with_real_device():
    scanner = FlowerCareScanner() 
    device = await scanner.find_device_by_mac(TEST_DEVICE_MAC)
    
    if device:
        async with device:
            data = await device.read_sensor_data()
            print(f"Test data: {data}")
    else:
        print("Test device not found")
```

### Debugging Bluetooth Issues

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use this for debugging
from flowercare.logging import setup_logging
setup_logging("DEBUG")
```

### Performance Testing

```python
import time

async def performance_test(device):
    start_time = time.time()
    
    async with device:
        data = await device.read_sensor_data()
    
    elapsed = time.time() - start_time
    print(f"Read took {elapsed:.2f} seconds")
```

## 📚 Resources

- **Python async/await**: https://docs.python.org/3/library/asyncio.html
- **Bluetooth Low Energy**: https://bleak.readthedocs.io/
- **Poetry documentation**: https://python-poetry.org/docs/
- **pytest documentation**: https://docs.pytest.org/
- **Type hints**: https://docs.python.org/3/library/typing.html

Thank you for contributing to the FlowerCare Python Library! 🌱