import asyncio
import logging
import struct
from datetime import datetime, timedelta
from typing import List, Optional, Union

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice

from .constants import CHARACTERISTIC_UUIDS, COMMANDS, SERVICE_UUIDS
from .exceptions import ConnectionError, DataParsingError, DeviceError, TimeoutError
from .models import DeviceInfo, HistoricalEntry, SensorData

logger = logging.getLogger(__name__)


class FlowerCareDevice:
    """FlowerCare device client for Bluetooth communication."""

    def __init__(self, device: BLEDevice) -> None:
        self.device: BLEDevice = device
        self.client: Optional[BleakClient] = None
        self._connected: bool = False

    @property
    def mac_address(self) -> str:
        return self.device.address

    @property
    def name(self) -> str:
        return self.device.name or "Unknown"

    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None and self.client.is_connected

    async def connect(self, timeout: float = 10.0) -> None:
        try:
            self.client = BleakClient(self.device)
            await asyncio.wait_for(self.client.connect(), timeout=timeout)
            self._connected = True
            logger.info(f"Connected to {self.name} ({self.mac_address})")
        except asyncio.TimeoutError:
            raise TimeoutError(f"Connection timeout after {timeout}s")
        except BleakError as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            self._connected = False
            logger.info(f"Disconnected from {self.name}")

    async def __aenter__(self) -> "FlowerCareDevice":
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]
    ) -> None:
        await self.disconnect()

    async def _write_command(self, command: bytes) -> None:
        if not self.is_connected or self.client is None:
            raise ConnectionError("Device not connected")

        try:
            await self.client.write_gatt_char(CHARACTERISTIC_UUIDS["MODE_CHANGE"], command)
        except BleakError as e:
            raise DeviceError(f"Failed to write command: {e}")

    async def _read_characteristic(self, char_uuid: str) -> bytes:
        if not self.is_connected or self.client is None:
            raise ConnectionError("Device not connected")

        try:
            return await self.client.read_gatt_char(char_uuid)
        except BleakError as e:
            raise DeviceError(f"Failed to read characteristic: {e}")

    def _parse_sensor_data(self, data: bytes) -> SensorData:
        if len(data) < 16:
            raise DataParsingError(f"Invalid data length: {len(data)}")

        try:
            temperature = struct.unpack("<H", data[0:2])[0] / 10.0
            brightness = struct.unpack("<I", data[3:7])[0]
            moisture = data[7]
            conductivity = struct.unpack("<H", data[8:10])[0]

            return SensorData(
                temperature=temperature,
                brightness=brightness,
                moisture=moisture,
                conductivity=conductivity,
                timestamp=datetime.now(),
            )
        except (struct.error, ValueError) as e:
            raise DataParsingError(f"Failed to parse sensor data: {e}")

    def _parse_historical_sensor_data(self, data: bytes, device_timestamp: int) -> SensorData:
        """Parse historical sensor data with different format than real-time data."""
        if len(data) < 12:  # Historical data is shorter
            raise DataParsingError(f"Invalid historical data length: {len(data)}")

        try:
            # Historical data format: timestamp(4) + temperature(2) + skip(1) + brightness(3) + moisture(1) + conductivity(2)
            temperature = struct.unpack("<H", data[0:2])[0] / 10.0
            brightness = struct.unpack("<I", data[3:7])[0] if len(data) >= 7 else 0
            moisture = data[7] if len(data) > 7 else 0
            conductivity = struct.unpack("<H", data[8:10])[0] if len(data) >= 10 else 0

            return SensorData(
                temperature=temperature,
                brightness=brightness,
                moisture=moisture,
                conductivity=conductivity,
                timestamp=datetime.fromtimestamp(device_timestamp),
            )
        except (struct.error, ValueError) as e:
            raise DataParsingError(f"Failed to parse historical sensor data: {e}")

    async def read_sensor_data(self) -> SensorData:
        await self._write_command(COMMANDS["REALTIME_DATA"])
        await asyncio.sleep(0.1)

        data = await self._read_characteristic(CHARACTERISTIC_UUIDS["SENSOR_DATA"])
        return self._parse_sensor_data(data)

    async def get_device_info(self) -> DeviceInfo:
        try:
            name_data = await self._read_characteristic(CHARACTERISTIC_UUIDS["DEVICE_NAME"])
            name = name_data.decode("utf-8").strip("\x00")
        except:
            name = self.name

        try:
            firmware_data = await self._read_characteristic(
                CHARACTERISTIC_UUIDS["FIRMWARE_BATTERY"]
            )
            firmware_version = firmware_data[2:].decode("utf-8").strip("\x00")
            battery_level = firmware_data[0]
        except:
            firmware_version = None
            battery_level = None

        return DeviceInfo(
            name=name,
            mac_address=self.mac_address,
            firmware_version=firmware_version,
            battery_level=battery_level,
        )

    async def blink_led(self) -> None:
        await self._write_command(COMMANDS["BLINK_LED"])

    async def get_historical_data(self) -> List[HistoricalEntry]:
        # Check connection status first, before any try-catch
        if not self.client:
            raise ConnectionError("Device not connected")

        historical_entries: List[HistoricalEntry] = []

        try:
            logger.info("Starting historical data retrieval")

            # First, get epoch time from device
            epoch_time_data: bytes = await self._read_characteristic(
                CHARACTERISTIC_UUIDS["EPOCH_TIME"]
            )
            device_epoch_seconds: int = struct.unpack("<I", epoch_time_data)[0]
            logger.debug(f"Device epoch time: {device_epoch_seconds} seconds")

            await self.client.write_gatt_char(
                CHARACTERISTIC_UUIDS["HISTORY_CONTROL"], COMMANDS["HISTORY_READ_INIT"]
            )
            await asyncio.sleep(0.5)

            # Read the number of historical entries
            historical_entries_data: bytes = await self._read_characteristic(
                CHARACTERISTIC_UUIDS["HISTORY_DATA"]
            )

            if len(historical_entries_data) >= 2:
                num_entries: int = struct.unpack("<H", historical_entries_data[:2])[0]
                logger.info(f"Number of Historical Entries: {num_entries}")

                if num_entries > 0:
                    # Read each historical entry
                    for i in range(min(num_entries, 1000)):  # Limit to 1000 entries for safety
                        try:
                            # Prepare command to read specific entry
                            cmd_history_read_entry: bytearray = bytearray(
                                COMMANDS["HISTORY_READ_ENTRY"]
                            )
                            cmd_history_read_entry[1] = i & 0xFF  # Set entry index

                            await self.client.write_gatt_char(
                                CHARACTERISTIC_UUIDS["HISTORY_CONTROL"], cmd_history_read_entry
                            )

                            await asyncio.sleep(0.1)
                            historical_entry_data: bytes = await self._read_characteristic(
                                CHARACTERISTIC_UUIDS["HISTORY_DATA"]
                            )

                            if len(historical_entry_data) >= 16:
                                # Check if entry is empty (all 0xFF bytes indicates empty slot)
                                if all(b == 0xFF for b in historical_entry_data):
                                    continue

                                # Parse using the correct historical data format
                                device_timestamp: int = struct.unpack(
                                    "<I", historical_entry_data[0:4]
                                )[0]

                                # Skip entries with invalid timestamps (0 or 0xFFFFFFFF)
                                if device_timestamp == 0 or device_timestamp == 0xFFFFFFFF:
                                    continue

                                # Parse sensor data from historical format
                                temperature = (
                                    struct.unpack("<H", historical_entry_data[4:6])[0] / 10.0
                                )
                                brightness = struct.unpack(
                                    "<I", historical_entry_data[7:10] + b"\x00"
                                )[
                                    0
                                ]  # 3 bytes + padding
                                moisture = historical_entry_data[11]
                                conductivity = struct.unpack("<H", historical_entry_data[12:14])[0]

                                # Calculate time ago from device epoch
                                time_diff_seconds = device_epoch_seconds - device_timestamp
                                hours, remainder = divmod(time_diff_seconds, 3600)
                                minutes, seconds = divmod(remainder, 60)
                                time_ago = f"{hours}h {minutes}m {seconds}s"

                                # Create actual timestamp from device epoch and relative time
                                actual_timestamp = datetime.now() - timedelta(
                                    seconds=time_diff_seconds
                                )

                                sensor_data = SensorData(
                                    temperature=temperature,
                                    brightness=brightness,
                                    moisture=moisture,
                                    conductivity=conductivity,
                                    timestamp=actual_timestamp,
                                )

                                historical_entries.append(
                                    HistoricalEntry(
                                        timestamp=actual_timestamp, sensor_data=sensor_data
                                    )
                                )

                                logger.debug(
                                    f"Historical Entry #{i}: {{'time': '{time_ago}', 'Timestamp': {device_timestamp}, 'Temperature': {temperature}, 'Brightness': {brightness}, 'Moisture': {moisture}, 'Conductivity': {conductivity}}}"
                                )

                        except (DeviceError, struct.error, ValueError, OSError) as error:
                            logger.debug(f"Error reading entry {i}: {error}")
                            continue

                else:
                    logger.info("Device reports 0 historical entries")
            else:
                logger.debug(
                    f"Invalid response when reading entry count: {len(historical_entries_data)} bytes"
                )

        except Exception as e:
            logger.info(
                f"Historical data feature not available or not supported by this device: {e}"
            )

        logger.info(f"Historical data retrieval complete. Found {len(historical_entries)} entries")
        return historical_entries
