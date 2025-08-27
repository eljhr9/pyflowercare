#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyflowercare import FlowerCareScanner, setup_logging


async def main():
    setup_logging("INFO")

    scanner = FlowerCareScanner()

    print("Scanning for FlowerCare devices...")
    devices = await scanner.scan_for_devices(timeout=10.0)

    if not devices:
        print("No FlowerCare devices found")
        return

    print(f"Found {len(devices)} device(s)")

    for device in devices:
        print(f"\nConnecting to {device.name} ({device.mac_address})...")

        try:
            async with device:
                device_info = await device.get_device_info()
                print(f"Device Info: {device_info}")

                sensor_data = await device.read_sensor_data()
                print(f"Sensor Data: {sensor_data}")

                print("Blinking LED...")
                await device.blink_led()

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
