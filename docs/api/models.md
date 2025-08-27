# Data Models

The FlowerCare library uses well-defined data models to represent sensor readings, device information, and historical data. These models provide type safety, clear interfaces, and convenient methods for working with plant sensor data.

## SensorData

::: flowercare.models.SensorData

The `SensorData` class represents a complete set of sensor measurements from a FlowerCare device.

### Fields

| Field | Type | Unit | Range | Description |
|-------|------|------|-------|-------------|
| `temperature` | `float` | °C | -10 to 60 | Air temperature near the plant |
| `brightness` | `int` | lux | 0 to 120,000 | Light intensity |
| `moisture` | `int` | % | 0 to 100 | Soil moisture percentage |
| `conductivity` | `int` | µS/cm | 0 to 10,000 | Soil electrical conductivity (fertility) |
| `timestamp` | `Optional[datetime]` | - | - | When the measurement was taken |

### Usage Examples

```python
# Reading sensor data
async with device:
    data = await device.read_sensor_data()
    
    # Access individual values
    temp = data.temperature      # 23.5
    light = data.brightness      # 15420
    moisture = data.moisture     # 42
    fertility = data.conductivity # 1180
    when = data.timestamp        # datetime object

# String representation
print(data)
# Output: Temperature: 23.5°C, Brightness: 15420 lux, Moisture: 42%, Conductivity: 1180 µS/cm

# JSON serialization
import json
from dataclasses import asdict

data_dict = asdict(data)
data_dict['timestamp'] = data.timestamp.isoformat() if data.timestamp else None
json_data = json.dumps(data_dict)
```

### Value Interpretation

#### Temperature (°C)
- **Optimal Range**: 18-24°C for most houseplants
- **Below 10°C**: Too cold, plant stress likely
- **Above 30°C**: Too hot, may need shade or relocation
- **Accuracy**: ±1°C typical

```python
def interpret_temperature(temp):
    if temp < 10:
        return "Too cold - risk of damage"
    elif temp < 18:
        return "Cool - growth may slow"
    elif temp <= 24:
        return "Optimal temperature"
    elif temp <= 30:
        return "Warm - monitor for stress"
    else:
        return "Too hot - provide shade"

status = interpret_temperature(data.temperature)
```

#### Brightness (lux)
- **Full sunlight**: ~100,000 lux
- **Partial shade**: 10,000-50,000 lux  
- **Bright indoor**: 1,000-5,000 lux
- **Low light plants**: 500-2,000 lux
- **Deep shade**: <500 lux

```python
def interpret_brightness(lux):
    if lux < 500:
        return "Very low light"
    elif lux < 2000:
        return "Low light - suitable for some plants"
    elif lux < 10000:
        return "Moderate indoor light"
    elif lux < 50000:
        return "Bright light - good for most plants"
    else:
        return "Very bright - may need shade"

light_condition = interpret_brightness(data.brightness)
```

#### Moisture (%)
- **0-20%**: Dry soil, watering needed
- **20-40%**: Slightly dry, monitor closely
- **40-70%**: Optimal moisture for most plants
- **70-90%**: Moist, reduce watering
- **90-100%**: Waterlogged, drainage issues

```python
def interpret_moisture(moisture):
    if moisture < 20:
        return "Dry - water immediately"
    elif moisture < 40:
        return "Slightly dry - water soon"
    elif moisture <= 70:
        return "Good moisture level"
    elif moisture <= 90:
        return "Moist - reduce watering"
    else:
        return "Waterlogged - check drainage"

water_status = interpret_moisture(data.moisture)
```

#### Conductivity (µS/cm)
- **0-200**: Very low nutrients, fertilize needed
- **200-500**: Low fertility, consider fertilizing
- **500-2000**: Good nutrient levels
- **2000-5000**: High fertility, may be excessive
- **>5000**: Very high, may damage roots

```python
def interpret_conductivity(conductivity):
    if conductivity < 200:
        return "Very low nutrients - fertilize needed"
    elif conductivity < 500:
        return "Low fertility - consider fertilizing"
    elif conductivity <= 2000:
        return "Good nutrient levels"
    elif conductivity <= 5000:
        return "High fertility - monitor for excess"
    else:
        return "Very high - may damage plant"

nutrient_status = interpret_conductivity(data.conductivity)
```

### Plant Health Analysis

