import asyncio
import logging
import re
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
        # A fresh BleakScanner is created per scan operation (see scan_* methods).
        # No scanner is instantiated here to avoid initializing the BLE backend
        # before it is actually needed.
        pass

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

    async def find_device_by_address(
        self, device_address: str, timeout: float = 10.0
    ) -> Optional[FlowerCareDevice]:
        """Find a FlowerCare device by MAC or UUID-like address without scanning.

        Args:
            device_address: MAC (e.g., "C4:7C:8D:12:34:56") or UUID-like identifier
                            (e.g., "19B586E3-3E4F-917B-5ED4-DF0C464B0C3B")
            timeout: Timeout parameter (kept for compatibility but not used)

        Returns:
            FlowerCareDevice instance or None if address is invalid
        """

        if not device_address:
            return None

        normalized = device_address.strip().upper()

        # Validate MAC format (XX:XX:XX:XX:XX:XX)
        mac_pattern = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")
        # Validate UUID format (8-4-4-4-12 hex digits)
        uuid_pattern = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$")

        if not (mac_pattern.match(normalized) or uuid_pattern.match(normalized)):
            return None

        # Create a minimal BLEDevice-like object for direct connection
        class DirectBLEDevice:
            def __init__(self, address: str):
                self.address = address
                self.name: Optional[str] = None

        try:
            direct_device = DirectBLEDevice(normalized)
            return FlowerCareDevice(direct_device)  # type: ignore[arg-type]
        except Exception:
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
