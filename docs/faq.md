# Frequently Asked Questions

Common questions and answers about the FlowerCare Python Library.

## General Questions

### What is FlowerCare?

FlowerCare (also known as Xiaomi MiFlora) is a Bluetooth Low Energy plant sensor that measures:
- **Temperature** - Air temperature around the plant
- **Brightness** - Light intensity in lux
- **Soil Moisture** - Water content in soil (0-100%)
- **Soil Conductivity** - Nutrient levels in µS/cm

The device stores data internally and can be accessed via Bluetooth using this Python library.

### Which devices are supported?

The library supports FlowerCare devices that advertise with:
- **Name**: Contains "Flower care" 
- **Service UUID**: `0000fe95-0000-1000-8000-00805f9b34fb`

This includes:
- Original FlowerCare sensors
- FlowerCare Max (with built-in battery)
- Most Xiaomi MiFlora variants

### What Python versions are supported?

- **Required**: Python 3.9 to 3.12
- **Recommended**: Python 3.11
- **Tested**: Python 3.9, 3.10, 3.11, 3.12

### What operating systems work?

| OS | Support | Notes |
|---|---|---|
| **Linux** | ✅ Full | Best performance, most tested |
| **macOS** | ✅ Full | Intel and Apple Silicon |
| **Windows** | ✅ Full | Windows 10 v1709+ required |

## Installation & Setup

### How do I install the library?

```bash
pip install pyflowercare
```

For development:
```bash
pip install pyflowercare[dev]
```

### Do I need special permissions?

**Linux**: Yes, grant Bluetooth capabilities:
```bash
sudo setcap cap_net_raw+eip $(which python)
```

**macOS**: Grant Bluetooth permission in System Preferences → Security & Privacy → Privacy → Bluetooth

**Windows**: No special setup required

### Can I use this in virtual environments?

Yes, virtual environments are fully supported and recommended:

```bash
# Create virtual environment
python -m venv flowercare_env
source flowercare_env/bin/activate  # Linux/Mac
# or
flowercare_env\Scripts\activate     # Windows

# Install library
pip install pyflowercare
```

## Device Discovery & Connection

### Why can't I find my device?

Common causes and solutions:

1. **Device connected to phone app**
   - Close Mi Home app or FlowerCare app
   - Disconnect device in phone's Bluetooth settings

2. **Device too far away**
   - Move within 10 meters of device
   - Remove obstacles between computer and device

3. **Low battery**
   - Replace CR2032 battery if device is old
   - Check battery level: `await device.get_device_info()`

4. **Bluetooth interference**
   - Turn off WiFi temporarily
   - Move away from other Bluetooth devices

### How do I find a specific device?

**By MAC address** (if known):
```python
device = await scanner.find_device_by_mac("C4:7C:8D:6A:8E:CA")
```

**By name pattern**:
```python
devices = await scanner.scan_for_devices()
my_device = next((d for d in devices if "Living Room" in d.name), None)
```

**Interactive selection**:
```python
devices = await scanner.scan_for_devices()

if devices:
    print("Available devices:")
    for i, device in enumerate(devices):
        print(f"{i+1}. {device.name} ({device.mac_address})")
    
    choice = int(input("Select device: ")) - 1
    selected_device = devices[choice]
```

### How long should I scan for devices?

- **Quick check**: 3-5 seconds
- **Normal discovery**: 10-15 seconds
- **Thorough scan**: 30+ seconds
- **Continuous monitoring**: No timeout (until stopped)

### Can I connect to multiple devices?

Yes, but not simultaneously to the same device:

```python
# Good: Sequential connections
for device in devices:
    async with device:
        data = await device.read_sensor_data()
        print(f"{device.name}: {data}")

# Good: Concurrent connections to different devices
async def read_device(device):
    async with device:
        return await device.read_sensor_data()

results = await asyncio.gather(*[
    read_device(device) for device in devices
])
```

## Data Reading

### How accurate are the sensors?

