# PyFlowerCare

A Python library for communicating with FlowerCare (Xiaomi MiFlora) Bluetooth plant sensors.

## Features

- **Device Discovery**: Scan and discover FlowerCare devices via Bluetooth Low Energy
- **Real-time Sensor Data**: Read temperature, brightness, soil moisture, and conductivity
- **Historical Data**: Access stored historical measurements from the device
- **Device Management**: Connect, disconnect, and manage multiple devices
- **Async Support**: Full asyncio support for non-blocking operations
- **Error Handling**: Comprehensive exception handling with meaningful error messages

## Installation

```bash
pip install pyflowercare
```

## Requirements

- Python 3.9+
- Bluetooth Low Energy support
- Linux/macOS/Windows with Bluetooth adapter

## Quick Start

### Basic Usage

```python
import asyncio
from flowercare import FlowerCareScanner

async def main():
    scanner = FlowerCareScanner()
    
    # Scan for devices
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if devices:
        device = devices[0]
        
        # Connect and read data
        async with device:
            sensor_data = await device.read_sensor_data()
            print(f"Temperature: {sensor_data.temperature}°C")
            print(f"Brightness: {sensor_data.brightness} lux")
            print(f"Moisture: {sensor_data.moisture}%")
            print(f"Conductivity: {sensor_data.conductivity} µS/cm")

asyncio.run(main())
```

### Device Information

```python
async with device:
    info = await device.get_device_info()
    print(f"Device: {info.name}")
    print(f"MAC: {info.mac_address}")
    print(f"Battery: {info.battery_level}%")
    print(f"Firmware: {info.firmware_version}")
```

### Historical Data

```python
async with device:
    history = await device.get_historical_data()
    
    for entry in history[-5:]:  # Last 5 entries
        print(f"{entry.timestamp}: {entry.sensor_data}")
```

### Continuous Monitoring

```python
import asyncio
from datetime import datetime
from flowercare import FlowerCareScanner

async def monitor_device(device):
    while True:
        try:
            async with device:
                while True:
                    data = await device.read_sensor_data()
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {data}")
                    await asyncio.sleep(60)  # Read every minute
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)  # Retry after 5 seconds

async def main():
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices()
    
    # Monitor all found devices
    tasks = [monitor_device(device) for device in devices]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## API Reference

### FlowerCareScanner

- `scan_for_devices(timeout=10.0)`: Scan for FlowerCare devices
- `find_device_by_mac(mac_address, timeout=10.0)`: Find specific device by MAC address
- `scan_continuously(callback, timeout=None)`: Continuous scanning with callback
- `scan_stream(timeout=None)`: Async generator for device discovery

### FlowerCareDevice

- `connect(timeout=10.0)`: Connect to device
- `disconnect()`: Disconnect from device
- `read_sensor_data()`: Read current sensor measurements
- `get_device_info()`: Get device information (name, MAC, battery, firmware)
- `get_historical_data()`: Get stored historical measurements
- `blink_led()`: Make device LED blink

### Data Models

#### SensorData
- `temperature`: Temperature in Celsius
- `brightness`: Light intensity in lux
- `moisture`: Soil moisture percentage
- `conductivity`: Soil conductivity in µS/cm
- `timestamp`: Measurement timestamp

#### DeviceInfo
- `name`: Device name
- `mac_address`: MAC address
- `firmware_version`: Firmware version
- `battery_level`: Battery level percentage

## Error Handling

The library provides specific exception types:

```python
from flowercare.exceptions import (
    FlowerCareError,      # Base exception
    ConnectionError,      # Connection failures
    DeviceError,         # Device operation errors
    DataParsingError,    # Data parsing errors
    TimeoutError         # Operation timeouts
)

try:
    async with device:
        data = await device.read_sensor_data()
except ConnectionError as e:
    print(f"Failed to connect: {e}")
except DeviceError as e:
    print(f"Device error: {e}")
```

## Logging

Enable logging to see detailed operation information:

```python
from flowercare.logging import setup_logging

setup_logging("DEBUG")  # Enable debug logging
```

## Examples

See the `examples/` directory for more comprehensive examples:

- `basic_usage.py`: Simple device connection and data reading
- `continuous_monitoring.py`: Continuous monitoring of multiple devices
- `historical_data.py`: Historical data retrieval and CSV export

## Troubleshooting

### Permission Issues (Linux)
```bash
sudo setcap cap_net_raw+eip $(eval readlink -f `which python`)
```

### Bluetooth Not Available
Ensure your system has Bluetooth Low Energy support and the adapter is enabled.

### Device Not Found
- Ensure the FlowerCare device is nearby and not connected to another app
- Try increasing the scan timeout
- Check that the device battery is not depleted

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.