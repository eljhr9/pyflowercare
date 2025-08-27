# Quick Start

Get up and running with the FlowerCare Python Library in just a few minutes!

## Your First Program

Let's create a simple script to discover and read data from your FlowerCare sensor:

```python title="my_first_flowercare.py"
import asyncio
from flowercare import FlowerCareScanner, setup_logging

async def main():
    # Enable logging to see what's happening
    setup_logging("INFO")
    
    # Create a scanner
    scanner = FlowerCareScanner()
    
    print("🔍 Scanning for FlowerCare devices...")
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if not devices:
        print("❌ No FlowerCare devices found")
        print("💡 Make sure your device is nearby and not connected to another app")
        return
    
    print(f"✅ Found {len(devices)} device(s)!")
    
    # Connect to the first device
    device = devices[0]
    print(f"📱 Connecting to {device.name} ({device.mac_address})...")
    
    async with device:
        # Read device information
        info = await device.get_device_info()
        print(f"ℹ️  Device: {info.name}")
        print(f"🔋 Battery: {info.battery_level}%")
        print(f"💾 Firmware: {info.firmware_version}")
        
        # Read sensor data
        print("\n📊 Reading sensor data...")
        data = await device.read_sensor_data()
        
        print(f"🌡️  Temperature: {data.temperature}°C")
        print(f"☀️  Brightness: {data.brightness} lux")
        print(f"💧 Moisture: {data.moisture}%")
        print(f"🌿 Conductivity: {data.conductivity} µS/cm")
        
        # Make the LED blink for identification
        print("\n💡 Blinking device LED...")
        await device.blink_led()

if __name__ == "__main__":
    asyncio.run(main())
```

Run this script:
```bash
python my_first_flowercare.py
```

## Expected Output

```
🔍 Scanning for FlowerCare devices...
✅ Found 1 device(s)!
📱 Connecting to Flower care (C4:7C:8D:6A:8E:CA)...
ℹ️  Device: Flower care
🔋 Battery: 85%
💾 Firmware: 3.2.9
📊 Reading sensor data...
🌡️  Temperature: 22.5°C
☀️  Brightness: 12450 lux
💧 Moisture: 45%
🌿 Conductivity: 1250 µS/cm
💡 Blinking device LED...
```

## Step-by-Step Breakdown

Let's understand what each part does:

### 1. Import Required Modules

```python
import asyncio
from flowercare import FlowerCareScanner, setup_logging
```

- `asyncio`: Python's async/await framework
- `FlowerCareScanner`: Finds FlowerCare devices
- `setup_logging`: Configures debug output

### 2. Enable Logging

```python
setup_logging("INFO")
```

This shows you what the library is doing internally. Levels available:
- `"DEBUG"`: Very detailed output
- `"INFO"`: General information
- `"WARNING"`: Only warnings and errors
- `"ERROR"`: Only errors

### 3. Scan for Devices

```python
scanner = FlowerCareScanner()
devices = await scanner.scan_for_devices(timeout=10.0)
```

The scanner looks for FlowerCare devices advertising on Bluetooth. The timeout prevents waiting forever.

### 4. Connect to Device

```python
async with device:
    # All device operations here
```

The `async with` statement automatically connects and disconnects. This ensures proper cleanup even if errors occur.

### 5. Read Data

```python
info = await device.get_device_info()
data = await device.read_sensor_data()
```

Two main types of data:
- **Device info**: Name, battery, firmware version
- **Sensor data**: Temperature, brightness, moisture, conductivity

## Common Variations

### Multiple Devices

```python
# Connect to all found devices
for device in devices:
    async with device:
        data = await device.read_sensor_data()
        print(f"{device.name}: {data.temperature}°C, {data.moisture}%")
```

### Find Specific Device

```python
# Find device by MAC address
target_mac = "C4:7C:8D:6A:8E:CA"
device = await scanner.find_device_by_mac(target_mac)

if device:
    async with device:
        data = await device.read_sensor_data()
        print(f"Target device data: {data}")
```

### Error Handling

```python
from flowercare.exceptions import ConnectionError, DeviceError

try:
    async with device:
        data = await device.read_sensor_data()
        print(data)
except ConnectionError:
    print("Failed to connect to device")
except DeviceError as e:
    print(f"Device operation failed: {e}")
```

## What's Next?

Now that you have the basics working, explore these topics:

- **[First Steps](first-steps.md)**: Learn core concepts in detail
- **[Device Discovery](../user-guide/device-discovery.md)**: Advanced scanning techniques
- **[Reading Sensor Data](../user-guide/reading-data.md)**: All about sensor measurements
- **[Examples](../examples/basic-usage.md)**: More complete code examples

## Troubleshooting

### No Devices Found

1. **Check device is on**: The FlowerCare should show a green light when active
2. **Check proximity**: Device should be within 10 meters
3. **Close other apps**: Other Bluetooth apps might be connected
4. **Check battery**: Low battery affects Bluetooth range

### Connection Fails

1. **Restart Bluetooth**: Turn Bluetooth off/on in system settings
2. **Update drivers**: Ensure Bluetooth drivers are current
3. **Check permissions**: See [installation guide](installation.md) for platform-specific permissions

### Import Errors

```python
ImportError: No module named 'flowercare'
```

The library isn't installed. Run:
```bash
pip install pyflowercare
```

### Async Errors

```python
RuntimeError: asyncio.run() cannot be called from a running event loop
```

You're running inside Jupyter or another async context. Use:
```python
# In Jupyter notebooks
await main()

# Instead of:
# asyncio.run(main())
```