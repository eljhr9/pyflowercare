# Troubleshooting Guide

This comprehensive troubleshooting guide helps you diagnose and resolve common issues when using the FlowerCare Python Library.

## Quick Diagnostic Checklist

Before diving into specific issues, run this quick diagnostic:

```python
import asyncio
from pyflowercare import FlowerCareScanner, setup_logging

async def quick_diagnostic():
    print("🔍 FlowerCare Quick Diagnostic")
    print("=" * 40)
    
    # Test 1: Library import
    try:
        from pyflowercare import FlowerCareDevice, FlowerCareScanner
        print("✅ Library import successful")
    except ImportError as e:
        print(f"❌ Library import failed: {e}")
        return
    
    # Test 2: Bluetooth availability
    try:
        from bleak import BleakScanner
        test_scanner = BleakScanner()
        print("✅ Bluetooth stack available")
    except Exception as e:
        print(f"❌ Bluetooth issue: {e}")
        return
    
    # Test 3: Device discovery
    try:
        scanner = FlowerCareScanner()
        devices = await scanner.scan_for_devices(timeout=5.0)
        print(f"✅ Scan completed - found {len(devices)} device(s)")
        
        if devices:
            device = devices[0]
            print(f"   Device: {device.name} ({device.mac_address})")
            
            # Test 4: Connection
            try:
                async with device:
                    print("✅ Connection successful")
                    
                    # Test 5: Data reading
                    try:
                        data = await device.read_sensor_data()
                        print(f"✅ Data reading successful: {data.temperature}°C")
                    except Exception as e:
                        print(f"❌ Data reading failed: {e}")
                        
            except Exception as e:
                print(f"❌ Connection failed: {e}")
        else:
            print("ℹ️  No FlowerCare devices found")
            
    except Exception as e:
        print(f"❌ Scan failed: {e}")

# Run diagnostic
asyncio.run(quick_diagnostic())
```

## Installation Issues

### ImportError: No module named 'flowercare'

**Problem**: The library is not installed or not in Python path.

**Solutions**:

1. **Install the library**:
```bash
pip install pyflowercare
```

2. **Verify installation**:
```bash
pip list | grep growify
python -c "import flowercare; print('OK')"
```

3. **Check Python environment**:
```bash
which python
python --version
```

4. **Virtual environment issues**:
```bash
# Create new virtual environment
python -m venv flowercare_env
source flowercare_env/bin/activate  # Linux/Mac
# or
flowercare_env\Scripts\activate  # Windows

pip install pyflowercare
```

### ImportError: No module named 'bleak'

**Problem**: The Bluetooth Low Energy library is not installed.

**Solutions**:

1. **Install bleak dependency**:
```bash
pip install bleak
```

2. **Platform-specific issues**:

=== "Linux"
    ```bash
    # Install system dependencies
    sudo apt-get install bluetooth bluez libbluetooth-dev
    
    # Reinstall bleak
    pip uninstall bleak
    pip install bleak
    ```

=== "Windows"
    ```bash
    # Install Visual C++ build tools first
    # Then install bleak
    pip install --no-cache-dir bleak
    ```

=== "macOS"
    ```bash
    # Usually works out of the box
    pip install bleak
    
    # If issues, try:
    brew install python
    pip3 install bleak
    ```

## Bluetooth Issues

### No Bluetooth Adapter Found

**Error**: `BleakError: Bluetooth adapter not found`

**Diagnosis**:
```python
import asyncio
from bleak import BleakScanner

async def check_bluetooth():
    try:
        scanner = BleakScanner()
        adapters = await scanner.get_available_adapters()
        print(f"Available adapters: {adapters}")
        
        devices = await scanner.discover(timeout=2.0)
        print(f"Found {len(devices)} BLE devices")
    except Exception as e:
        print(f"Bluetooth error: {e}")

asyncio.run(check_bluetooth())
```

**Solutions**:

1. **Enable Bluetooth**:
   - Windows: Settings → Devices → Bluetooth & other devices
   - macOS: System Preferences → Bluetooth
   - Linux: `sudo systemctl enable bluetooth && sudo systemctl start bluetooth`

2. **Update drivers**:
   - Windows: Device Manager → Bluetooth → Update driver
   - Linux: `sudo apt-get update && sudo apt-get upgrade`