```python
from dataclasses import dataclass
from typing import List

@dataclass
class PlantHealthAssessment:
    overall_score: int  # 0-100
    issues: List[str]
    recommendations: List[str]
    status: str  # "healthy", "attention_needed", "critical"

def assess_plant_health(data: SensorData) -> PlantHealthAssessment:
    """Comprehensive plant health assessment"""
    score = 100
    issues = []
    recommendations = []
    
    # Temperature assessment
    if data.temperature < 15 or data.temperature > 28:
        score -= 20
        issues.append("Temperature stress")
        if data.temperature < 15:
            recommendations.append("Move to warmer location")
        else:
            recommendations.append("Provide shade or cooling")
    
    # Light assessment
    if data.brightness < 1000:
        score -= 15
        issues.append("Insufficient light")
        recommendations.append("Move to brighter location")
    elif data.brightness > 80000:
        score -= 10
        issues.append("Too much direct light")
        recommendations.append("Provide some shade")
    
    # Moisture assessment
    if data.moisture < 20:
        score -= 25
        issues.append("Dry soil")
        recommendations.append("Water immediately")
    elif data.moisture > 85:
        score -= 20
        issues.append("Overwatered")
        recommendations.append("Improve drainage, reduce watering")
    
    # Fertility assessment
    if data.conductivity < 200:
        score -= 15
        issues.append("Low nutrients")
        recommendations.append("Apply fertilizer")
    elif data.conductivity > 3000:
        score -= 10
        issues.append("Excess nutrients")
        recommendations.append("Flush soil, reduce fertilizer")
    
    # Determine overall status
    if score >= 80:
        status = "healthy"
    elif score >= 60:
        status = "attention_needed"
    else:
        status = "critical"
    
    return PlantHealthAssessment(
        overall_score=max(0, score),
        issues=issues,
        recommendations=recommendations,
        status=status
    )

# Usage
health = assess_plant_health(data)
print(f"Plant Health Score: {health.overall_score}/100")
print(f"Status: {health.status}")
if health.issues:
    print("Issues:", ", ".join(health.issues))
    print("Recommendations:", ", ".join(health.recommendations))
```

## DeviceInfo

::: flowercare.models.DeviceInfo

The `DeviceInfo` class contains metadata about a FlowerCare device.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Device advertised name (typically "Flower care") |
| `mac_address` | `str` | Unique Bluetooth MAC address |
| `firmware_version` | `Optional[str]` | Device firmware version |
| `battery_level` | `Optional[int]` | Battery percentage (0-100) |

### Usage Examples

```python
# Get device information
async with device:
    info = await device.get_device_info()
    
    print(f"Device: {info.name}")
    print(f"MAC: {info.mac_address}")
    print(f"Firmware: {info.firmware_version}")
    print(f"Battery: {info.battery_level}%")

# String representation
print(info)
# Output: Device: Flower care (C4:7C:8D:6A:8E:CA), Firmware: 3.2.9, Battery: 85%

# Battery monitoring
def check_battery_status(info: DeviceInfo) -> str:
    if info.battery_level is None:
        return "Unknown"
    elif info.battery_level < 10:
        return "Critical - replace battery"
    elif info.battery_level < 20:
        return "Low - battery replacement needed soon"
    elif info.battery_level < 50:
        return "Moderate - monitor battery level"
    else:
        return "Good"

battery_status = check_battery_status(info)
print(f"Battery Status: {battery_status}")
```

### Firmware Versions

Common firmware versions and their capabilities:

| Version | Features | Notes |
|---------|----------|--------|
| 2.6.6 | Basic sensors | Original firmware |
| 2.7.0+ | Improved accuracy | Better temperature calibration |
| 3.1.8+ | Enhanced BLE | More reliable connections |
| 3.2.9+ | Latest features | Current production firmware |

```python
def check_firmware_compatibility(info: DeviceInfo) -> str:
    """Check if firmware supports all features"""
    if info.firmware_version is None:
        return "Unknown firmware version"
    
    version = info.firmware_version
    
    # Parse version (e.g., "3.2.9" -> [3, 2, 9])
    try:
        parts = [int(x) for x in version.split('.')]
        major, minor = parts[0], parts[1]
        
        if major < 2 or (major == 2 and minor < 6):
            return "Very old firmware - consider device replacement"
        elif major < 3:
            return "Old firmware - basic features only"
        elif major == 3 and minor < 2:
            return "Good firmware with enhanced BLE"
        else:
            return "Latest firmware with all features"
            
    except (ValueError, IndexError):
        return f"Unknown firmware format: {version}"

compatibility = check_firmware_compatibility(info)
```

