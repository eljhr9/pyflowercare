# FlowerCareScanner

The `FlowerCareScanner` class handles discovery and identification of FlowerCare Bluetooth devices. It provides multiple scanning methods to fit different use cases, from one-time device discovery to continuous monitoring.

::: flowercare.scanner.FlowerCareScanner

## Overview

The scanner uses Bluetooth Low Energy (BLE) to discover FlowerCare devices by their advertising data. It can identify devices by their advertised name ("Flower care") or service UUID.

```python
from flowercare import FlowerCareScanner

# Create scanner instance
scanner = FlowerCareScanner()

# Basic usage
devices = await scanner.scan_for_devices(timeout=10.0)
```

## Device Identification

The scanner identifies FlowerCare devices using two methods:

1. **Device Name**: Advertised name contains "Flower care"
2. **Service UUID**: Device advertises the FlowerCare service UUID (`0000fe95-0000-1000-8000-00805f9b34fb`)

This dual approach ensures reliable detection even if the device name varies.

## Scanning Methods

### `scan_for_devices(timeout=10.0)`
```python
async def scan_for_devices(self, timeout: float = 10.0) -> List[FlowerCareDevice]
```
Performs a one-time scan for FlowerCare devices.

**Parameters:**
- `timeout` (float): Scan duration in seconds (default: 10.0)

**Returns:** List of `FlowerCareDevice` objects found during the scan

**Raises:**
- `TimeoutError`: If scan times out (rare - usually returns empty list)

```python
# Basic scan
scanner = FlowerCareScanner()
devices = await scanner.scan_for_devices(timeout=15.0)

print(f"Found {len(devices)} device(s)")
for device in devices:
    print(f"- {device.name} ({device.mac_address})")
```

#### Usage Examples

**Quick Discovery:**
```python
# Fast scan for nearby devices
devices = await scanner.scan_for_devices(timeout=5.0)
```

**Thorough Discovery:**
```python
# Longer scan for distant or hidden devices
devices = await scanner.scan_for_devices(timeout=30.0)
```

**Multiple Scans:**
```python
# Combine multiple scans for better coverage
all_devices = []

for _ in range(3):
    devices = await scanner.scan_for_devices(timeout=10.0)
    for device in devices:
        if device.mac_address not in [d.mac_address for d in all_devices]:
            all_devices.append(device)
    
    await asyncio.sleep(1)  # Brief pause between scans

print(f"Total unique devices: {len(all_devices)}")
```

### `find_device_by_mac(mac_address, timeout=10.0)`
```python
async def find_device_by_mac(self, mac_address: str, timeout: float = 10.0) -> Optional[FlowerCareDevice]
```
Searches for a specific device by its MAC address.

**Parameters:**
- `mac_address` (str): Target device MAC address (case-insensitive)
- `timeout` (float): Maximum scan time in seconds (default: 10.0)

**Returns:** `FlowerCareDevice` if found, `None` if not found

**Raises:**
- `TimeoutError`: If scan times out

```python
# Find specific device
target_mac = "C4:7C:8D:6A:8E:CA"
device = await scanner.find_device_by_mac(target_mac, timeout=15.0)

if device:
    print(f"Found target device: {device.name}")
    async with device:
        data = await device.read_sensor_data()
        print(data)
else:
    print("Device not found")
```

#### Use Cases

**Known Device Connection:**
```python
# Connect to previously discovered device
known_mac = "C4:7C:8D:6A:8E:CA"
device = await scanner.find_device_by_mac(known_mac)

if device:
    async with device:
        data = await device.read_sensor_data()
        print(f"Living room plant: {data.temperature}°C, {data.moisture}%")
```

**Device Verification:**
```python
# Verify device is still reachable
async def check_device_availability(mac_address):
    device = await scanner.find_device_by_mac(mac_address, timeout=5.0)
    return device is not None

is_available = await check_device_availability("C4:7C:8D:6A:8E:CA")
print(f"Device available: {is_available}")
```

### `scan_continuously(callback, timeout=None)`
```python
async def scan_continuously(self, 
                          callback: Callable[[FlowerCareDevice], None],
                          timeout: Optional[float] = None) -> None
```
Runs a continuous scan, calling the provided function for each discovered device.

**Parameters:**
- `callback`: Function called for each new device found
- `timeout` (Optional[float]): Scan duration in seconds, `None` for infinite

**Callback Signature:**
```python
def callback(device: FlowerCareDevice) -> None:
    # Handle discovered device
    pass
```

```python
def on_device_found(device):
    print(f"Discovered: {device.name} ({device.mac_address})")

# Scan for 60 seconds
await scanner.scan_continuously(on_device_found, timeout=60.0)

# Scan indefinitely (until cancelled)
await scanner.scan_continuously(on_device_found)
```

#### Real-World Examples

