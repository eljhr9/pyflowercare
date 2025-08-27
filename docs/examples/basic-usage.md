# Basic Usage Examples

This section provides fundamental examples to get you started with the FlowerCare library. These examples cover the most common use cases and serve as building blocks for more advanced applications.

## Simple Device Discovery and Reading

The most basic use case - find a device and read its data:

```python title="simple_reading.py"
import asyncio
from pyflowercare import FlowerCareScanner, setup_logging

async def main():
    # Enable logging to see what's happening
    setup_logging("INFO")
    
    # Create scanner and find devices
    scanner = FlowerCareScanner()
    print("🔍 Scanning for FlowerCare devices...")
    
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if not devices:
        print("❌ No devices found")
        print("💡 Make sure your FlowerCare device is nearby and not connected to another app")
        return
    
    # Use the first device found
    device = devices[0]
    print(f"✅ Found device: {device.name} ({device.mac_address})")
    
    # Connect and read data
    async with device:
        data = await device.read_sensor_data()
        
        print("\n📊 Current Conditions:")
        print(f"🌡️  Temperature: {data.temperature}°C")
        print(f"☀️  Brightness: {data.brightness:,} lux")
        print(f"💧 Moisture: {data.moisture}%")
        print(f"🌿 Conductivity: {data.conductivity} µS/cm")
        print(f"⏰ Measured: {data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Expected Output:**
```
🔍 Scanning for FlowerCare devices...
✅ Found device: Flower care (C4:7C:8D:6A:8E:CA)

📊 Current Conditions:
🌡️  Temperature: 23.2°C
☀️  Brightness: 15,420 lux
💧 Moisture: 42%
🌿 Conductivity: 1,180 µS/cm
⏰ Measured: 2024-01-15 14:30:22
```

## Device Information and Health Check

Get comprehensive information about your device:

```python title="device_info.py"
import asyncio
from pyflowercare import FlowerCareScanner

async def device_health_check():
    """Comprehensive device health and information check"""
    
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices(timeout=15.0)
    
    if not devices:
        print("No devices found for health check")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"\n{'='*50}")
        print(f"Device {i}: {device.name}")
        print(f"{'='*50}")
        
        try:
            async with device:
                # Get device information
                print("📱 Device Information:")
                info = await device.get_device_info()
                print(f"  Name: {info.name}")
                print(f"  MAC Address: {info.mac_address}")
                print(f"  Firmware: {info.firmware_version or 'Unknown'}")
                
                # Battery status with visual indicator
                battery = info.battery_level
                if battery is not None:
                    if battery > 70:
                        battery_icon = "🟢"
                        battery_status = "Good"
                    elif battery > 30:
                        battery_icon = "🟡"
                        battery_status = "Moderate"
                    else:
                        battery_icon = "🔴"
                        battery_status = "Low - Replace Soon"
                    
                    print(f"  Battery: {battery}% {battery_icon} ({battery_status})")
                else:
                    print("  Battery: Unknown")
                
                # Current sensor readings
                print("\n📊 Current Readings:")
                data = await device.read_sensor_data()
                print(f"  Temperature: {data.temperature}°C")
                print(f"  Brightness: {data.brightness:,} lux")
                print(f"  Soil Moisture: {data.moisture}%")
                print(f"  Soil Conductivity: {data.conductivity} µS/cm")
                
                # Basic plant health assessment
                health_issues = []
                if data.temperature < 15:
                    health_issues.append("Temperature too cold")
                elif data.temperature > 30:
                    health_issues.append("Temperature too hot")
                
                if data.moisture < 20:
                    health_issues.append("Soil too dry - needs water")
                elif data.moisture > 80:
                    health_issues.append("Soil too wet - check drainage")
                
                if data.brightness < 1000:
                    health_issues.append("Low light conditions")
                
                if data.conductivity < 200:
                    health_issues.append("Low soil nutrients")
                
                print("\n🏥 Health Assessment:")
                if health_issues:
                    print("  ⚠️  Issues detected:")
                    for issue in health_issues:
                        print(f"    • {issue}")
                else:
                    print("  ✅ All conditions look good!")
                
                # Test LED functionality
                print("\n💡 Testing LED...")
                await device.blink_led()
                print("  LED blink command sent successfully")
                
        except Exception as e:
            print(f"❌ Error checking device: {e}")

