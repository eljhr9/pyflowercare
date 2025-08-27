# Installation

This guide will help you install the FlowerCare Python Library and set up your environment.

## Requirements

Before installing the library, ensure your system meets these requirements:

### Python Version
- **Python 3.9 to 3.12** is required
- Python 3.11 is recommended for the best experience

Check your Python version:
```bash
python --version
```

### Operating System Support

| OS | Support | Notes |
|---|---|---|
| **Linux** | ✅ Full | Recommended for production |
| **macOS** | ✅ Full | Intel and Apple Silicon |
| **Windows** | ✅ Full | Windows 10 v1709+ required |

### Bluetooth Requirements

- **Bluetooth 4.0+ adapter** (Bluetooth Low Energy support)
- **Adapter drivers** properly installed and working

!!! tip "Verify Bluetooth"
    Test your Bluetooth setup with the system's built-in Bluetooth scanner before proceeding.

## Installation Methods

### 1. Using pip (Recommended)

Install the latest stable release from PyPI:

```bash
pip install pyflowercare
```

For development dependencies:
```bash
pip install pyflowercare[dev]
```

### 2. Using Poetry

If you're using Poetry for dependency management:

```bash
poetry add pyflowercare
```

### 3. From Source

Install the latest development version:

```bash
# Clone the repository
git clone https://github.com/eljhr9/pyflowercare.git
cd pyflowercare

# Install with pip
pip install -e .

# Or with Poetry
poetry install
```

## Platform-Specific Setup

### Linux Setup

#### Prerequisites
Install Bluetooth development libraries:

=== "Ubuntu/Debian"
    ```bash
    sudo apt-get update
    sudo apt-get install bluetooth bluez libbluetooth-dev
    ```

=== "CentOS/RHEL/Fedora"
    ```bash
    sudo dnf install bluez bluez-libs bluez-libs-devel
    # or for older versions:
    # sudo yum install bluez bluez-libs bluez-libs-devel
    ```

=== "Arch Linux"
    ```bash
    sudo pacman -S bluez bluez-utils
    ```

#### Permissions
Grant Bluetooth access to your Python interpreter:

```bash
# Method 1: Using setcap (recommended)
sudo setcap cap_net_raw+eip $(eval readlink -f `which python`)

# Method 2: Run as root (not recommended for production)
sudo python your_script.py
```

#### Enable Bluetooth Service
```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

### macOS Setup

macOS includes Bluetooth support out of the box. No additional setup required.

!!! note "macOS Permissions"
    You may need to grant Bluetooth permissions to your terminal or IDE in System Preferences → Security & Privacy → Privacy → Bluetooth.

### Windows Setup

#### Prerequisites
- **Windows 10 version 1709** or later
- **Microsoft C++ Build Tools** (for compiling dependencies)

#### Install Build Tools
1. Download [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install with C++ build tools workload

#### Alternative: Conda
If you encounter build issues, use conda:
```bash
conda install -c conda-forge bleak
pip install pyflowercare --no-deps
```

## Verification

Verify your installation works correctly:

```python
import asyncio
from pyflowercare import FlowerCareScanner, setup_logging

async def test_installation():
    # Enable debug logging
    setup_logging("INFO")
    
    # Test scanner creation
    scanner = FlowerCareScanner()
    print("✅ FlowerCare library installed successfully!")
    
    # Test device discovery (optional - requires actual device)
    print("🔍 Scanning for devices...")
    devices = await scanner.scan_for_devices(timeout=5.0)
    print(f"📱 Found {len(devices)} device(s)")

# Run the test
asyncio.run(test_installation())
```

Expected output:
```
✅ FlowerCare library installed successfully!
🔍 Scanning for devices...
📱 Found 0 device(s)
```

## Common Installation Issues

### Issue: `bleak` installation fails

**Solution**: Install system dependencies first (see platform-specific sections above).

### Issue: Permission denied on Linux

**Solution**: Use `setcap` or run as root:
```bash
sudo setcap cap_net_raw+eip $(which python)
```

### Issue: Bluetooth adapter not found

**Symptoms**: 
```
bleak.exc.BleakError: Bluetooth adapter not found
```

**Solutions**:
1. Ensure Bluetooth is enabled in system settings
2. Install/update Bluetooth drivers
3. Try different Bluetooth adapter

### Issue: Python version too old

**Symptoms**:
```
ERROR: Package requires a different Python version
```

**Solution**: Upgrade Python:
```bash
# Using pyenv (recommended)
pyenv install 3.11
pyenv global 3.11

# Or use your package manager
sudo apt install python3.11  # Ubuntu
brew install python@3.11     # macOS
```

## Next Steps

Once installed, proceed to:

- **[Quick Start Guide](quick-start.md)**: Get up and running in minutes
- **[First Steps](first-steps.md)**: Learn the fundamentals
- **[Device Discovery](../user-guide/device-discovery.md)**: Find your FlowerCare devices

## Development Installation

If you plan to contribute to the library:

```bash
# Clone and install in development mode
git clone https://github.com/eljhr9/pyflowercare.git
cd pyflowercare

# Install with development dependencies
poetry install

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest
```

This sets up:
- Editable installation
- Development dependencies (pytest, black, mypy, etc.)
- Pre-commit hooks for code quality
- Test suite