Typical accuracy:
- **Temperature**: ±1°C
- **Brightness**: ±15%
- **Moisture**: ±5%
- **Conductivity**: ±10%

Accuracy can be affected by:
- Sensor calibration
- Environmental conditions  
- Battery level
- Device age

### What do the sensor values mean?

#### Temperature (°C)
- **15-18°C**: Cool, growth may slow
- **18-24°C**: Optimal for most plants
- **24-28°C**: Warm, monitor for stress
- **>28°C**: Too hot, may need shade

#### Brightness (lux)
- **<500**: Very low light
- **500-2000**: Low light plants
- **2000-10000**: Moderate indoor light
- **10000-50000**: Bright light, good for most plants
- **>50000**: Very bright, may need shade

#### Moisture (%)
- **0-20%**: Dry, needs water
- **20-40%**: Slightly dry
- **40-70%**: Good moisture level
- **70-90%**: Moist, reduce watering
- **90-100%**: Waterlogged

#### Conductivity (µS/cm)
- **0-200**: Low nutrients, fertilize
- **200-500**: Fair fertility
- **500-2000**: Good nutrient levels
- **2000-5000**: High fertility
- **>5000**: Excessive, may damage roots

### How often should I read sensor data?

Depends on your use case:

- **Manual monitoring**: Once per day
- **Automated systems**: Every 15-30 minutes
- **Research/logging**: Every 5-10 minutes
- **Real-time alerts**: Every 1-5 minutes

**Note**: Frequent readings drain device battery faster.

### Can I read historical data?

Yes, devices store approximately 2-3 weeks of data:

```python
async with device:
    history = await device.get_historical_data()
    print(f"Found {len(history)} historical entries")
    
    for entry in history[-5:]:  # Last 5 entries
        print(f"{entry.timestamp}: {entry.sensor_data}")
```

**Limitations**:
- Limited storage (device overwrites old data)
- Reading full history takes 30+ seconds
- Not all devices support historical data

## Error Handling

### What should I do when operations fail?

**Connection errors**:
```python
try:
    async with device:
        data = await device.read_sensor_data()
except ConnectionError:
    print("Device unreachable - check proximity and battery")
except TimeoutError:
    print("Operation timed out - try again")
```

**Data parsing errors**:
```python
try:
    data = await device.read_sensor_data()
except DataParsingError:
    print("Invalid data received - device may need reset")
```

**Comprehensive error handling**:
```python
from flowercare.exceptions import FlowerCareError

try:
    async with device:
        data = await device.read_sensor_data()
except FlowerCareError as e:
    print(f"FlowerCare operation failed: {e}")
```

### Why do connections sometimes fail?

Common causes:

1. **Device busy**: Already connected to another app
2. **Low battery**: Replace CR2032 battery
3. **Distance**: Move closer to device
4. **Interference**: Other Bluetooth devices nearby
5. **System issues**: Restart Bluetooth service

### Should I implement retry logic?

Yes, for production applications:

```python
async def robust_read(device, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with device:
                return await device.read_sensor_data()
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise e
```

## Performance & Optimization

### How can I make operations faster?

1. **Reuse connections**:
```python
# Good: Single connection for multiple operations
async with device:
    info = await device.get_device_info()
    data = await device.read_sensor_data()
    await device.blink_led()
```

2. **Concurrent device reads**:
```python
# Read multiple devices simultaneously
results = await asyncio.gather(*[
    device.read_sensor_data() for device in devices
])
```

3. **Appropriate timeouts**:
```python
# Quick scan for nearby devices
devices = await scanner.scan_for_devices(timeout=5.0)
```

### How much battery does frequent reading use?

Approximate battery usage:
- **Reading every hour**: 6+ months
- **Reading every 15 minutes**: 3-4 months  
- **Reading every 5 minutes**: 1-2 months
- **Continuous reading**: Days to weeks

Battery life also depends on:
- Device age and battery quality
- Bluetooth connection strength
- Temperature (cold reduces battery life)

### Can I cache sensor data?

