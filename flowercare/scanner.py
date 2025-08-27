import asyncio
import logging
from typing import AsyncGenerator, Callable, List, Optional, Set

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .constants import ADVERTISEMENT_UUID, DEVICE_NAME_PREFIX
from .device import FlowerCareDevice
from .exceptions import TimeoutError

logger = logging.getLogger(__name__)


class FlowerCareScanner:
    """Scanner for discovering FlowerCare devices via Bluetooth."""

    def __init__(self) -> None:
        self.scanner: BleakScanner = BleakScanner()

    @staticmethod
    def _is_flowercare_device(device: BLEDevice, advertisement_data: AdvertisementData) -> bool:
        if device.name and DEVICE_NAME_PREFIX.lower() in device.name.lower():
            return True

        if advertisement_data.service_uuids:
            service_uuids = advertisement_data.service_uuids
            if ADVERTISEMENT_UUID.lower() in [uuid.lower() for uuid in service_uuids]:
                return True

        return False

    async def scan_for_devices(self, timeout: float = 10.0) -> List[FlowerCareDevice]:
        devices: List[FlowerCareDevice] = []
        found_addresses: Set[str] = set()

        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData) -> None:
            if (
                self._is_flowercare_device(device, advertisement_data)
                and device.address not in found_addresses
            ):
                found_addresses.add(device.address)
                devices.append(FlowerCareDevice(device))
                logger.info(f"Found FlowerCare device: {device.name} ({device.address})")

        try:
            async with BleakScanner(detection_callback) as scanner:
                await asyncio.sleep(timeout)

        except asyncio.TimeoutError:
            raise TimeoutError(f"Scan timeout after {timeout}s")

        return devices

    async def find_device_by_mac(
        self, mac_address: str, timeout: float = 10.0
    ) -> Optional[FlowerCareDevice]:
        mac_address = mac_address.lower()

        devices = await self.scan_for_devices(timeout)
        for device in devices:
            if device.mac_address.lower() == mac_address:
                return device

        return None

    async def scan_continuously(
        self, callback: Callable[[FlowerCareDevice], None], timeout: Optional[float] = None
    ) -> None:
        found_devices: Set[str] = set()

        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData) -> None:
            if (
                self._is_flowercare_device(device, advertisement_data)
                and device.address not in found_devices
            ):
                found_devices.add(device.address)
                flowercare_device: FlowerCareDevice = FlowerCareDevice(device)
                callback(flowercare_device)

        async with BleakScanner(detection_callback) as scanner:
            if timeout:
                await asyncio.sleep(timeout)
            else:
                while True:
                    await asyncio.sleep(1.0)

    async def scan_stream(
        self, timeout: Optional[float] = None
    ) -> AsyncGenerator[FlowerCareDevice, None]:
        found_devices: Set[str] = set()
        device_queue: asyncio.Queue[FlowerCareDevice] = asyncio.Queue()

        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData) -> None:
            if (
                self._is_flowercare_device(device, advertisement_data)
                and device.address not in found_devices
            ):
                found_devices.add(device.address)
                flowercare_device: FlowerCareDevice = FlowerCareDevice(device)
                device_queue.put_nowait(flowercare_device)

        scan_task: Optional[asyncio.Task[None]] = None
        try:
            async with BleakScanner(detection_callback) as scanner:
                if timeout:
                    scan_task = asyncio.create_task(asyncio.sleep(timeout))

                while True:
                    try:
                        device: FlowerCareDevice = await asyncio.wait_for(
                            device_queue.get(), timeout=1.0
                        )
                        yield device
                    except asyncio.TimeoutError:
                        if scan_task and scan_task.done():
                            break
                        continue

        except asyncio.CancelledError:
            if scan_task:
                scan_task.cancel()
            raise