## HistoricalEntry

::: flowercare.models.HistoricalEntry

The `HistoricalEntry` class represents a single historical sensor reading with its timestamp.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `datetime` | When the measurement was recorded |
| `sensor_data` | `SensorData` | The sensor measurements |

### Usage Examples

```python
# Get historical data
async with device:
    history = await device.get_historical_data()
    
    print(f"Found {len(history)} historical entries")
    
    # Show recent entries
    for entry in history[-5:]:
        print(f"{entry.timestamp}: {entry.sensor_data}")

# Data analysis
def analyze_history(history: List[HistoricalEntry]) -> dict:
    """Analyze historical trends"""
    if not history:
        return {"error": "No data available"}
    
    # Extract values
    temperatures = [entry.sensor_data.temperature for entry in history]
    moistures = [entry.sensor_data.moisture for entry in history]
    conductivities = [entry.sensor_data.conductivity for entry in history]
    brightnesses = [entry.sensor_data.brightness for entry in history]
    
    # Calculate statistics
    return {
        "duration": {
            "start": history[0].timestamp,
            "end": history[-1].timestamp,
            "days": (history[-1].timestamp - history[0].timestamp).days
        },
        "temperature": {
            "avg": sum(temperatures) / len(temperatures),
            "min": min(temperatures),
            "max": max(temperatures)
        },
        "moisture": {
            "avg": sum(moistures) / len(moistures),
            "min": min(moistures),
            "max": max(moistures)
        },
        "conductivity": {
            "avg": sum(conductivities) / len(conductivities),
            "min": min(conductivities),
            "max": max(conductivities)
        },
        "brightness": {
            "avg": sum(brightnesses) / len(brightnesses),
            "min": min(brightnesses),
            "max": max(brightnesses)
        }
    }

# Usage
analysis = analyze_history(history)
print(f"Data span: {analysis['duration']['days']} days")
print(f"Average temperature: {analysis['temperature']['avg']:.1f}°C")
print(f"Moisture range: {analysis['moisture']['min']}% - {analysis['moisture']['max']}%")
```

### Trend Analysis

```python
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def plot_sensor_trends(history: List[HistoricalEntry], days: int = 7):
    """Plot sensor data trends for the last N days"""
    if not history:
        print("No historical data to plot")
        return
    
    # Filter to last N days
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_data = [entry for entry in history if entry.timestamp >= cutoff_date]
    
    if not recent_data:
        print(f"No data in the last {days} days")
        return
    
    # Extract data
    timestamps = [entry.timestamp for entry in recent_data]
    temperatures = [entry.sensor_data.temperature for entry in recent_data]
    moistures = [entry.sensor_data.moisture for entry in recent_data]
    conductivities = [entry.sensor_data.conductivity for entry in recent_data]
    
    # Create plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    
    # Temperature
    ax1.plot(timestamps, temperatures, 'r-', linewidth=2)
    ax1.set_title('Temperature')
    ax1.set_ylabel('°C')
    ax1.grid(True, alpha=0.3)
    
    # Moisture
    ax2.plot(timestamps, moistures, 'b-', linewidth=2)
    ax2.set_title('Soil Moisture')
    ax2.set_ylabel('%')
    ax2.grid(True, alpha=0.3)
    
    # Conductivity
    ax3.plot(timestamps, conductivities, 'g-', linewidth=2)
    ax3.set_title('Soil Conductivity')
    ax3.set_ylabel('µS/cm')
    ax3.grid(True, alpha=0.3)
    
    # All sensors normalized
    ax4.plot(timestamps, [t/30 for t in temperatures], 'r-', label='Temp (÷30)', alpha=0.7)
    ax4.plot(timestamps, [m/100 for m in moistures], 'b-', label='Moisture (÷100)', alpha=0.7)
    ax4.plot(timestamps, [c/2000 for c in conductivities], 'g-', label='Conductivity (÷2000)', alpha=0.7)
    ax4.set_title('All Sensors (Normalized)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# Usage
plot_sensor_trends(history, days=14)
```

## Data Export

### CSV Export

```python
import csv
from typing import List

def export_to_csv(history: List[HistoricalEntry], filename: str):
    """Export historical data to CSV file"""
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'temperature', 'brightness', 
            'moisture', 'conductivity'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for entry in history:
            writer.writerow({
                'timestamp': entry.timestamp.isoformat(),
                'temperature': entry.sensor_data.temperature,
                'brightness': entry.sensor_data.brightness,
                'moisture': entry.sensor_data.moisture,
                'conductivity': entry.sensor_data.conductivity
            })
    
    print(f"Exported {len(history)} entries to {filename}")

# Usage
export_to_csv(history, "plant_data.csv")
```