Yes, implement caching for efficiency:

```python
from datetime import datetime, timedelta

class CachedReader:
    def __init__(self, cache_duration_minutes=5):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    async def get_data(self, device):
        mac = device.mac_address
        now = datetime.now()
        
        # Check cache
        if mac in self.cache:
            cached_time, cached_data = self.cache[mac]
            if now - cached_time < self.cache_duration:
                return cached_data
        
        # Read fresh data
        async with device:
            data = await device.read_sensor_data()
            self.cache[mac] = (now, data)
            return data
```

## Integration & Development

### Can I use this with Home Assistant?

Yes, you can create custom Home Assistant integrations:

```python
# Example Home Assistant sensor
async def create_ha_sensor_data(device):
    async with device:
        data = await device.read_sensor_data()
        
    return {
        'temperature': data.temperature,
        'moisture': data.moisture,
        'brightness': data.brightness,
        'conductivity': data.conductivity,
        'battery': info.battery_level,
        'last_updated': data.timestamp.isoformat()
    }
```

### How do I log data to a database?

Example with SQLite:

```python
import sqlite3
import asyncio
from datetime import datetime

class PlantDataLogger:
    def __init__(self, db_path="plant_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY,
                device_mac TEXT,
                timestamp TEXT,
                temperature REAL,
                brightness INTEGER,
                moisture INTEGER,
                conductivity INTEGER
            )
        """)
        conn.commit()
        conn.close()
    
    async def log_device_data(self, device):
        async with device:
            data = await device.read_sensor_data()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO sensor_readings 
            (device_mac, timestamp, temperature, brightness, moisture, conductivity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            device.mac_address,
            data.timestamp.isoformat(),
            data.temperature,
            data.brightness,
            data.moisture,
            data.conductivity
        ))
        conn.commit()
        conn.close()
```

### Can I create a web dashboard?

Yes, using Flask or FastAPI:

```python
from flask import Flask, jsonify
import asyncio

app = Flask(__name__)

@app.route('/api/plants')
async def get_plant_data():
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices()
    
    plant_data = []
    for device in devices:
        try:
            async with device:
                data = await device.read_sensor_data()
                plant_data.append({
                    'name': device.name,
                    'mac': device.mac_address,
                    'temperature': data.temperature,
                    'moisture': data.moisture,
                    'brightness': data.brightness,
                    'conductivity': data.conductivity
                })
        except Exception as e:
            plant_data.append({
                'name': device.name,
                'mac': device.mac_address,
                'error': str(e)
            })
    
    return jsonify(plant_data)
```

### How do I contribute to the library?

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/awesome-feature`
3. **Make your changes** and add tests
4. **Run the tests**: `pytest`
5. **Submit a pull request**

Development setup:
```bash
git clone https://github.com/eljhr9/pyflowercare.git
cd pyflowercare
poetry install --with dev
pre-commit install
```

## Troubleshooting

### I'm getting import errors

**Check installation**:
```bash
pip list | grep growify
python -c "import flowercare; print('OK')"
```

**Virtual environment issues**:
```bash
# Ensure you're in the right environment
which python
pip install pyflowercare
```

### Bluetooth isn't working

**Linux**:
```bash
# Check Bluetooth service
systemctl status bluetooth

# Grant permissions
sudo setcap cap_net_raw+eip $(which python)
```

**macOS**:
- Check System Preferences → Bluetooth
- Grant app permissions in Security & Privacy

**Windows**:
- Ensure Windows 10 v1709+
- Update Bluetooth drivers
- Try different Bluetooth adapter

### Where can I get more help?

1. **Documentation**: Read the full documentation
2. **GitHub Issues**: Report bugs or request features
3. **Discussions**: Ask questions on GitHub Discussions
4. **Examples**: Check the `examples/` directory
5. **Troubleshooting**: See the detailed troubleshooting guide

Still need help? Create an issue with:
- Python version and OS
- Error messages and stack traces
- Minimal code example that reproduces the issue