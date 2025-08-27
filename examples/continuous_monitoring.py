#!/usr/bin/env python3
import asyncio
import signal
import sys
from datetime import datetime

sys.path.insert(0, "../")

from flowercare import FlowerCareDevice, FlowerCareScanner, setup_logging


class FlowerCareMonitor:
    def __init__(self):
        self.running = True
        self.devices = []

    async def monitor_device(self, device: FlowerCareDevice):
        print(f"Starting monitoring for {device.name} ({device.mac_address})")

        while self.running:
            try:
                async with device:
                    while self.running:
                        sensor_data = await device.read_sensor_data()
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"[{timestamp}] {device.name}: {sensor_data}")

                        await asyncio.sleep(60)

            except Exception as e:
                print(f"Error monitoring {device.name}: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False


async def main():
    setup_logging("INFO")

    monitor = FlowerCareMonitor()

    def signal_handler(signum, frame):
        print("\nShutting down...")
        monitor.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    scanner = FlowerCareScanner()

    print("Scanning for FlowerCare devices...")
    devices = await scanner.scan_for_devices(timeout=10.0)

    if not devices:
        print("No FlowerCare devices found")
        return

    print(f"Found {len(devices)} device(s), starting monitoring...")

    tasks = []
    for device in devices:
        task = asyncio.create_task(monitor.monitor_device(device))
        tasks.append(task)

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