**Device Monitoring:**
```python
discovered_devices = set()

def track_device_discovery(device):
    if device.mac_address not in discovered_devices:
        discovered_devices.add(device.mac_address)
        print(f"New device found: {device.name}")
        
        # Could trigger device setup, notifications, etc.
        asyncio.create_task(setup_new_device(device))

async def setup_new_device(device):
    """Configure newly discovered device"""
    try:
        async with device:
            info = await device.get_device_info()
            print(f"Setup complete for {info.name} (Battery: {info.battery_level}%)")
    except Exception as e:
        print(f"Setup failed: {e}")

# Monitor for new devices
await scanner.scan_continuously(track_device_discovery, timeout=300)
```

**Network Presence Detection:**
```python
class DevicePresenceMonitor:
    def __init__(self):
        self.devices_seen = {}
        self.presence_callbacks = {}
    
    def on_device_discovered(self, device):
        mac = device.mac_address
        current_time = time.time()
        
        if mac not in self.devices_seen:
            print(f"Device {device.name} came online")
            if mac in self.presence_callbacks:
                self.presence_callbacks[mac]('online', device)
        
        self.devices_seen[mac] = current_time
    
    async def start_monitoring(self):
        await scanner.scan_continuously(self.on_device_discovered)

monitor = DevicePresenceMonitor()
await monitor.start_monitoring()
```

### `scan_stream(timeout=None)`
```python
async def scan_stream(self, timeout: Optional[float] = None) -> AsyncGenerator[FlowerCareDevice, None]
```
Returns an async generator that yields discovered devices as they're found.

**Parameters:**
- `timeout` (Optional[float]): Scan duration in seconds, `None` for infinite

**Yields:** `FlowerCareDevice` objects as they're discovered

```python
# Process devices as they're found
async for device in scanner.scan_stream(timeout=30.0):
    print(f"Found: {device.name}")
    
    # Process device immediately
    try:
        async with device:
            data = await device.read_sensor_data()
            print(f"  Current moisture: {data.moisture}%")
    except Exception as e:
        print(f"  Error reading data: {e}")
```

#### Advanced Usage

**Device Processing Pipeline:**
```python
async def process_device_stream():
    async for device in scanner.scan_stream(timeout=60.0):
        # Add to processing queue
        await device_queue.put(device)

async def device_processor():
    while True:
        device = await device_queue.get()
        
        try:
            async with device:
                data = await device.read_sensor_data()
                await save_to_database(device.mac_address, data)
        except Exception as e:
            print(f"Processing error: {e}")
        finally:
            device_queue.task_done()

# Run scanner and processor concurrently
await asyncio.gather(
    process_device_stream(),
    device_processor()
)
```

**Real-time Dashboard:**
```python
class RealTimeDashboard:
    def __init__(self):
        self.device_data = {}
    
    async def update_dashboard(self):
        async for device in scanner.scan_stream():
            try:
                async with device:
                    data = await device.read_sensor_data()
                    self.device_data[device.mac_address] = {
                        'name': device.name,
                        'data': data,
                        'last_seen': datetime.now()
                    }
                    await self.refresh_display()
            except Exception as e:
                print(f"Dashboard update error: {e}")
    
    async def refresh_display(self):
        # Update web interface, terminal display, etc.
        for mac, info in self.device_data.items():
            data = info['data']
            print(f"{info['name']}: {data.temperature}°C, {data.moisture}%")

dashboard = RealTimeDashboard()
await dashboard.update_dashboard()
```

## Configuration and Optimization

### Scanner Reuse

Create one scanner instance and reuse it:

```python
# Good: Reuse scanner
scanner = FlowerCareScanner()
devices1 = await scanner.scan_for_devices()
devices2 = await scanner.scan_for_devices()  # Reuses internal scanner

# Avoid: Multiple scanner instances
scanner1 = FlowerCareScanner()
scanner2 = FlowerCareScanner()  # Unnecessary overhead
```

### Timeout Selection

Choose timeouts based on your needs:

| Use Case | Recommended Timeout | Reason |
|----------|-------------------|---------|
| **Quick Check** | 3-5 seconds | Fast response, nearby devices only |
| **Standard Discovery** | 10-15 seconds | Good balance of speed and coverage |
| **Thorough Scan** | 30+ seconds | Maximum device discovery |
| **Background Monitoring** | None (infinite) | Continuous operation |

```python
# Quick availability check
devices = await scanner.scan_for_devices(timeout=3.0)

# Thorough initial discovery  
devices = await scanner.scan_for_devices(timeout=30.0)

# Production monitoring
await scanner.scan_continuously(handler, timeout=None)
```

### Performance Optimization

**Concurrent Scanning:**
```python
# Scan multiple areas simultaneously (if using multiple adapters)
async def multi_adapter_scan():
    scanner1 = FlowerCareScanner()  # Default adapter
    scanner2 = FlowerCareScanner()  # Could be different adapter
    
    results = await asyncio.gather(
        scanner1.scan_for_devices(timeout=10.0),
        scanner2.scan_for_devices(timeout=10.0)
    )
    
    all_devices = results[0] + results[1]
    # Remove duplicates based on MAC address
    unique_devices = {d.mac_address: d for d in all_devices}.values()
    return list(unique_devices)
```