3. **Check hardware**:
   ```bash
   # Linux
   lsusb | grep -i bluetooth
   hciconfig
   
   # Windows
   # Device Manager → Bluetooth radios
   
   # macOS
   system_profiler SPBluetoothDataType
   ```

### Permission Denied (Linux)

**Error**: `PermissionError: [Errno 1] Operation not permitted`

**Solutions**:

1. **Grant capabilities (recommended)**:
```bash
sudo setcap cap_net_raw+eip $(eval readlink -f `which python`)
```

2. **Add user to bluetooth group**:
```bash
sudo usermod -a -G bluetooth $USER
# Log out and back in
```

3. **Run as root (not recommended)**:
```bash
sudo python your_script.py
```

4. **Verify permissions**:
```bash
getcap $(which python)
groups $USER
```

## Device Discovery Issues

### No Devices Found

**Problem**: Scanner returns empty list despite devices being nearby.

**Diagnostic Script**:
```python
import asyncio
from pyflowercare import FlowerCareScanner
from bleak import BleakScanner

async def debug_discovery():
    print("🔍 Device Discovery Debug")
    print("=" * 30)
    
    # Test general BLE discovery
    print("1. General BLE device scan...")
    general_scanner = BleakScanner()
    all_devices = await general_scanner.discover(timeout=10.0)
    print(f"   Found {len(all_devices)} total BLE devices")
    
    for device in all_devices:
        print(f"   - {device.name or 'Unknown'} ({device.address})")
        print(f"     Services: {device.metadata.get('uuids', [])}")
    
    print("\n2. FlowerCare specific scan...")
    flowercare_scanner = FlowerCareScanner()
    flowercare_devices = await flowercare_scanner.scan_for_devices(timeout=15.0)
    print(f"   Found {len(flowercare_devices)} FlowerCare devices")
    
    for device in flowercare_devices:
        print(f"   - {device.name} ({device.mac_address})")

asyncio.run(debug_discovery())
```

**Solutions**:

1. **Increase scan timeout**:
```python
devices = await scanner.scan_for_devices(timeout=30.0)
```

2. **Check device state**:
   - Ensure FlowerCare device is not connected to phone app
   - Check battery level (replace if < 10%)
   - Move device closer (< 5 meters)

3. **Multiple scan attempts**:
```python
async def robust_scan(attempts=3):
    scanner = FlowerCareScanner()
    all_devices = {}
    
    for i in range(attempts):
        print(f"Scan attempt {i+1}/{attempts}...")
        devices = await scanner.scan_for_devices(timeout=10.0)
        
        for device in devices:
            all_devices[device.mac_address] = device
        
        await asyncio.sleep(2)  # Brief pause
    
    return list(all_devices.values())

devices = await robust_scan()
```

4. **Check Bluetooth interference**:
   - Turn off WiFi temporarily
   - Move away from other Bluetooth devices
   - Try different time of day

### Intermittent Device Discovery

**Problem**: Devices appear and disappear between scans.

**Solutions**:

1. **Continuous monitoring**:
```python
async def monitor_device_presence():
    scanner = FlowerCareScanner()
    seen_devices = set()
    
    async for device in scanner.scan_stream(timeout=60.0):
        if device.mac_address not in seen_devices:
            print(f"New device: {device.name} ({device.mac_address})")
            seen_devices.add(device.mac_address)
        else:
            print(f"Seen again: {device.name}")

await monitor_device_presence()
```

2. **Device state tracking**:
```python
from datetime import datetime, timedelta

class DeviceTracker:
    def __init__(self):
        self.last_seen = {}
    
    def update_device(self, device):
        self.last_seen[device.mac_address] = {
            'device': device,
            'timestamp': datetime.now()
        }
    
    def get_missing_devices(self, timeout_minutes=5):
        cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
        missing = []
        
        for mac, info in self.last_seen.items():
            if info['timestamp'] < cutoff:
                missing.append(info['device'])
        
        return missing

tracker = DeviceTracker()
```

## Connection Issues

### Connection Timeout

**Error**: `TimeoutError: Connection timeout after 10s`

**Diagnostic**:
```python
async def test_connection_stability(device):
    success_count = 0
    total_attempts = 5
    
    for i in range(total_attempts):
        try:
            print(f"Connection attempt {i+1}/{total_attempts}...")
            await device.connect(timeout=15.0)
            await device.disconnect()
            success_count += 1
            print("✅ Success")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        await asyncio.sleep(1)
    
    print(f"Success rate: {success_count}/{total_attempts}")

# Test with your device
await test_connection_stability(device)
```