if __name__ == "__main__":
    asyncio.run(device_health_check())
```

## Working with Multiple Devices

Handle multiple FlowerCare devices simultaneously:

```python title="multiple_devices.py"
import asyncio
from pyflowercare import FlowerCareScanner
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class PlantInfo:
    name: str
    location: str
    optimal_moisture_min: int = 30
    optimal_moisture_max: int = 70

async def monitor_multiple_plants():
    """Monitor multiple plants with custom names and settings"""
    
    # Define your plants (update MAC addresses to match your devices)
    plant_registry: Dict[str, PlantInfo] = {
        "C4:7C:8D:6A:8E:CA": PlantInfo("Monstera Deliciosa", "Living Room", 40, 80),
        "C4:7C:8D:6B:8F:CB": PlantInfo("Snake Plant", "Bedroom", 20, 50),
        "C4:7C:8D:6C:90:CC": PlantInfo("Pothos", "Kitchen Window", 35, 75),
    }
    
    scanner = FlowerCareScanner()
    print("🔍 Scanning for FlowerCare devices...")
    devices = await scanner.scan_for_devices(timeout=15.0)
    
    if not devices:
        print("❌ No devices found")
        return
    
    print(f"✅ Found {len(devices)} device(s)")
    
    # Read all devices concurrently
    async def read_plant_data(device):
        """Read data from a single plant"""
        mac = device.mac_address
        plant_info = plant_registry.get(mac)
        
        try:
            async with device:
                data = await device.read_sensor_data()
                
                # Plant name and location
                if plant_info:
                    name = plant_info.name
                    location = plant_info.location
                    moisture_min = plant_info.optimal_moisture_min
                    moisture_max = plant_info.optimal_moisture_max
                else:
                    name = f"Unknown Plant"
                    location = "Unknown Location"
                    moisture_min, moisture_max = 30, 70
                
                # Moisture status check
                if data.moisture < moisture_min:
                    moisture_status = "🔴 Too Dry - Water Needed"
                elif data.moisture > moisture_max:
                    moisture_status = "🔵 Too Wet - Check Drainage"
                else:
                    moisture_status = "🟢 Good"
                
                # Temperature status
                if data.temperature < 18:
                    temp_status = "🥶 Too Cold"
                elif data.temperature > 26:
                    temp_status = "🥵 Too Hot"
                else:
                    temp_status = "🌡️ Good"
                
                return {
                    'name': name,
                    'location': location,
                    'mac': mac,
                    'data': data,
                    'moisture_status': moisture_status,
                    'temp_status': temp_status,
                    'error': None
                }
                
        except Exception as e:
            return {
                'name': plant_info.name if plant_info else "Unknown",
                'location': plant_info.location if plant_info else "Unknown",
                'mac': mac,
                'data': None,
                'error': str(e)
            }
    
    # Read all devices concurrently
    print("\n📊 Reading data from all plants...")
    results = await asyncio.gather(*[read_plant_data(device) for device in devices])
    
    # Display results
    print(f"\n{'='*80}")
    print("🌱 PLANT STATUS REPORT")
    print(f"{'='*80}")
    
    for result in results:
        print(f"\n🏷️  {result['name']} ({result['location']})")
        print(f"   MAC: {result['mac']}")
        
        if result['error']:
            print(f"   ❌ Error: {result['error']}")
        else:
            data = result['data']
            print(f"   🌡️  Temperature: {data.temperature}°C {result['temp_status']}")
            print(f"   💧 Moisture: {data.moisture}% {result['moisture_status']}")
            print(f"   ☀️  Brightness: {data.brightness:,} lux")
            print(f"   🌿 Conductivity: {data.conductivity} µS/cm")
    
    # Summary
    successful_reads = sum(1 for r in results if not r['error'])
    failed_reads = len(results) - successful_reads
    
    print(f"\n📈 Summary: {successful_reads} successful, {failed_reads} failed")
    
    # Plants needing attention
    needs_attention = [r for r in results if r.get('data') and 
                      ('Too Dry' in r['moisture_status'] or 'Too Cold' in r['temp_status'] or 'Too Hot' in r['temp_status'])]
    
    if needs_attention:
        print(f"\n⚠️  Plants needing attention:")
        for plant in needs_attention:
            issues = []
            if 'Too Dry' in plant['moisture_status']:
                issues.append("needs water")
            if 'Too Cold' in plant['temp_status']:
                issues.append("too cold")
            if 'Too Hot' in plant['temp_status']:
                issues.append("too hot")
            
            print(f"   • {plant['name']}: {', '.join(issues)}")
    else:
        print(f"\n✅ All plants are healthy!")

