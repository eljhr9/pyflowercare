# FlowerCareDevice

The `FlowerCareDevice` class is the core interface for communicating with FlowerCare Bluetooth sensors. It handles all device operations including connecting, reading sensor data, and managing the device lifecycle.

::: pyflowercare.device.FlowerCareDevice

## Overview

The `FlowerCareDevice` class provides a high-level interface for FlowerCare plant sensors. Each instance represents a single physical device and manages its Bluetooth Low Energy connection.

```python
from pyflowercare import FlowerCareScanner

# Get a device instance
scanner = FlowerCareScanner()
devices = await scanner.scan_for_devices()
device = devices[0]  # FlowerCareDevice instance
```

## Key Features

- **Automatic connection management** with context manager support
- **Real-time sensor data** reading (temperature, brightness, moisture, conductivity)
- **Historical data access** to retrieve stored measurements
- **Device information** including battery level and firmware version
- **LED control** for device identification
- **Robust error handling** with meaningful exceptions

## Basic Usage Pattern

```python
async with device:
    # All device operations here
    data = await device.read_sensor_data()
    print(data)
# Automatically disconnects
```

## Properties

### `mac_address`
```python
@property
def mac_address(self) -> str
```
Returns the device's MAC address (Bluetooth identifier).

**Returns:** Device MAC address as a string (e.g., "C4:7C:8D:6A:8E:CA")

```python
print(f"Device MAC: {device.mac_address}")
# Output: Device MAC: C4:7C:8D:6A:8E:CA
```

### `name`
```python
@property
def name(self) -> str
```
Returns the device's advertised name.

**Returns:** Device name as a string (e.g., "Flower care")

```python
print(f"Device name: {device.name}")
# Output: Device name: Flower care
```

### `is_connected`
```python
@property
def is_connected(self) -> bool
```
Checks if the device is currently connected.

**Returns:** `True` if connected, `False` otherwise

```python
if device.is_connected:
    data = await device.read_sensor_data()
```

### `last_history_complete`
```python
@property
def last_history_complete(self) -> bool
```
Whether the most recent `get_historical_data()` call ran to completion.

`get_historical_data()` never raises on a mid-read connection drop — it
reconnects and resumes, and if it ultimately cannot finish it returns the
entries collected so far. Check this property afterwards to tell a complete
read from a partial one.

**Returns:** `True` if the last history read finished; `False` if it was
interrupted (or has not run yet on a fresh connection — it defaults to `True`
before the first call).

```python
async with device:
    history = await device.get_historical_data()
    if not device.last_history_complete:
        print(f"⚠️ Partial read: only {len(history)} entries retrieved")
```

## Connection Management

### `connect(timeout=10.0)`
```python
async def connect(self, timeout: float = 10.0) -> None
```
Establishes a Bluetooth connection to the device.

**Parameters:**
- `timeout` (float): Connection timeout in seconds (default: 10.0)

**Raises:**
- `ConnectionError`: If connection fails
- `TimeoutError`: If connection times out

```python
try:
    await device.connect(timeout=15.0)
    print("Connected successfully!")
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

### `disconnect()`
```python
async def disconnect(self) -> None
```
Closes the Bluetooth connection to the device.

**Raises:**
- No exceptions - always succeeds

```python
await device.disconnect()
print("Disconnected")
```

### Context Manager Support

The recommended way to use devices is with the `async with` statement:

```python
# Automatic connection and cleanup
async with device:
    # Connection established automatically
    data = await device.read_sensor_data()
    info = await device.get_device_info()
    # Connection closed automatically, even if exceptions occur
```

This pattern ensures:
- Automatic connection establishment
- Proper cleanup on exit
- Exception safety

## Data Reading Methods

### `read_sensor_data()`
```python
async def read_sensor_data(self) -> SensorData
```
Reads current sensor measurements from the device.

**Returns:** `SensorData` object containing current measurements

**Raises:**
- `ConnectionError`: If device is not connected
- `DeviceError`: If device operation fails
- `DataParsingError`: If sensor data is invalid

```python
async with device:
    data = await device.read_sensor_data()
    
    print(f"Temperature: {data.temperature}°C")
    print(f"Brightness: {data.brightness} lux")
    print(f"Moisture: {data.moisture}%")
    print(f"Conductivity: {data.conductivity} µS/cm")
    print(f"Timestamp: {data.timestamp}")
```

#### SensorData Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `temperature` | `float` | °C | Air temperature (may be negative) |
| `brightness` | `Optional[int]` | lux | Light intensity, or `None` if not measured |
| `moisture` | `int` | % | Soil moisture (0-100) |
| `conductivity` | `Optional[int]` | µS/cm | Soil conductivity/fertility, or `None` if not measured |
| `timestamp` | `datetime` | - | When measurement was taken |

### `get_device_info()`
```python
async def get_device_info(self) -> DeviceInfo
```
Retrieves device information including battery level and firmware version.

**Returns:** `DeviceInfo` object with device details

**Raises:**
- `ConnectionError`: If device is not connected
- `DeviceError`: If device operation fails

```python
async with device:
    info = await device.get_device_info()
    
    print(f"Name: {info.name}")
    print(f"MAC: {info.mac_address}")
    print(f"Battery: {info.battery_level}%")
    print(f"Firmware: {info.firmware_version}")
