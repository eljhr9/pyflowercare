from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from flowercare import (
    DeviceInfo,
    FlowerCareDevice,
    FlowerCareScanner,
    HistoricalEntry,
    SensorData,
    setup_logging,
)


class TestIntegration:
    """Integration tests for FlowerCare library."""

    def test_library_imports(self):
        """Test that all main classes can be imported."""
        # This test verifies that the __init__.py exports work correctly
        assert FlowerCareDevice is not None
        assert FlowerCareScanner is not None
        assert SensorData is not None
        assert DeviceInfo is not None
        assert HistoricalEntry is not None
        assert setup_logging is not None

    @pytest.mark.asyncio
    async def test_scan_and_connect_workflow(self, mock_ble_device, mock_bleak_client):
        """Test the complete workflow of scanning and connecting to a device."""
        scanner = FlowerCareScanner()

        # Mock successful scanning
        with patch("flowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            def simulate_detection(callback_func):
                from bleak.backends.scanner import AdvertisementData

                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]
                callback_func(mock_ble_device, mock_advertisement)
                return mock_scanner_instance

            mock_scanner_class.side_effect = simulate_detection

            # Scan for devices
            devices = await scanner.scan_for_devices(timeout=1.0)
            assert len(devices) == 1

            device = devices[0]
            assert isinstance(device, FlowerCareDevice)

            # Mock connection and data reading
            with patch("flowercare.device.BleakClient", return_value=mock_bleak_client):
                # Test connection
                await device.connect()
                assert device.is_connected

                # Test device info reading
                mock_bleak_client.read_gatt_char.side_effect = [
                    b"Flower care\x00\x00",  # Device name
                    bytes([85, 0]) + b"3.3.6\x00\x00\x00",  # Firmware and battery
                ]

                device_info = await device.get_device_info()
                assert isinstance(device_info, DeviceInfo)
                assert device_info.name == "Flower care"
                assert device_info.battery_level == 85
                assert device_info.firmware_version == "3.3.6"

                # Test sensor data reading
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
                        0,
                        0,  # padding
                    ]
                )
                # Reset side_effect before setting return_value
                mock_bleak_client.read_gatt_char.side_effect = None
                mock_bleak_client.read_gatt_char.return_value = sensor_bytes

                sensor_data = await device.read_sensor_data()
                assert isinstance(sensor_data, SensorData)
                assert sensor_data.temperature == 23.5
                assert sensor_data.brightness == 150
                assert sensor_data.moisture == 65
                assert sensor_data.conductivity == 520

                # Test LED blinking
                await device.blink_led()

                # Test disconnection
                await device.disconnect()
                assert not device.is_connected

    @pytest.mark.asyncio
    async def test_historical_data_workflow(self, mock_ble_device, mock_bleak_client):
        """Test the historical data retrieval workflow."""
        device = FlowerCareDevice(mock_ble_device)

        with patch("flowercare.device.BleakClient", return_value=mock_bleak_client):
            await device.connect()

            # Mock historical data responses
            count_response = bytes([2, 0]) + b"\x00" * 14  # 2 entries
            entry_response = bytes(
                [
                    0x00,
                    0x80,
                    0xA0,
                    0x63,  # Timestamp (1672574400)
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
                    0,  # padding to make 16 bytes for sensor data
                ]
            )

            # Mock epoch time first, then responses
            epoch_time_bytes = (1672580000).to_bytes(4, byteorder="little")  # Mock epoch time
            mock_bleak_client.read_gatt_char.side_effect = [
                epoch_time_bytes,  # First read: epoch time
                count_response,  # Second read: historical entries count
                entry_response,  # Third read: first entry
                entry_response,  # Fourth read: second entry
            ]

            historical_data = await device.get_historical_data()

            assert isinstance(historical_data, list)
            assert len(historical_data) == 2

            for entry in historical_data:
                assert isinstance(entry, HistoricalEntry)
                assert isinstance(entry.sensor_data, SensorData)
                assert isinstance(entry.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_context_manager_workflow(self, mock_ble_device, mock_bleak_client):
        """Test using device as context manager."""
        device = FlowerCareDevice(mock_ble_device)

        with patch("flowercare.device.BleakClient", return_value=mock_bleak_client):
            async with device:
                assert device.is_connected

                # Test that we can perform operations within the context
                mock_bleak_client.read_gatt_char.return_value = bytes(
                    [235, 0, 0, 150, 0, 0, 0, 65, 8, 2, 0, 0, 0, 0, 0, 0]
                )

                sensor_data = await device.read_sensor_data()
                assert isinstance(sensor_data, SensorData)

            # Device should be disconnected after exiting context
            mock_bleak_client.disconnect.assert_called()

    @pytest.mark.asyncio
    async def test_find_device_by_mac_workflow(self, mock_ble_device):
        """Test finding a specific device by MAC address."""
        scanner = FlowerCareScanner()
        target_mac = "AA:BB:CC:DD:EE:FF"
        mock_ble_device.address = target_mac

        with patch("flowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            def simulate_detection(callback_func):
                from bleak.backends.scanner import AdvertisementData

                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]
                callback_func(mock_ble_device, mock_advertisement)
                return mock_scanner_instance

            mock_scanner_class.side_effect = simulate_detection

            # Test finding existing device
            found_device = await scanner.find_device_by_mac(target_mac)
            assert found_device is not None
            assert isinstance(found_device, FlowerCareDevice)
            assert found_device.mac_address == target_mac

            # Test finding non-existing device
            not_found = await scanner.find_device_by_mac("FF:FF:FF:FF:FF:FF")
            assert not_found is None

    def test_pydantic_model_integration(self):
        """Test that Pydantic models work correctly together."""
        # Create sensor data
        sensor_data = SensorData(
            temperature=25.5,
            brightness=200,
            moisture=70,
            conductivity=600,
            timestamp=datetime.now(),
        )

        # Create device info
        device_info = DeviceInfo(
            name="Test Device",
            mac_address="AA:BB:CC:DD:EE:FF",
            firmware_version="1.0.0",
            battery_level=90,
        )

        # Create historical entry
        historical_entry = HistoricalEntry(timestamp=datetime.now(), sensor_data=sensor_data)

        # Test that all models validate correctly
        assert sensor_data.temperature == 25.5
        assert device_info.name == "Test Device"
        assert historical_entry.sensor_data == sensor_data

        # Test string representations
        assert "25.5°C" in str(sensor_data)
        assert "Test Device" in str(device_info)
        assert "25.5°C" in str(historical_entry)

    def test_error_handling_integration(self):
        """Test that exceptions are properly propagated."""
        from flowercare.exceptions import ConnectionError, DeviceError, FlowerCareError

        # Test exception hierarchy
        connection_error = ConnectionError("Connection failed")
        device_error = DeviceError("Device error")

        assert isinstance(connection_error, FlowerCareError)
        assert isinstance(device_error, FlowerCareError)

        # Test that specific errors can be caught
        try:
            raise connection_error
        except FlowerCareError:
            pass  # Should catch as base class

        try:
            raise device_error
        except DeviceError:
            pass  # Should catch as specific class

    def test_logging_integration(self):
        """Test that logging setup works with the library."""
        # Test that setup_logging doesn't raise exceptions
        setup_logging("INFO")
        setup_logging("DEBUG", include_timestamp=False)

        # Test that logger creation works
        from flowercare.logging import get_logger

        logger = get_logger("test")
        assert logger is not None
        assert logger.name == "flowercare.test"