**Solutions**:

1. **Increase timeout**:
```python
await device.connect(timeout=30.0)
```

2. **Retry with backoff**:
```python
async def robust_connect(device, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            timeout = min(10.0 + (attempt * 5.0), 30.0)
            await device.connect(timeout=timeout)
            return True
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt
                print(f"Retry in {wait_time}s... ({e})")
                await asyncio.sleep(wait_time)
            else:
                print(f"All attempts failed: {e}")
                return False
```

3. **Check signal strength**:
   - Move closer to device
   - Remove obstacles between device and computer
   - Check for interference sources

### Device Already Connected

**Error**: `ConnectionError: Device already connected to another application`

**Solutions**:

1. **Close other applications**:
   - Close phone apps (Mi Home, FlowerCare app)
   - Check for other Python scripts using the device

2. **Force disconnect**:
```python
# On Linux/macOS
import subprocess
subprocess.run(["bluetoothctl", "disconnect", device.mac_address])
```

3. **Restart Bluetooth**:
```bash
# Linux
sudo systemctl restart bluetooth

# macOS
sudo killall bluetoothd

# Windows
# Disable/enable Bluetooth adapter in Device Manager
```

## Data Reading Issues

### Invalid Sensor Data

**Error**: `DataParsingError: Invalid data length: 8`

**Diagnostic**:
```python
async def debug_data_reading(device):
    async with device:
        try:
            # Try reading raw characteristics
            from pyflowercare.constants import CHARACTERISTIC_UUIDS, COMMANDS
            
            # Send command
            await device.client.write_gatt_char(
                CHARACTERISTIC_UUIDS["MODE_CHANGE"], 
                COMMANDS["REALTIME_DATA"]
            )
            
            await asyncio.sleep(0.5)
            
            # Read raw data
            raw_data = await device.client.read_gatt_char(
                CHARACTERISTIC_UUIDS["SENSOR_DATA"]
            )
            
            print(f"Raw data length: {len(raw_data)}")
            print(f"Raw data: {raw_data.hex()}")
            
            # Try parsing
            data = device._parse_sensor_data(raw_data)
            print(f"Parsed: {data}")
            
        except Exception as e:
            print(f"Debug failed: {e}")

await debug_data_reading(device)
```

**Solutions**:

1. **Firmware compatibility**:
```python
async def check_firmware_compatibility(device):
    async with device:
        info = await device.get_device_info()
        firmware = info.firmware_version
        
        print(f"Firmware: {firmware}")
        
        if firmware and firmware.startswith("2."):
            print("⚠️  Old firmware - may have compatibility issues")
        elif firmware and firmware.startswith("3."):
            print("✅ Modern firmware - should work well")
        else:
            print("❓ Unknown firmware version")
```

2. **Data validation**:
```python
async def validated_read(device, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with device:
                data = await device.read_sensor_data()
                
                # Validate ranges
                if not (-20 <= data.temperature <= 70):
                    raise ValueError(f"Temperature out of range: {data.temperature}")
                if not (0 <= data.moisture <= 100):
                    raise ValueError(f"Moisture out of range: {data.moisture}")
                if not (0 <= data.brightness <= 200000):
                    raise ValueError(f"Brightness out of range: {data.brightness}")
                
                return data
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
    
    return None
```

### Inconsistent Readings

**Problem**: Sensor values fluctuate wildly between readings.

**Solutions**:

1. **Multiple reading average**:
```python
async def stable_reading(device, samples=5, delay=1.0):
    readings = []
    
    async with device:
        for i in range(samples):
            data = await device.read_sensor_data()
            readings.append(data)
            if i < samples - 1:
                await asyncio.sleep(delay)
    
    # Calculate averages
    avg_temp = sum(r.temperature for r in readings) / len(readings)
    avg_moisture = sum(r.moisture for r in readings) / len(readings)
    avg_brightness = sum(r.brightness for r in readings) / len(readings)
    avg_conductivity = sum(r.conductivity for r in readings) / len(readings)
    
    return {
        'temperature': round(avg_temp, 1),
        'moisture': round(avg_moisture),
        'brightness': round(avg_brightness),
        'conductivity': round(avg_conductivity),
        'sample_count': len(readings)
    }
```

