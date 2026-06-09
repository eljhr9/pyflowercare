import struct
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bleak import BleakError
from bleak.backends.device import BLEDevice

from pyflowercare.device import FlowerCareDevice
from pyflowercare.exceptions import ConnectionError, DataParsingError, DeviceError, TimeoutError
from pyflowercare.models import DeviceInfo, HistoricalEntry, SensorData


class TestFlowerCareDevice:
    """Test FlowerCareDevice class."""

    def test_device_initialization(self, mock_ble_device):
        """Test device initialization."""
        device = FlowerCareDevice(mock_ble_device)

        assert device.device == mock_ble_device
        assert device.client is None
        assert device._connected is False

    def test_properties(self, mock_ble_device):
        """Test device properties."""
        device = FlowerCareDevice(mock_ble_device)

        assert device.mac_address == "AA:BB:CC:DD:EE:FF"
        assert device.name == "Flower care"
        assert device.is_connected is False

        # Test with no name
        mock_ble_device.name = None
        assert device.name == "Unknown"

    @pytest.mark.asyncio
    async def test_connect_success(self, mock_ble_device, mock_bleak_client):
        """Test successful connection."""
        device = FlowerCareDevice(mock_ble_device)

        with patch("pyflowercare.device.BleakClient", return_value=mock_bleak_client):
            await device.connect()

        assert device._connected is True
        assert device.client == mock_bleak_client
        mock_bleak_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_timeout(self, mock_ble_device, mock_bleak_client):
        """Test connection timeout."""
        device = FlowerCareDevice(mock_ble_device)
        mock_bleak_client.connect.side_effect = BleakError("Connection failed")

        with patch("pyflowercare.device.BleakClient", return_value=mock_bleak_client):
            with pytest.raises(ConnectionError) as exc_info:
                await device.connect()

        assert "Failed to connect" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect(self, mock_ble_device, mock_bleak_client):
        """Test disconnection."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        await device.disconnect()

        mock_bleak_client.disconnect.assert_called_once()
        assert device._connected is False

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_ble_device, mock_bleak_client):
        """Test async context manager."""
        device = FlowerCareDevice(mock_ble_device)

        with patch("pyflowercare.device.BleakClient", return_value=mock_bleak_client):
            async with device as ctx_device:
                assert ctx_device is device
                assert device._connected is True

        mock_bleak_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_command_not_connected(self, mock_ble_device):
        """Test writing command when not connected."""
        device = FlowerCareDevice(mock_ble_device)

        with pytest.raises(ConnectionError) as exc_info:
            await device._write_command(b"\xa0\x1f")

        assert "Device not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_write_command_success(self, mock_ble_device, mock_bleak_client):
        """Test successful command writing."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        await device._write_command(b"\xa0\x1f")

        mock_bleak_client.write_gatt_char.assert_called_once()

    @pytest.mark.asyncio
    async def test_write_command_bleak_error(self, mock_ble_device, mock_bleak_client):
        """Test command writing with Bleak error."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True
        mock_bleak_client.write_gatt_char.side_effect = BleakError("Write failed")

        with pytest.raises(DeviceError) as exc_info:
            await device._write_command(b"\xa0\x1f")

        assert "Failed to write command" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_characteristic_not_connected(self, mock_ble_device):
        """Test reading characteristic when not connected."""
        device = FlowerCareDevice(mock_ble_device)

        with pytest.raises(ConnectionError) as exc_info:
            await device._read_characteristic("test-uuid")

        assert "Device not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_characteristic_success(self, mock_ble_device, mock_bleak_client):
        """Test successful characteristic reading."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True
        mock_bleak_client.read_gatt_char.return_value = b"test data"

        result = await device._read_characteristic("test-uuid")

        assert result == b"test data"
        mock_bleak_client.read_gatt_char.assert_called_once_with("test-uuid")

    @pytest.mark.asyncio
    async def test_read_characteristic_bleak_error(self, mock_ble_device, mock_bleak_client):
        """Test characteristic reading with Bleak error."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True
        mock_bleak_client.read_gatt_char.side_effect = BleakError("Read failed")

        with pytest.raises(DeviceError) as exc_info:
            await device._read_characteristic("test-uuid")

        assert "Failed to read characteristic" in str(exc_info.value)

    def test_parse_sensor_data_success(self, mock_ble_device, sensor_data_bytes):
        """Test successful sensor data parsing."""
        device = FlowerCareDevice(mock_ble_device)

        result = device._parse_sensor_data(sensor_data_bytes)

        assert isinstance(result, SensorData)
        assert result.temperature == 23.5
        assert result.brightness == 150
        assert result.moisture == 65
        assert result.conductivity == 520
        assert result.timestamp is not None

    def test_parse_sensor_data_invalid_length(self, mock_ble_device):
        """Test sensor data parsing with invalid length."""
        device = FlowerCareDevice(mock_ble_device)

        with pytest.raises(DataParsingError) as exc_info:
            device._parse_sensor_data(b"short")

        assert "Invalid data length" in str(exc_info.value)

    def test_parse_sensor_data_validation_error(self, mock_ble_device):
        """Test sensor data parsing with Pydantic validation error."""
        device = FlowerCareDevice(mock_ble_device)
        # Provide bytes that will cause Pydantic validation to fail
        bad_data = b"x" * 16  # 16 bytes but invalid values for model

        with pytest.raises(DataParsingError) as exc_info:
            device._parse_sensor_data(bad_data)

        assert "Failed to parse sensor data" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_sensor_data(self, mock_ble_device, mock_bleak_client, sensor_data_bytes):
        """Test reading sensor data."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True
        mock_bleak_client.read_gatt_char.return_value = sensor_data_bytes

        result = await device.read_sensor_data()

        assert isinstance(result, SensorData)
        assert result.temperature == 23.5
        assert mock_bleak_client.write_gatt_char.call_count == 1
        assert mock_bleak_client.read_gatt_char.call_count == 1

    @pytest.mark.asyncio
    async def test_get_device_info_full(
        self, mock_ble_device, mock_bleak_client, device_info_bytes
    ):
        """Test getting complete device info."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        # Mock the characteristic reads
        def read_side_effect(uuid):
            if "2a00" in uuid:  # DEVICE_NAME
                return b"Flower care\x00\x00"
            elif "1a02" in uuid:  # FIRMWARE_BATTERY
                return device_info_bytes
            return b""

        mock_bleak_client.read_gatt_char.side_effect = read_side_effect

        result = await device.get_device_info()

        assert isinstance(result, DeviceInfo)
        assert result.name == "Flower care"
        assert result.mac_address == "AA:BB:CC:DD:EE:FF"
        assert result.firmware_version == "3.3.6"
        assert result.battery_level == 85

    @pytest.mark.asyncio
    async def test_get_device_info_fallback(self, mock_ble_device, mock_bleak_client):
        """Test getting device info with fallbacks."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        # Mock read failures
        mock_bleak_client.read_gatt_char.side_effect = BleakError("Read failed")

        result = await device.get_device_info()

        assert isinstance(result, DeviceInfo)
        assert result.name == "Flower care"  # Fallback to device.name
        assert result.mac_address == "AA:BB:CC:DD:EE:FF"
        assert result.firmware_version is None
        assert result.battery_level is None

    @pytest.mark.asyncio
    async def test_blink_led(self, mock_ble_device, mock_bleak_client):
        """Test LED blinking."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        await device.blink_led()

        mock_bleak_client.write_gatt_char.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_historical_data_no_entries(self, mock_ble_device, mock_bleak_client):
        """Test getting historical data with no entries."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        # Mock epoch time (first read) and zero entries response (second read)
        epoch_time_bytes = (1672574400).to_bytes(4, byteorder="little")  # Mock epoch time
        zero_entries_bytes = bytes([0, 0]) + b"\x00" * 14

        mock_bleak_client.read_gatt_char.side_effect = [
            epoch_time_bytes,  # First read: epoch time
            zero_entries_bytes,  # Second read: historical entries count
        ]

        result = await device.get_historical_data()

        assert isinstance(result, list)
        assert len(result) == 0
        assert mock_bleak_client.write_gatt_char.call_count >= 1  # Init command

    @pytest.mark.asyncio
    async def test_get_historical_data_with_entries(
        self, mock_ble_device, mock_bleak_client, historical_count_bytes, historical_entry_bytes
    ):
        """Test getting historical data with entries."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        # Mock epoch time and responses
        epoch_time_bytes = (1672580000).to_bytes(4, byteorder="little")  # Mock epoch time
        read_responses = [epoch_time_bytes, historical_count_bytes] + [historical_entry_bytes] * 5
        mock_bleak_client.read_gatt_char.side_effect = read_responses

        result = await device.get_historical_data()

        assert isinstance(result, list)
        assert len(result) == 5

        for entry in result:
            assert isinstance(entry, HistoricalEntry)
            assert isinstance(entry.sensor_data, SensorData)
            assert entry.timestamp is not None

    @pytest.mark.asyncio
    async def test_get_historical_data_connection_error(self, mock_ble_device):
        """Test getting historical data when not connected."""
        device = FlowerCareDevice(mock_ble_device)

        with pytest.raises(ConnectionError) as exc_info:
            await device.get_historical_data()

        assert "Device not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_historical_data_invalid_response(self, mock_ble_device, mock_bleak_client):
        """Test getting historical data with invalid response."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        # Mock epoch time first, then invalid response (too short)
        epoch_time_bytes = (1672574400).to_bytes(4, byteorder="little")
        mock_bleak_client.read_gatt_char.side_effect = [
            epoch_time_bytes,  # First read: epoch time
            b"\x00",  # Second read: invalid response (too short)
        ]

        result = await device.get_historical_data()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_historical_data_exception_handling(self, mock_ble_device, mock_bleak_client):
        """Test historical data exception handling."""
        device = FlowerCareDevice(mock_ble_device)
        device.client = mock_bleak_client
        device._connected = True

        # Mock write failure
        mock_bleak_client.write_gatt_char.side_effect = BleakError("Write failed")

        result = await device.get_historical_data()

        assert isinstance(result, list)
        assert len(result) == 0