```

#### DeviceInfo Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Device name |
| `mac_address` | `str` | MAC address |
| `battery_level` | `int` or `None` | Battery percentage (0-100) |
| `firmware_version` | `str` or `None` | Firmware version string |

### `get_historical_data()`
```python
async def get_historical_data(self) -> List[HistoricalEntry]
```
Retrieves historical sensor data stored on the device.

The read is resilient: if the BLE link drops mid-retrieval, the library waits
briefly, reconnects, and resumes from the same entry (up to a few attempts)
without losing already-collected entries. If it still cannot finish, it returns
the entries gathered so far instead of raising. Check
[`last_history_complete`](#last_history_complete) to distinguish a full read
from a partial one.

**Returns:** List of `HistoricalEntry` objects, ordered by timestamp. May be a
partial list if the connection could not be recovered.

**Raises:**
- `ConnectionError`: Only if the device is not connected when the call starts.
  Drops *during* retrieval are handled internally and yield a partial result.

```python
async with device:
    history = await device.get_historical_data()

    print(f"Found {len(history)} historical entries")
    if not device.last_history_complete:
        print("⚠️ Read was interrupted — this is a partial result")

    # Show last 5 entries
    for entry in history[-5:]:
        print(f"{entry.timestamp}: {entry.sensor_data}")
```

#### HistoricalEntry Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `datetime` | When measurement was recorded |
| `sensor_data` | `SensorData` | The sensor measurements |

!!! note "Historical Data Limitations"
    - Device stores limited history (typically last 2-3 weeks)
    - Data is overwritten when memory is full
    - Reading history can take 30+ seconds for full data

## Device Control

### `blink_led()`
```python
async def blink_led(self) -> None
```
Makes the device's LED blink for identification purposes.

**Raises:**
- `ConnectionError`: If device is not connected
- `DeviceError`: If device operation fails

```python
async with device:
    print("Look for the blinking light!")
    await device.blink_led()
```

The LED will blink for several seconds, making it easy to identify the physical device.

## Error Handling

The `FlowerCareDevice` class raises specific exceptions for different error conditions:

```python
from pyflowercare.exceptions import (
    ConnectionError, 
    DeviceError, 
    DataParsingError, 
    TimeoutError
)

try:
    async with device:
        data = await device.read_sensor_data()
        
except ConnectionError:
    print("Could not connect to device")
    
except TimeoutError:
    print("Operation timed out")
    
except DeviceError as e:
    print(f"Device error: {e}")
    
except DataParsingError as e:
    print(f"Invalid data received: {e}")
```

### Exception Hierarchy

```
FlowerCareError (base)
├── ConnectionError
├── DeviceError  
├── DataParsingError
└── TimeoutError
```

## Usage Examples

### Basic Sensor Reading

```python
from pyflowercare import FlowerCareScanner

async def read_plant_data():
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices()
    
    if devices:
        device = devices[0]
        async with device:
            data = await device.read_sensor_data()
            return data
    return None
```

### Device Health Check

```python
async def device_health_check(device):
    """Check device connectivity and battery status"""
    
    try:
        async with device:
            info = await device.get_device_info()
            data = await device.read_sensor_data()
            
            health = {
                "connected": True,
                "battery": info.battery_level,
                "firmware": info.firmware_version,
                "last_reading": data.timestamp,
                "status": "healthy"
            }
            
            if info.battery_level < 20:
                health["status"] = "low_battery"
                
            return health
            
    except ConnectionError:
        return {"connected": False, "status": "unreachable"}
    except Exception as e:
        return {"connected": False, "status": f"error: {e}"}
```

### Historical Data Analysis

```python
async def analyze_plant_history(device):
    """Analyze historical trends"""
    
    async with device:
        history = await device.get_historical_data()
        
    if not history:
        return "No historical data available"
    
    # Calculate trends
    temperatures = [e.sensor_data.temperature for e in history]
    moistures = [e.sensor_data.moisture for e in history]
    
    return {
        "readings_count": len(history),
        "date_range": (history[0].timestamp, history[-1].timestamp),
        "avg_temperature": sum(temperatures) / len(temperatures),
        "avg_moisture": sum(moistures) / len(moistures),
        "min_moisture": min(moistures),
        "max_temperature": max(temperatures)
    }
```

### Multiple Operations

```python
async def full_device_report(device):
    """Get complete device information and data"""
    
    async with device:  # Single connection for all operations
        # Device information
        info = await device.get_device_info()
        
        # Current sensor data  
        current_data = await device.read_sensor_data()
        
        # Historical data (optional - can be slow)
        try:
            history = await device.get_historical_data()
            history_summary = f"{len(history)} entries"
        except:
            history_summary = "unavailable"
            
        # LED identification
        await device.blink_led()
        
        return {
            "device": info,
            "current": current_data,
            "history": history_summary,
            "led_blinked": True
        }
```

## Performance Considerations

### Connection Reuse
For multiple operations, keep the connection open:

```python
# Good: Single connection
async with device:
    info = await device.get_device_info()
    data = await device.read_sensor_data()
    await device.blink_led()

# Avoid: Multiple connections
await device.connect()
info = await device.get_device_info()
await device.disconnect()

await device.connect()  # Reconnecting is slow
data = await device.read_sensor_data()
await device.disconnect()
```

### Concurrent Operations
Read from multiple devices simultaneously:

```python
async def read_all_devices(devices):
    async def read_one(device):
        async with device:
            return await device.read_sensor_data()
    
    # All devices read concurrently
    results = await asyncio.gather(*[
        read_one(device) for device in devices
    ])
    return results
```

### Timeouts
Set appropriate timeouts for your use case:

```python
# Quick scan for responsive devices
await device.connect(timeout=5.0)

# Patient connection for distant devices  
await device.connect(timeout=30.0)
```

## Thread Safety

`FlowerCareDevice` is **not thread-safe**. Use within a single async context:

```python
# Good: Single async context
async def good_usage():
    async with device:
        data1 = await device.read_sensor_data()
        data2 = await device.read_sensor_data()

# Avoid: Multiple threads
# Don't use the same device instance across threads
```