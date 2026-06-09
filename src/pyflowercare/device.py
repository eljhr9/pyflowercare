import asyncio
import logging
import struct
from datetime import datetime, timedelta
from typing import List, Optional

from bleak import BleakClient, BleakError
from bleak.backends.device import BLEDevice

from .constants import (
    CHARACTERISTIC_UUIDS,
    COMMANDS,
    MAX_HISTORY_ENTRIES,
    MAX_HISTORY_RECONNECTS,
    MAX_VALID_BRIGHTNESS,
    MAX_VALID_CONDUCTIVITY,
    RECONNECT_SETTLE_DELAY,
)
from .exceptions import ConnectionError, DataParsingError, DeviceError, TimeoutError
from .models import DeviceInfo, HistoricalEntry, SensorData

logger = logging.getLogger(__name__)


class FlowerCareDevice:
    """FlowerCare device client for Bluetooth communication."""

    def __init__(self, device: BLEDevice) -> None:
        self.device: BLEDevice = device
        self.client: Optional[BleakClient] = None
        self._connected: bool = False
        self._cached_name: Optional[str] = None
        self._last_history_complete: bool = True

    @property
    def mac_address(self) -> str:
        return self.device.address

    @property
    def name(self) -> str:
        if self._cached_name:
            return self._cached_name
        return self.device.name or "Unknown"

    @property
    def last_history_complete(self) -> bool:
        """Whether the most recent get_historical_data() call ran to completion.

        False indicates the call was interrupted (e.g. the connection dropped
        mid-read) and returned only the entries collected before the failure.
        """
        return self._last_history_complete

    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None and self.client.is_connected

    async def connect(self, timeout: float = 10.0) -> None:
        try:
            # Check if device is a proper BLEDevice from bleak or our custom DirectBLEDevice
            # Proper BLEDevices are instances of the BLEDevice class from bleak
            if isinstance(self.device, BLEDevice):
                # This is a proper BLEDevice from bleak
                self.client = BleakClient(self.device)
            else:
                # This is our custom duck-typed DirectBLEDevice from
                # find_device_by_address; connect via its address string. mypy
                # sees self.device as always-BLEDevice and flags this dead.
                self.client = BleakClient(self.device.address)  # type: ignore[unreachable]
            await asyncio.wait_for(self.client.connect(), timeout=timeout)
            self._connected = True

            # Best-effort: read the device name from its GATT characteristic.
            # This is an optional optimization; any failure falls back to the
            # advertised BLE name, so it must never break the connection.
            if not self._cached_name:
                try:
                    name_data = await self.client.read_gatt_char(
                        CHARACTERISTIC_UUIDS["DEVICE_NAME"]
                    )
                    self._cached_name = name_data.decode("utf-8").strip("\x00")
                except Exception:
                    pass

            logger.info(f"Connected to {self.name} ({self.mac_address})")
        except asyncio.TimeoutError:
            # Ensure cleanup on timeout
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass
                self.client = None
            self._connected = False
            raise TimeoutError(f"Connection timeout after {timeout}s")
        except BleakError as e:
            # Ensure cleanup on error
            if self.client:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass
                self.client = None
            self._connected = False
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        if self.client:
            try:
                if self.client.is_connected:
                    await self.client.disconnect()
            except BleakError as e:
                # Device may already be disconnected
                logger.debug(f"Disconnect error (device may already be disconnected): {e}")
            finally:
                self._connected = False

    async def __aenter__(self) -> "FlowerCareDevice":
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[object]
    ) -> None:
        # Always attempt to disconnect, even if an exception occurred
        try:
            await self.disconnect()
        except Exception as e:
            # Log but don't raise - we don't want to mask the original exception
            logger.debug(f"Error during context manager disconnect: {e}")

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
            # Temperature is a signed int16 (negative readings are valid)
            temperature = struct.unpack("<h", data[0:2])[0] / 10.0
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

    async def read_sensor_data(self) -> SensorData:
        await self._write_command(COMMANDS["REALTIME_DATA"])
        await asyncio.sleep(0.1)

        data = await self._read_characteristic(CHARACTERISTIC_UUIDS["SENSOR_DATA"])
        return self._parse_sensor_data(data)

    async def get_device_info(self) -> DeviceInfo:
        try:
            name_data = await self._read_characteristic(CHARACTERISTIC_UUIDS["DEVICE_NAME"])
            name = name_data.decode("utf-8").strip("\x00")
            # Cache the name for future use
            if name and not self._cached_name:
                self._cached_name = name
        except (DeviceError, ConnectionError, UnicodeDecodeError):
            name = self.name

        try:
            firmware_data = await self._read_characteristic(
                CHARACTERISTIC_UUIDS["FIRMWARE_BATTERY"]
            )
            firmware_version = firmware_data[2:].decode("utf-8").strip("\x00")
            battery_level = firmware_data[0]
        except (DeviceError, ConnectionError, UnicodeDecodeError, IndexError):
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

    async def _read_device_epoch(self) -> int:
        """Read the device's internal clock (seconds since boot).

        Uses direct client calls so a mid-operation disconnect surfaces as a
        raw BleakError, letting the init phase reconnect and retry.
        """
        if self.client is None or not self.client.is_connected:
            raise ConnectionError("Device not connected")
        data = await self.client.read_gatt_char(CHARACTERISTIC_UUIDS["EPOCH_TIME"])
        return int(struct.unpack("<I", data)[0])

    async def _begin_history_read(self) -> int:
        """Enter history-read mode and return the reported entry count.

        Uses direct client calls so a mid-operation disconnect surfaces as a
        raw BleakError (which the caller treats as a reconnect trigger).
        """
        if self.client is None or not self.client.is_connected:
            raise ConnectionError("Device not connected")
        await self.client.write_gatt_char(
            CHARACTERISTIC_UUIDS["HISTORY_CONTROL"], COMMANDS["HISTORY_READ_INIT"]
        )
        await asyncio.sleep(0.5)
        data = await self.client.read_gatt_char(CHARACTERISTIC_UUIDS["HISTORY_DATA"])
        if len(data) < 2:
            logger.debug(f"Invalid entry-count response: {len(data)} bytes")
            return 0
        return int(struct.unpack("<H", data[:2])[0])

    async def _read_history_entry(self, index: int) -> bytes:
        """Select and read a single raw 16-byte history record by index.

        The select command is 0xA1 followed by the index as a 2-byte
        little-endian value (e.g. entry 256 -> 0xA1 0x00 0x01). Uses direct
        client calls so a disconnect raises BleakError rather than being
        wrapped, letting the retrieval loop reconnect and resume.
        """
        if self.client is None or not self.client.is_connected:
            raise ConnectionError("Device disconnected during history read")
        cmd = bytearray(COMMANDS["HISTORY_READ_ENTRY"])
        cmd[1:3] = index.to_bytes(2, "little")
        await self.client.write_gatt_char(CHARACTERISTIC_UUIDS["HISTORY_CONTROL"], cmd)
        return bytes(await self.client.read_gatt_char(CHARACTERISTIC_UUIDS["HISTORY_DATA"]))

    async def _reconnect_device(self) -> None:
        """Disconnect and reconnect, pausing for the BLE stack to settle.

        Reconnecting immediately after a drop typically times out, so we let the
        peripheral re-advertise and the old link release first.
        """
        try:
            await self.disconnect()
        except Exception:
            pass
        await asyncio.sleep(RECONNECT_SETTLE_DELAY)
        await self.connect()

    async def _resume_history_read(self) -> None:
        """Reconnect after a mid-retrieval drop and re-enter history-read mode."""
        await self._reconnect_device()
        await self._begin_history_read()  # re-init; the re-read entry count is ignored

    def _parse_history_entry(
        self,
        raw: bytes,
        device_epoch_seconds: int,
        reference_time: Optional[datetime] = None,
    ) -> Optional[HistoricalEntry]:
        """Parse one raw 16-byte history record.

        Returns None for empty or incompletely-written slots (the device fills
        unmeasured bytes with 0xFF). Brightness/conductivity values above the
        sensor's documented range are reported as None ("not measured") rather
        than as nonsense sentinel numbers.

        `reference_time` anchors the relative device timestamps to wall-clock
        time; pass a single value captured once per retrieval so every entry
        shares the same reference and timestamps don't drift across a long read.
        """
        if len(raw) < 16 or all(b == 0xFF for b in raw):
            return None

        device_timestamp = int(struct.unpack("<I", raw[0:4])[0])
        if device_timestamp in (0, 0xFFFFFFFF):
            return None  # empty slot

        # A valid timestamp with an all-zero sensor payload is a slot the device
        # reserved but never wrote a reading into -- skip it. (Genuine readings
        # that merely happen to log 0.0C keep non-zero light/moisture/conductivity
        # bytes, so this only drops truly-empty slots.)
        if not any(raw[4:16]):
            return None

        # A moisture byte of 0xFF (255, impossible as a percentage) marks a slot
        # whose sensor payload was never written -- skip it entirely.
        moisture = raw[11]
        if moisture == 0xFF:
            return None

        # Temperature is a signed int16 (negative readings are valid).
        temperature = struct.unpack("<h", raw[4:6])[0] / 10.0
        brightness = struct.unpack("<I", raw[7:10] + b"\x00")[0]  # 3-byte LE + padding
        conductivity = struct.unpack("<H", raw[12:14])[0]

        reference = reference_time if reference_time is not None else datetime.now()
        actual_timestamp = reference - timedelta(seconds=device_epoch_seconds - device_timestamp)
        sensor_data = SensorData(
            temperature=temperature,
            brightness=brightness if brightness <= MAX_VALID_BRIGHTNESS else None,
            moisture=moisture,
            conductivity=conductivity if conductivity <= MAX_VALID_CONDUCTIVITY else None,
            timestamp=actual_timestamp,
        )
        return HistoricalEntry(timestamp=actual_timestamp, sensor_data=sensor_data)

    async def get_historical_data(self) -> List[HistoricalEntry]:
        # Check connection status first, before any try-catch
        if not self.is_connected:
            raise ConnectionError("Device not connected")

        historical_entries: List[HistoricalEntry] = []
        # Reset completion flag; set to True only if retrieval runs to the end.
        # Callers can inspect `last_history_complete` to detect interrupted reads.
        self._last_history_complete = False

        try:
            logger.info("Starting historical data retrieval")

            # Anchor all entries to one wall-clock reference so timestamps stay
            # consistent even if the read spans reconnects.
            reference_time = datetime.now()

            # Init phase (epoch + enter history mode) with reconnect-resume:
            # some devices drop right after connecting, before the entry loop.
            init_reconnects = 0
            while True:
                try:
                    device_epoch_seconds = await self._read_device_epoch()
                    logger.debug(f"Device epoch time: {device_epoch_seconds} seconds")
                    num_entries = await self._begin_history_read()
                    break
                except (ConnectionError, BleakError, TimeoutError) as error:
                    if init_reconnects >= MAX_HISTORY_RECONNECTS:
                        logger.warning(
                            f"Giving up initializing history read after "
                            f"{init_reconnects} reconnect attempt(s): {error}"
                        )
                        return historical_entries
                    init_reconnects += 1
                    logger.warning(
                        f"Connection lost initializing history read; reconnecting "
                        f"({init_reconnects}/{MAX_HISTORY_RECONNECTS}): {error}"
                    )
                    try:
                        await self._reconnect_device()
                    except (ConnectionError, BleakError, TimeoutError) as reconnect_err:
                        logger.warning(
                            f"Reconnect failed during history init: {reconnect_err}; "
                            f"returning no entries"
                        )
                        return historical_entries

            logger.info(f"Number of Historical Entries: {num_entries}")

            if num_entries <= 0:
                logger.info("Device reports 0 historical entries")
            else:
                total = min(num_entries, MAX_HISTORY_ENTRIES)
                if num_entries > MAX_HISTORY_ENTRIES:
                    logger.warning(
                        f"Device reports {num_entries} entries; reading the first {total}"
                    )

                i = 0
                reconnects = 0
                while i < total:
                    try:
                        raw = await self._read_history_entry(i)
                        logger.debug(f"Entry #{i} raw: {raw.hex()}")
                        entry = self._parse_history_entry(raw, device_epoch_seconds, reference_time)
                        if entry is not None:
                            historical_entries.append(entry)
                            logger.debug(f"Historical Entry #{i}: {entry.sensor_data}")
                        i += 1
                        # Healthy read - the link is alive again, so refresh the
                        # reconnect budget (it caps *consecutive* drops, letting a
                        # large history that drops periodically still drain fully).
                        reconnects = 0
                    except (DeviceError, struct.error, ValueError, OSError) as error:
                        # A single unparseable entry - skip it and move on.
                        logger.debug(f"Skipping unparseable entry {i}: {error}")
                        i += 1
                    except (ConnectionError, BleakError, TimeoutError) as error:
                        # Connection dropped mid-retrieval: reconnect and resume
                        # from the same index without losing collected entries.
                        if reconnects >= MAX_HISTORY_RECONNECTS:
                            logger.warning(
                                f"Giving up after {reconnects} reconnect attempt(s) at "
                                f"entry {i}/{total}; returning {len(historical_entries)} "
                                f"partial entries"
                            )
                            return historical_entries
                        reconnects += 1
                        logger.warning(
                            f"Connection lost at entry {i}/{total}; reconnecting and "
                            f"resuming ({reconnects}/{MAX_HISTORY_RECONNECTS}): {error}"
                        )
                        try:
                            await self._resume_history_read()
                        except (ConnectionError, BleakError, TimeoutError) as reconnect_err:
                            # Reconnect itself failed - a clean partial result,
                            # not an unexpected error. last_history_complete stays False.
                            logger.warning(
                                f"Reconnect failed at entry {i}/{total}: {reconnect_err}; "
                                f"returning {len(historical_entries)} partial entries"
                            )
                            return historical_entries

        except (ConnectionError, BleakError) as e:
            # Connection lost (and not recoverable) during retrieval. Return
            # whatever was collected; the caller can detect the partial read
            # via last_history_complete.
            logger.error(f"Connection lost during historical data retrieval: {e}")
            logger.info(
                f"Retrieval interrupted; returning {len(historical_entries)} partial entries"
            )
            return historical_entries
        except (struct.error, ValueError) as e:
            # Data parsing error - device may not support historical data
            logger.warning(
                f"Historical data parsing failed - device may not support this feature: {e}"
            )
            return historical_entries
        except Exception as e:
            logger.error(f"Unexpected error during historical data retrieval: {e}")
            return historical_entries

        self._last_history_complete = True
        valid = len(historical_entries)
        # `num_entries` is the slot count the device reports; many slots can be
        # empty/unwritten (all-zero or 0xFF) and are skipped, so valid <= reported.
        read = min(num_entries, MAX_HISTORY_ENTRIES)
        logger.info(
            f"Historical data retrieval complete: {valid} valid entries "
            f"({num_entries} reported, {read - valid} empty/unwritten slots skipped)"
        )
        return historical_entries