class TestParseHistoryEntry:
    """Parse real 16-byte history records captured from hardware.

    Byte patterns are taken verbatim from a live FlowerCare (firmware 3.3.6).
    Device epoch for these captures was 256895 seconds.
    """

    EPOCH = 256895

    def _device(self, mock_ble_device):
        return FlowerCareDevice(mock_ble_device)

    def test_fully_valid_entry(self, mock_ble_device):
        """A complete record parses all fields (incl. signed temperature)."""
        device = self._device(mock_ble_device)
        raw = bytes.fromhex("90210300d600031100000004310182ff")
        entry = device._parse_history_entry(raw, self.EPOCH)

        assert entry is not None
        assert entry.sensor_data.temperature == 21.4
        assert entry.sensor_data.brightness == 17
        assert entry.sensor_data.moisture == 4
        assert entry.sensor_data.conductivity == 305

    def test_unmeasured_conductivity_becomes_none(self, mock_ble_device):
        """Valid reading with a 0xFFFF conductivity sentinel -> conductivity None."""
        device = self._device(mock_ble_device)
        raw = bytes.fromhex("70e60300090103af06000012ffffffff")
        entry = device._parse_history_entry(raw, self.EPOCH)

        assert entry is not None
        assert entry.sensor_data.temperature == 26.5
        assert entry.sensor_data.brightness == 1711
        assert entry.sensor_data.moisture == 18
        assert entry.sensor_data.conductivity is None  # 0xFFFF sentinel

    def test_implausible_brightness_becomes_none(self, mock_ble_device):
        """Out-of-range brightness sentinel -> brightness None, other fields kept."""
        device = self._device(mock_ble_device)
        raw = bytes.fromhex("a02f0300dc0003a00084ff1fffffffff")
        entry = device._parse_history_entry(raw, self.EPOCH)

        assert entry is not None
        assert entry.sensor_data.temperature == 22.0
        assert entry.sensor_data.moisture == 31
        assert entry.sensor_data.brightness is None  # > documented max lux
        assert entry.sensor_data.conductivity is None

    def test_incomplete_slot_skipped(self, mock_ble_device):
        """A slot with moisture=0xFF is incompletely written -> skipped (None)."""
        device = self._device(mock_ble_device)
        raw = bytes.fromhex("60d803000bd5afb3ffffffffffffffff")
        assert device._parse_history_entry(raw, self.EPOCH) is None

    def test_all_ff_slot_skipped(self, mock_ble_device):
        device = self._device(mock_ble_device)
        assert device._parse_history_entry(b"\xff" * 16, self.EPOCH) is None

    def test_all_zero_slot_skipped(self, mock_ble_device):
        """Empty slots (timestamp 0) are skipped."""
        device = self._device(mock_ble_device)
        assert device._parse_history_entry(b"\x00" * 16, self.EPOCH) is None

    def test_zero_payload_with_timestamp_skipped(self, mock_ble_device):
        """A valid timestamp but all-zero payload is a reserved-but-empty slot."""
        device = self._device(mock_ble_device)
        raw = bytes.fromhex("90210300") + b"\x00" * 12  # ts=205200, payload all zero
        assert device._parse_history_entry(raw, self.EPOCH) is None

    def test_real_zero_celsius_reading_kept(self, mock_ble_device):
        """A genuine 0.0C reading with non-zero other fields is NOT dropped."""
        device = self._device(mock_ble_device)
        # ts, temp=0x0000 (0.0C), light=28, moisture=24, cond=153 (real payload)
        raw = bytes.fromhex("109203000000031c0000001899000000")
        entry = device._parse_history_entry(raw, self.EPOCH)

        assert entry is not None
        assert entry.sensor_data.temperature == 0.0
        assert entry.sensor_data.moisture == 24
        assert entry.sensor_data.conductivity == 153

    def test_short_buffer_skipped(self, mock_ble_device):
        device = self._device(mock_ble_device)
        assert device._parse_history_entry(b"\x01\x02\x03", self.EPOCH) is None

    def test_negative_temperature(self, mock_ble_device):
        """Signed temperature handles sub-zero readings (e.g. -5.0C)."""
        device = self._device(mock_ble_device)
        # ts=205200, temp=0xFFCE (-50 -> -5.0C), light=17, moisture=4, cond=305
        raw = bytes.fromhex("90210300ceff031100000004310182ff")
        entry = device._parse_history_entry(raw, self.EPOCH)

        assert entry is not None
        assert entry.sensor_data.temperature == -5.0