2. **Outlier filtering**:
```python
import statistics

async def filtered_reading(device, samples=5):
    readings = []
    
    async with device:
        for _ in range(samples):
            data = await device.read_sensor_data()
            readings.append(data)
            await asyncio.sleep(0.5)
    
    # Remove outliers using median absolute deviation
    def remove_outliers(values):
        median = statistics.median(values)
        mad = statistics.median([abs(x - median) for x in values])
        threshold = 2 * mad
        
        return [x for x in values if abs(x - median) <= threshold]
    
    temps = remove_outliers([r.temperature for r in readings])
    moistures = remove_outliers([r.moisture for r in readings])
    
    return {
        'temperature': statistics.mean(temps) if temps else None,
        'moisture': statistics.mean(moistures) if moistures else None,
        'samples_used': len(temps)
    }
```

## Performance Issues

### Slow Operations

**Problem**: Operations take much longer than expected.

**Diagnostic**:
```python
import time

async def performance_test(device):
    print("⏱️  Performance Test")
    print("=" * 20)
    
    # Test connection time
    start = time.time()
    await device.connect()
    connect_time = time.time() - start
    print(f"Connection time: {connect_time:.2f}s")
    
    # Test data reading time
    start = time.time()
    data = await device.read_sensor_data()
    read_time = time.time() - start
    print(f"Data reading time: {read_time:.2f}s")
    
    # Test disconnection time
    start = time.time()
    await device.disconnect()
    disconnect_time = time.time() - start
    print(f"Disconnection time: {disconnect_time:.2f}s")
    
    print(f"Total operation time: {connect_time + read_time + disconnect_time:.2f}s")

await performance_test(device)
```

**Solutions**:

1. **Connection reuse**:
```python
# Good: Single connection for multiple operations
async with device:
    data1 = await device.read_sensor_data()
    info = await device.get_device_info()
    await device.blink_led()

# Avoid: Multiple connections
await device.connect()
data1 = await device.read_sensor_data()
await device.disconnect()

await device.connect()  # Slow reconnection
info = await device.get_device_info()
await device.disconnect()
```

2. **Concurrent operations**:
```python
# Read multiple devices concurrently
async def read_all_devices(devices):
    async def read_one(device):
        async with device:
            return await device.read_sensor_data()
    
    results = await asyncio.gather(*[
        read_one(device) for device in devices
    ])
    return results
```

## Platform-Specific Issues

### Windows Issues

**Problem**: `OSError: [WinError 10054] An existing connection was forcibly closed`

**Solutions**:

1. **Update Windows**:
   - Ensure Windows 10 version 1709 or later
   - Install latest updates

2. **Bluetooth driver issues**:
   - Update Bluetooth drivers
   - Try different Bluetooth adapter

3. **Antivirus interference**:
   - Temporarily disable antivirus
   - Add Python to antivirus exclusions

### macOS Issues

**Problem**: `Authorization required for Bluetooth access`

**Solutions**:

1. **Grant permissions**:
   - System Preferences → Security & Privacy → Privacy → Bluetooth
   - Allow terminal/IDE access

2. **Reset Bluetooth module**:
```bash
sudo killall bluetoothd
```

### Linux Issues

**Problem**: `dbus.exceptions.DBusException: org.freedesktop.DBus.Error.NoReply`

**Solutions**:

1. **Restart D-Bus**:
```bash
sudo systemctl restart dbus
sudo systemctl restart bluetooth
```

2. **Check D-Bus permissions**:
```bash
# Add user to necessary groups
sudo usermod -a -G bluetooth,netdev $USER
```

3. **Systemd issues**:
```bash
# Check Bluetooth service status
systemctl status bluetooth

# Restart if needed
sudo systemctl restart bluetooth
```

## Getting Help

If you're still experiencing issues:

1. **Enable debug logging**:
```python
from pyflowercare.logging import setup_logging
setup_logging("DEBUG")
```

2. **Collect system information**:
```python
import platform
import sys
print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")
```

3. **Create minimal reproduction case**:
```python
import asyncio
from pyflowercare import FlowerCareScanner

async def minimal_repro():
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if devices:
        device = devices[0]
        async with device:
            data = await device.read_sensor_data()
            print(data)

asyncio.run(minimal_repro())
```

4. **Report issues**:
   - GitHub Issues: Include system info, error messages, and reproduction steps
   - Community forums: Provide context about your use case

Remember: Most issues are related to Bluetooth connectivity or permissions. Start with the quick diagnostic script at the top of this guide to identify the problem area.