### JSON Export

```python
import json
from dataclasses import asdict

def export_to_json(history: List[HistoricalEntry], filename: str):
    """Export historical data to JSON file"""
    
    data = []
    for entry in history:
        entry_dict = {
            'timestamp': entry.timestamp.isoformat(),
            'sensor_data': asdict(entry.sensor_data)
        }
        # Convert timestamp in sensor_data to string
        if entry_dict['sensor_data']['timestamp']:
            entry_dict['sensor_data']['timestamp'] = entry.sensor_data.timestamp.isoformat()
        data.append(entry_dict)
    
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=2)
    
    print(f"Exported {len(history)} entries to {filename}")

# Usage
export_to_json(history, "plant_data.json")
```

## Custom Data Models

You can extend the existing models or create custom ones for your specific needs:

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class PlantProfile:
    """Extended plant information"""
    device_mac: str
    plant_name: str
    plant_species: str
    location: str
    planted_date: datetime
    optimal_temp_range: tuple  # (min, max)
    optimal_moisture_range: tuple  # (min, max)
    notes: Optional[str] = None

@dataclass
class SensorAlert:
    """Sensor-based alert"""
    device_mac: str
    alert_type: str  # "low_moisture", "high_temperature", etc.
    current_value: float
    threshold_value: float
    severity: str  # "low", "medium", "high"
    timestamp: datetime
    message: str

@dataclass
class PlantCareEvent:
    """Record of plant care activities"""
    device_mac: str
    event_type: str  # "watered", "fertilized", "repotted"
    timestamp: datetime
    notes: Optional[str] = None
    sensor_data_before: Optional[SensorData] = None
    sensor_data_after: Optional[SensorData] = None

# Usage example
def create_plant_profile(device: FlowerCareDevice) -> PlantProfile:
    """Interactive plant profile creation"""
    
    plant_name = input("Plant name: ")
    species = input("Plant species: ")
    location = input("Location: ")
    
    # Get optimal ranges based on species (simplified)
    species_ranges = {
        "pothos": ((18, 26), (40, 70)),
        "snake_plant": ((18, 27), (20, 50)),
        "fiddle_leaf_fig": ((20, 25), (50, 70)),
    }
    
    temp_range, moisture_range = species_ranges.get(
        species.lower(), 
        ((18, 24), (40, 70))  # Default ranges
    )
    
    return PlantProfile(
        device_mac=device.mac_address,
        plant_name=plant_name,
        plant_species=species,
        location=location,
        planted_date=datetime.now(),
        optimal_temp_range=temp_range,
        optimal_moisture_range=moisture_range
    )

def check_sensor_alerts(data: SensorData, profile: PlantProfile) -> List[SensorAlert]:
    """Generate alerts based on sensor data and plant profile"""
    alerts = []
    
    # Temperature alerts
    temp_min, temp_max = profile.optimal_temp_range
    if data.temperature < temp_min:
        alerts.append(SensorAlert(
            device_mac=profile.device_mac,
            alert_type="low_temperature",
            current_value=data.temperature,
            threshold_value=temp_min,
            severity="medium" if data.temperature > temp_min - 5 else "high",
            timestamp=datetime.now(),
            message=f"{profile.plant_name} is too cold: {data.temperature}°C"
        ))
    elif data.temperature > temp_max:
        alerts.append(SensorAlert(
            device_mac=profile.device_mac,
            alert_type="high_temperature",
            current_value=data.temperature,
            threshold_value=temp_max,
            severity="medium" if data.temperature < temp_max + 5 else "high",
            timestamp=datetime.now(),
            message=f"{profile.plant_name} is too hot: {data.temperature}°C"
        ))
    
    # Moisture alerts
    moisture_min, moisture_max = profile.optimal_moisture_range
    if data.moisture < moisture_min:
        alerts.append(SensorAlert(
            device_mac=profile.device_mac,
            alert_type="low_moisture",
            current_value=data.moisture,
            threshold_value=moisture_min,
            severity="high" if data.moisture < 20 else "medium",
            timestamp=datetime.now(),
            message=f"{profile.plant_name} needs water: {data.moisture}%"
        ))
    
    return alerts
```

This comprehensive data model system allows you to build sophisticated plant monitoring applications with type safety, clear interfaces, and extensible functionality.