if __name__ == "__main__":
    asyncio.run(monitor_multiple_plants())
```

## Historical Data Analysis

Access and analyze historical sensor data:

```python title="history_analysis.py"
import asyncio
from pyflowercare import FlowerCareScanner
from datetime import datetime, timedelta
import statistics

async def analyze_plant_history():
    """Analyze historical data to understand plant patterns"""
    
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if not devices:
        print("No devices found")
        return
    
    device = devices[0]  # Analyze first device
    
    print(f"📊 Analyzing historical data for {device.name} ({device.mac_address})")
    print("⏳ Reading historical data... (this may take 30+ seconds)")
    
    async with device:
        # Get current data for comparison
        current_data = await device.read_sensor_data()
        
        # Get historical data
        history = await device.get_historical_data()
        
        if not history:
            print("❌ No historical data available")
            return
        
        print(f"✅ Found {len(history)} historical entries")
        
        # Extract data arrays
        temperatures = [entry.sensor_data.temperature for entry in history]
        moistures = [entry.sensor_data.moisture for entry in history]
        brightnesses = [entry.sensor_data.brightness for entry in history]
        conductivities = [entry.sensor_data.conductivity for entry in history]
        
        # Time range analysis
        start_date = history[0].timestamp
        end_date = history[-1].timestamp
        duration = end_date - start_date
        
        print(f"\n📅 Data Range:")
        print(f"   From: {start_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   To: {end_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Duration: {duration.days} days, {duration.seconds // 3600} hours")
        
        # Statistical analysis
        print(f"\n📈 Temperature Analysis:")
        print(f"   Current: {current_data.temperature}°C")
        print(f"   Average: {statistics.mean(temperatures):.1f}°C")
        print(f"   Range: {min(temperatures):.1f}°C to {max(temperatures):.1f}°C")
        print(f"   Std Dev: {statistics.stdev(temperatures):.1f}°C")
        
        print(f"\n💧 Moisture Analysis:")
        print(f"   Current: {current_data.moisture}%")
        print(f"   Average: {statistics.mean(moistures):.1f}%")
        print(f"   Range: {min(moistures)}% to {max(moistures)}%")
        print(f"   Std Dev: {statistics.stdev(moistures):.1f}%")
        
        print(f"\n☀️  Brightness Analysis:")
        print(f"   Current: {current_data.brightness:,} lux")
        print(f"   Average: {statistics.mean(brightnesses):,.0f} lux")
        print(f"   Range: {min(brightnesses):,} to {max(brightnesses):,} lux")
        
        print(f"\n🌿 Conductivity Analysis:")
        print(f"   Current: {current_data.conductivity} µS/cm")
        print(f"   Average: {statistics.mean(conductivities):.0f} µS/cm")
        print(f"   Range: {min(conductivities)} to {max(conductivities)} µS/cm")
        
        # Trend analysis (last 7 days vs overall average)
        week_ago = datetime.now() - timedelta(days=7)
        recent_entries = [entry for entry in history if entry.timestamp >= week_ago]
        
        if len(recent_entries) > 5:
            recent_temps = [entry.sensor_data.temperature for entry in recent_entries]
            recent_moistures = [entry.sensor_data.moisture for entry in recent_entries]
            
            avg_temp_recent = statistics.mean(recent_temps)
            avg_moisture_recent = statistics.mean(recent_moistures)
            avg_temp_overall = statistics.mean(temperatures)
            avg_moisture_overall = statistics.mean(moistures)
            
            print(f"\n📊 Recent Trends (Last 7 Days vs Overall):")
            temp_trend = avg_temp_recent - avg_temp_overall
            moisture_trend = avg_moisture_recent - avg_moisture_overall
            
            temp_arrow = "📈" if temp_trend > 1 else "📉" if temp_trend < -1 else "➡️"
            moisture_arrow = "📈" if moisture_trend > 5 else "📉" if moisture_trend < -5 else "➡️"
            
            print(f"   Temperature: {temp_arrow} {temp_trend:+.1f}°C change")
            print(f"   Moisture: {moisture_arrow} {moisture_trend:+.1f}% change")
        
        # Find extreme events
        print(f"\n🔍 Notable Events:")
        
        # Lowest moisture (drought events)
        min_moisture_entry = min(history, key=lambda x: x.sensor_data.moisture)
        print(f"   Driest: {min_moisture_entry.sensor_data.moisture}% on {min_moisture_entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        # Highest temperature
        max_temp_entry = max(history, key=lambda x: x.sensor_data.temperature)
        print(f"   Hottest: {max_temp_entry.sensor_data.temperature}°C on {max_temp_entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        # Brightest day
        max_brightness_entry = max(history, key=lambda x: x.sensor_data.brightness)
        print(f"   Brightest: {max_brightness_entry.sensor_data.brightness:,} lux on {max_brightness_entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
        
        # Care recommendations based on trends
        print(f"\n💡 Care Recommendations:")
        
        if statistics.mean(moistures) < 30:
            print("   • Consider watering more frequently")
        elif statistics.mean(moistures) > 70:
            print("   • Reduce watering frequency or improve drainage")
        else:
            print("   • Watering schedule appears good")
        
        if statistics.mean(temperatures) < 18:
            print("   • Plant may benefit from a warmer location")
        elif statistics.mean(temperatures) > 26:
            print("   • Consider moving to a cooler location")
        else:
            print("   • Temperature conditions are good")
        
        if statistics.mean(brightnesses) < 5000:
            print("   • Consider moving to a brighter location")
        elif statistics.mean(brightnesses) > 80000:
            print("   • Plant may benefit from some shade during peak hours")
        else:
            print("   • Light conditions are appropriate")

if __name__ == "__main__":
    asyncio.run(analyze_plant_history())
```

## Error Handling and Recovery

Robust error handling for production use:

```python title="robust_monitoring.py"
import asyncio
import logging
from datetime import datetime
from pyflowercare import FlowerCareScanner
from pyflowercare.exceptions import (
    FlowerCareError, ConnectionError, DeviceError, 
    DataParsingError, TimeoutError
)

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobustPlantMonitor:
    def __init__(self):
        self.scanner = FlowerCareScanner()
        self.device_errors = {}  # Track error counts per device
        self.last_successful_data = {}  # Cache last good readings
        
    async def safe_device_read(self, device, max_retries=3):
        """Safely read device data with retries and error handling"""
        
        mac = device.mac_address
        
        for attempt in range(max_retries):
            try:
                async with device:
                    # Try to read device info first (quick check)
                    info = await device.get_device_info()
                    
                    # Read sensor data
                    data = await device.read_sensor_data()
                    
                    # Success - reset error count and cache data
                    self.device_errors[mac] = 0
                    self.last_successful_data[mac] = {
                        'data': data,
                        'timestamp': datetime.now(),
                        'device_info': info
                    }
                    
                    logger.info(f"Successfully read data from {device.name} ({mac})")
                    return data
                    
            except ConnectionError as e:
                logger.warning(f"Connection failed for {mac} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except TimeoutError as e:
                logger.warning(f"Timeout for {mac} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    
            except DataParsingError as e:
                logger.error(f"Data parsing error for {mac}: {e}")
                # Don't retry data parsing errors
                break
                
            except DeviceError as e:
                logger.error(f"Device error for {mac}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    
            except FlowerCareError as e:
                logger.error(f"Unexpected FlowerCare error for {mac}: {e}")
                break
                
        # All attempts failed
        self.device_errors[mac] = self.device_errors.get(mac, 0) + 1
        logger.error(f"Failed to read {mac} after {max_retries} attempts (total errors: {self.device_errors[mac]})")
        return None
    
    def get_cached_data(self, mac_address, max_age_minutes=60):
        """Get cached data if it's recent enough"""
        
        if mac_address not in self.last_successful_data:
            return None
            
        cached = self.last_successful_data[mac_address]
        age = (datetime.now() - cached['timestamp']).total_seconds() / 60
        
        if age <= max_age_minutes:
            logger.info(f"Using cached data for {mac_address} ({age:.1f} minutes old)")
            return cached['data']
        else:
            logger.debug(f"Cached data for {mac_address} is too old ({age:.1f} minutes)")
            return None
    
    def get_device_status(self, mac_address):
        """Get device health status"""
        error_count = self.device_errors.get(mac_address, 0)
        has_recent_data = mac_address in self.last_successful_data
        
        if error_count == 0 and has_recent_data:
            return "healthy"
        elif error_count < 3:
            return "warning"
        else:
            return "critical"
    
    async def monitor_devices(self, duration_minutes=None):
        """Monitor all devices with error recovery"""
        
        logger.info("Starting robust plant monitoring...")
        
        # Initial device discovery
        devices = await self.scanner.scan_for_devices(timeout=15.0)
        if not devices:
            logger.error("No devices found")
            return
        
        logger.info(f"Found {len(devices)} device(s) to monitor")
        
        start_time = datetime.now()
        monitoring = True
        
        while monitoring:
            try:
                logger.info("Reading all devices...")
                
                # Read all devices
                for device in devices:
                    data = await self.safe_device_read(device)
                    
                    if data:
                        # Device read successfully
                        status = self.get_device_status(device.mac_address)
                        print(f"✅ {device.name}: {data.temperature}°C, {data.moisture}% ({status})")
                    else:
                        # Try cached data
                        cached_data = self.get_cached_data(device.mac_address)
                        status = self.get_device_status(device.mac_address)
                        
                        if cached_data:
                            print(f"⚠️  {device.name}: {cached_data.temperature}°C, {cached_data.moisture}% (cached, {status})")
                        else:
                            print(f"❌ {device.name}: No data available ({status})")
                
                # Check if we should continue
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        monitoring = False
                
                # Wait before next reading cycle
                if monitoring:
                    logger.info("Waiting 5 minutes before next reading...")
                    await asyncio.sleep(300)  # 5 minutes
                    
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                monitoring = False
                
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
        
        # Final status report
        logger.info("Monitoring session complete")
        self.print_status_report()
    
    def print_status_report(self):
        """Print final status report"""
        print(f"\n{'='*60}")
        print("📊 MONITORING SESSION REPORT")
        print(f"{'='*60}")
        
        for mac, error_count in self.device_errors.items():
            status = self.get_device_status(mac)
            has_data = mac in self.last_successful_data
            
            status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}.get(status, "❓")
            
            print(f"{status_emoji} Device {mac}:")
            print(f"   Status: {status}")
            print(f"   Errors: {error_count}")
            print(f"   Has Data: {'Yes' if has_data else 'No'}")
            
            if has_data:
                last_data = self.last_successful_data[mac]
                age = (datetime.now() - last_data['timestamp']).total_seconds() / 60
                print(f"   Last Reading: {age:.1f} minutes ago")

async def main():
    """Run robust plant monitoring"""
    
    monitor = RobustPlantMonitor()
    
    # Monitor for 30 minutes (or indefinitely if None)
    await monitor.monitor_devices(duration_minutes=30)

if __name__ == "__main__":
    asyncio.run(main())
```

## Data Export and Logging

Save sensor data for long-term analysis:

```python title="data_export.py"
import asyncio
import csv
import json
from datetime import datetime
from pathlib import Path
from pyflowercare import FlowerCareScanner

async def export_plant_data():
    """Export current and historical data to files"""
    
    scanner = FlowerCareScanner()
    devices = await scanner.scan_for_devices(timeout=10.0)
    
    if not devices:
        print("No devices found")
        return
    
    # Create export directory
    export_dir = Path("plant_data_export")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for device in devices:
        print(f"\n📊 Exporting data from {device.name} ({device.mac_address})")
        
        try:
            async with device:
                # Get device info
                info = await device.get_device_info()
                
                # Get current data
                current_data = await device.read_sensor_data()
                
                # Get historical data
                print("   Reading historical data...")
                history = await device.get_historical_data()
                
                # Prepare filenames
                safe_mac = device.mac_address.replace(":", "_")
                base_filename = f"flowercare_{safe_mac}_{timestamp}"
                
                # Export current data to JSON
                current_file = export_dir / f"{base_filename}_current.json"
                current_export = {
                    "device_info": {
                        "name": info.name,
                        "mac_address": info.mac_address,
                        "firmware_version": info.firmware_version,
                        "battery_level": info.battery_level
                    },
                    "current_data": {
                        "temperature": current_data.temperature,
                        "brightness": current_data.brightness,
                        "moisture": current_data.moisture,
                        "conductivity": current_data.conductivity,
                        "timestamp": current_data.timestamp.isoformat()
                    },
                    "export_timestamp": datetime.now().isoformat()
                }
                
                with open(current_file, 'w') as f:
                    json.dump(current_export, f, indent=2)
                print(f"   ✅ Current data exported to {current_file}")
                
                # Export historical data to CSV
                if history:
                    history_file = export_dir / f"{base_filename}_history.csv"
                    
                    with open(history_file, 'w', newline='') as f:
                        fieldnames = ['timestamp', 'temperature', 'brightness', 'moisture', 'conductivity']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        
                        writer.writeheader()
                        for entry in history:
                            writer.writerow({
                                'timestamp': entry.timestamp.isoformat(),
                                'temperature': entry.sensor_data.temperature,
                                'brightness': entry.sensor_data.brightness,
                                'moisture': entry.sensor_data.moisture,
                                'conductivity': entry.sensor_data.conductivity
                            })
                    
                    print(f"   ✅ Historical data ({len(history)} entries) exported to {history_file}")
                else:
                    print("   ℹ️  No historical data available")
                
                # Export detailed JSON with everything
                full_file = export_dir / f"{base_filename}_full.json"
                full_export = {
                    "device_info": current_export["device_info"],
                    "current_data": current_export["current_data"],
                    "historical_data": [
                        {
                            "timestamp": entry.timestamp.isoformat(),
                            "temperature": entry.sensor_data.temperature,
                            "brightness": entry.sensor_data.brightness,
                            "moisture": entry.sensor_data.moisture,
                            "conductivity": entry.sensor_data.conductivity
                        }
                        for entry in history
                    ] if history else [],
                    "export_timestamp": datetime.now().isoformat(),
                    "statistics": {
                        "historical_entries": len(history) if history else 0,
                        "date_range": {
                            "start": history[0].timestamp.isoformat() if history else None,
                            "end": history[-1].timestamp.isoformat() if history else None
                        } if history else None
                    }
                }
                
                with open(full_file, 'w') as f:
                    json.dump(full_export, f, indent=2)
                print(f"   ✅ Complete data exported to {full_file}")
                
        except Exception as e:
            print(f"   ❌ Error exporting {device.mac_address}: {e}")
    
    print(f"\n📁 All exports saved to: {export_dir.absolute()}")

if __name__ == "__main__":
    asyncio.run(export_plant_data())
```

These examples provide a solid foundation for building FlowerCare applications. They demonstrate:

- **Basic sensor reading** and device management
- **Error handling** and retry logic  
- **Multiple device** management
- **Historical data analysis** and trend identification
- **Data export** for long-term storage
- **Robust monitoring** with caching and recovery

Each example is self-contained and can be adapted for your specific needs.