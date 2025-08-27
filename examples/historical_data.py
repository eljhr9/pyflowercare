#!/usr/bin/env python3
import asyncio
import csv
import sys
from datetime import datetime
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

    for device in devices:
        print(f"\nConnecting to {device.name} ({device.mac_address})...")

        try:
            async with device:
                print("Reading historical data...")
                historical_data = await device.get_historical_data()

                if not historical_data:
                    print("No historical data available")
                    continue

                print(f"Found {len(historical_data)} historical entries")

                filename = f"flowercare_history_{device.mac_address.replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                with open(filename, "w", newline="") as csvfile:
                    fieldnames = [
                        "timestamp",
                        "temperature",
                        "brightness",
                        "moisture",
                        "conductivity",
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for entry in historical_data:
                        writer.writerow(
                            {
                                "timestamp": entry.timestamp.isoformat(),
                                "temperature": entry.sensor_data.temperature,
                                "brightness": entry.sensor_data.brightness,
                                "moisture": entry.sensor_data.moisture,
                                "conductivity": entry.sensor_data.conductivity,
                            }
                        )

                print(f"Historical data saved to {filename}")

                print("\nRecent entries:")
                for entry in historical_data[-5:]:
                    print(f"  {entry}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