**Adaptive Timeout:**
```python
async def adaptive_scan(target_count=5):
    """Scan until finding target number of devices or timeout"""
    scanner = FlowerCareScanner()
    found_devices = []
    timeout = 5.0
    
    while len(found_devices) < target_count and timeout <= 30.0:
        new_devices = await scanner.scan_for_devices(timeout=timeout)
        
        # Add new devices
        for device in new_devices:
            if device.mac_address not in [d.mac_address for d in found_devices]:
                found_devices.append(device)
        
        if len(found_devices) < target_count:
            timeout += 5.0  # Increase timeout for next attempt
            
    return found_devices
```

## Error Handling

Scanner methods are generally robust and rarely throw exceptions:

```python
try:
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if not devices:
        print("No devices found - check Bluetooth and device proximity")
    else:
        print(f"Found {len(devices)} device(s)")
        
except TimeoutError:
    print("Scan operation timed out")
except Exception as e:
    print(f"Unexpected error during scan: {e}")
```

## Troubleshooting

### No Devices Found

1. **Check Bluetooth Status:**
```python
# Verify basic scanning works
import bleak
scanner = bleak.BleakScanner()
all_devices = await scanner.discover(timeout=10.0)
print(f"All BLE devices found: {len(all_devices)}")
```

2. **Increase Scan Time:**
```python
# Try longer scan
devices = await scanner.scan_for_devices(timeout=30.0)
```

3. **Check Device State:**
   - Ensure FlowerCare device is not connected to another app
   - Verify device is powered on (battery not dead)
   - Check device is within range (< 10 meters)

### Inconsistent Discovery

```python
# Multiple scan attempts
async def robust_discovery(attempts=3):
    scanner = FlowerCareScanner()
    all_devices = {}
    
    for i in range(attempts):
        print(f"Scan attempt {i+1}/{attempts}")
        devices = await scanner.scan_for_devices(timeout=15.0)
        
        for device in devices:
            all_devices[device.mac_address] = device
            
        await asyncio.sleep(2)  # Brief pause between attempts
    
    return list(all_devices.values())

devices = await robust_discovery()
```

### Platform-Specific Issues

**Linux Permissions:**
```python
# Check if permission error occurs
try:
    devices = await scanner.scan_for_devices()
except PermissionError:
    print("Bluetooth permission denied")
    print("Run: sudo setcap cap_net_raw+eip $(which python)")
```

**Windows Adapter Issues:**
```python
# Verify Bluetooth adapter is available
try:
    from bleak import BleakScanner
    scanner = BleakScanner()
    await scanner.discover(timeout=1.0)  # Quick test
    print("Bluetooth adapter working")
except Exception as e:
    print(f"Bluetooth adapter issue: {e}")
```

## Integration Examples

### Home Assistant Integration

```python
async def home_assistant_discovery():
    """Discover devices for Home Assistant"""
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices(timeout=20.0)
    
    ha_devices = []
    for device in devices:
        try:
            async with device:
                info = await device.get_device_info()
                ha_devices.append({
                    'name': info.name,
                    'mac': device.mac_address,
                    'battery': info.battery_level,
                    'firmware': info.firmware_version
                })
        except Exception as e:
            print(f"Error reading {device.mac_address}: {e}")
    
    return ha_devices
```

### Plant Monitoring System

```python
class PlantMonitoringSystem:
    def __init__(self):
        self.scanner = FlowerCareScanner()
        self.known_plants = {}  # MAC -> plant info
    
    async def discover_new_plants(self):
        """Find and register new plant sensors"""
        devices = await self.scanner.scan_for_devices(timeout=15.0)
        
        new_plants = []
        for device in devices:
            if device.mac_address not in self.known_plants:
                try:
                    async with device:
                        info = await device.get_device_info()
                        plant_name = input(f"Name for new plant sensor {device.mac_address}: ")
                        
                        self.known_plants[device.mac_address] = {
                            'name': plant_name,
                            'device_info': info,
                            'added_date': datetime.now()
                        }
                        new_plants.append(plant_name)
                        
                except Exception as e:
                    print(f"Failed to setup {device.mac_address}: {e}")
        
        return new_plants
    
    async def monitor_all_plants(self):
        """Read data from all registered plants"""
        results = {}
        
        for mac, plant_info in self.known_plants.items():
            device = await self.scanner.find_device_by_mac(mac, timeout=10.0)
            
            if device:
                try:
                    async with device:
                        data = await device.read_sensor_data()
                        results[plant_info['name']] = data
                except Exception as e:
                    results[plant_info['name']] = f"Error: {e}"
            else:
                results[plant_info['name']] = "Device not found"
        
        return results

# Usage
system = PlantMonitoringSystem()
new_plants = await system.discover_new_plants()
print(f"Added {len(new_plants)} new plants")

plant_data = await system.monitor_all_plants()
for plant, data in plant_data.items():
    print(f"{plant}: {data}")
```