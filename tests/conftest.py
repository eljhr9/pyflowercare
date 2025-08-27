import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from bleak import BleakClient
from bleak.backends.device import BLEDevice

from flowercare import DeviceInfo, HistoricalEntry, SensorData


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_ble_device() -> Mock:
    """Create a mock BLE device."""
    device = Mock(spec=BLEDevice)
    device.name = "Flower care"
    device.address = "AA:BB:CC:DD:EE:FF"
    return device


@pytest.fixture
def mock_bleak_client() -> AsyncMock:
    """Create a mock Bleak client."""
    client = AsyncMock(spec=BleakClient)
    client.is_connected = True
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    client.read_gatt_char = AsyncMock()
    client.write_gatt_char = AsyncMock()
    return client


@pytest.fixture
def sample_sensor_data() -> SensorData:
    """Create sample sensor data."""
    return SensorData(
        temperature=23.5,
        brightness=150,
        moisture=65,
        conductivity=520,
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def sample_device_info() -> DeviceInfo:
    """Create sample device info."""
    return DeviceInfo(
        name="Flower care",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="3.3.6",
        battery_level=85,
    )


@pytest.fixture
def sample_historical_entry(sample_sensor_data: SensorData) -> HistoricalEntry:
    """Create sample historical entry."""
    return HistoricalEntry(timestamp=datetime(2023, 1, 1, 12, 0, 0), sensor_data=sample_sensor_data)


@pytest.fixture
def sensor_data_bytes() -> bytes:
    """Create sample sensor data bytes."""
    # Temperature: 23.5°C (235 / 10)
    # Unknown byte
    # Unknown byte
    # Brightness: 150 lux
    # Moisture: 65%
    # Conductivity: 520 µS/cm
    # Padding bytes
    return bytes(
        [
            235,
            0,  # temperature (235 = 23.5°C)
            0,  # unknown
            150,
            0,
            0,
            0,  # brightness (150 lux)
            65,  # moisture (65%)
            8,
            2,  # conductivity (520 µS/cm)
            0,
            0,
            0,
            0,
            0,
            0,
            0,  # padding
        ]
    )


@pytest.fixture
def device_info_bytes() -> bytes:
    """Create sample device info bytes."""
    # Battery level (85), unknown byte, firmware version "3.3.6"
    return bytes([85, 0]) + b"3.3.6\x00\x00\x00"


@pytest.fixture
def historical_count_bytes() -> bytes:
    """Create sample historical entry count bytes."""
    # 5 entries available
    return bytes([5, 0]) + b"\x00" * 14


@pytest.fixture
def historical_entry_bytes() -> bytes:
    """Create sample historical entry bytes."""
    # Timestamp: 1672574400 (2023-01-01 12:00:00 UTC)
    # Plus sensor data (needs to be at least 16 bytes)
    timestamp_bytes = (1672574400).to_bytes(4, byteorder="little")
    sensor_bytes = bytes(
        [
            235,
            0,  # temperature (23.5°C)
            0,  # unknown
            150,
            0,
            0,
            0,  # brightness (150 lux)
            65,  # moisture (65%)
            8,
            2,  # conductivity (520 µS/cm)
            0,
            0,
            0,
            0,
            0,
            0,  # padding to make 16 bytes
        ]
    )
    return timestamp_bytes + sensor_bytes
