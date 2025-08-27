# FlowerCare Python Library

A modern, comprehensive Python library for communicating with FlowerCare (Xiaomi MiFlora) Bluetooth plant sensors.

![FlowerCare](https://via.placeholder.com/600x200/4CAF50/FFFFFF?text=FlowerCare+Python+Library)

## 🌱 Overview

The FlowerCare Python Library provides a clean, async-first interface for interacting with FlowerCare Bluetooth Low Energy plant sensors. Whether you're building a home automation system, conducting plant research, or just want to monitor your garden, this library makes it simple to access real-time and historical sensor data.

## ✨ Key Features

### 📡 **Bluetooth Low Energy**
Full BLE support with automatic device discovery and connection management

### 📊 **Real-time Data** 
Read live sensor measurements: temperature, brightness, soil moisture, and conductivity

### 📜 **Historical Data**
Access stored measurements from the device's internal memory

### ⚡ **Async First**
Built with asyncio for high-performance, non-blocking operations

### 🛡️ **Robust Error Handling**
Comprehensive exception handling with meaningful error messages

### 🏷️ **Type Hints**
Full type annotation support for better IDE integration and code quality

## 📊 What You Can Monitor

| Sensor | Unit | Range | Description |
|--------|------|-------|-------------|
| **Temperature** | °C | -10 to 60°C | Ambient temperature |
| **Brightness** | lux | 0 to 120,000 lux | Light intensity |
| **Soil Moisture** | % | 0 to 100% | Soil water content |
| **Soil Conductivity** | µS/cm | 0 to 10,000 µS/cm | Soil fertility/nutrients |

## 🚀 Quick Example

```python
import asyncio
from flowercare import FlowerCareScanner

async def main():
    # Discover devices
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if devices:
        device = devices[0]
        
        # Read sensor data
        async with device:
            data = await device.read_sensor_data()
            print(f"🌡️  Temperature: {data.temperature}°C")
            print(f"☀️  Brightness: {data.brightness} lux")
            print(f"💧  Moisture: {data.moisture}%")
            print(f"🌿  Conductivity: {data.conductivity} µS/cm")

asyncio.run(main())
```

## 🎯 Use Cases

- **Smart Garden Monitoring**: Automate plant care based on sensor readings
- **Research & Agriculture**: Collect environmental data for plant studies
- **Home Automation**: Integrate with smart home systems
- **Data Logging**: Long-term monitoring and analysis
- **Plant Health Alerts**: Get notified when plants need attention

## 🔧 Requirements

- **Python**: 3.9 to 3.12 (3.11 recommended)
- **Platform**: Linux, macOS, or Windows with Bluetooth adapter
- **Dependencies**: `bleak` for Bluetooth Low Energy communication

## 📚 Documentation Structure

This documentation is organized to help you get started quickly and then dive deeper into advanced topics:

- **[Getting Started](getting-started/installation.md)**: Installation and basic setup
- **[User Guide](user-guide/device-discovery.md)**: Comprehensive usage instructions
- **[Examples](examples/basic-usage.md)**: Real-world code examples
- **[API Reference](api/device.md)**: Detailed class and method documentation
- **[Advanced Topics](advanced/protocol.md)**: Protocol details and optimization

## 🤝 Community & Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/your-username/pyflowercare/issues)
- **Discussions**: Join the conversation on [GitHub Discussions](https://github.com/your-username/pyflowercare/discussions)
- **Contributing**: See our [contribution guidelines](https://github.com/your-username/pyflowercare/blob/main/CONTRIBUTING.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/your-username/pyflowercare/blob/main/LICENSE) file for details.