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

    # Method 1: Scan for devices (discovers devices via Bluetooth)
    print("Method 1: Scanning for FlowerCare devices...")
    devices = await scanner.scan_for_devices(timeout=10.0)

    if devices:
        print(f"Found {len(devices)} device(s) via scanning")
        for device in devices[:1]:  # Connect to first found device
            await connect_and_read(device)
    else:
        print("No FlowerCare devices found via scanning")

    # Method 2: Connect directly by MAC address (no scanning required)
    print("\nMethod 2: Connecting directly by MAC address...")
    print("Replace 'YOUR_DEVICE_MAC' with your actual device MAC address")

    # Example MAC address - replace with your actual device MAC
    device_mac = "C4:7C:8D:6A:8E:CA"
    device = await scanner.find_device_by_address(device_mac)

    if device:
        print(f"Created device for MAC: {device.mac_address}")
        await connect_and_read(device)
    else:
        print("Invalid MAC address format")


async def connect_and_read(device):
    """Connect to a device and read its data."""
    print(f"\nConnecting to {device.name or 'Unknown'} ({device.mac_address})...")

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
