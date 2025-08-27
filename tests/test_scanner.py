import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from pyflowercare.device import FlowerCareDevice
from pyflowercare.exceptions import TimeoutError
from pyflowercare.scanner import FlowerCareScanner


class TestFlowerCareScanner:
    """Test FlowerCareScanner class."""

    @patch("pyflowercare.scanner.BleakScanner")
    def test_scanner_initialization(self, mock_bleak_scanner):
        """Test scanner initialization."""
        scanner = FlowerCareScanner()
        assert scanner.scanner is not None
        mock_bleak_scanner.assert_called_once()

    def test_is_flowercare_device_by_name(self):
        """Test device identification by name."""
        mock_device = Mock(spec=BLEDevice)
        mock_device.name = "Flower care"
        mock_advertisement = Mock(spec=AdvertisementData)
        mock_advertisement.service_uuids = []

        result = FlowerCareScanner._is_flowercare_device(mock_device, mock_advertisement)
        assert result is True

    def test_is_flowercare_device_by_name_case_insensitive(self):
        """Test device identification by name (case insensitive)."""
        mock_device = Mock(spec=BLEDevice)
        mock_device.name = "FLOWER CARE"
        mock_advertisement = Mock(spec=AdvertisementData)
        mock_advertisement.service_uuids = []

        result = FlowerCareScanner._is_flowercare_device(mock_device, mock_advertisement)
        assert result is True

    def test_is_flowercare_device_by_uuid(self):
        """Test device identification by service UUID."""
        mock_device = Mock(spec=BLEDevice)
        mock_device.name = None
        mock_advertisement = Mock(spec=AdvertisementData)
        mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]

        result = FlowerCareScanner._is_flowercare_device(mock_device, mock_advertisement)
        assert result is True

    def test_is_flowercare_device_by_uuid_case_insensitive(self):
        """Test device identification by service UUID (case insensitive)."""
        mock_device = Mock(spec=BLEDevice)
        mock_device.name = None
        mock_advertisement = Mock(spec=AdvertisementData)
        mock_advertisement.service_uuids = ["0000FE95-0000-1000-8000-00805F9B34FB"]

        result = FlowerCareScanner._is_flowercare_device(mock_device, mock_advertisement)
        assert result is True

    def test_is_not_flowercare_device(self):
        """Test device that is not FlowerCare."""
        mock_device = Mock(spec=BLEDevice)
        mock_device.name = "Other device"
        mock_advertisement = Mock(spec=AdvertisementData)
        mock_advertisement.service_uuids = ["other-uuid"]

        result = FlowerCareScanner._is_flowercare_device(mock_device, mock_advertisement)
        assert result is False

    def test_is_flowercare_device_no_service_uuids(self):
        """Test device identification with no service UUIDs."""
        mock_device = Mock(spec=BLEDevice)
        mock_device.name = "Other device"
        mock_advertisement = Mock(spec=AdvertisementData)
        mock_advertisement.service_uuids = None

        result = FlowerCareScanner._is_flowercare_device(mock_device, mock_advertisement)
        assert result is False

    @pytest.mark.asyncio
    async def test_scan_for_devices_success(self, mock_ble_device):
        """Test successful device scanning."""
        scanner = FlowerCareScanner()

        # Mock the scanner behavior
        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            # Simulate finding a device during scanning
            def simulate_detection(callback_func):
                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]
                callback_func(mock_ble_device, mock_advertisement)
                return mock_scanner_instance

            mock_scanner_class.side_effect = simulate_detection

            devices = await scanner.scan_for_devices(timeout=1.0)

            assert len(devices) == 1
            assert isinstance(devices[0], FlowerCareDevice)
            assert devices[0].device == mock_ble_device

    @pytest.mark.asyncio
    async def test_scan_for_devices_no_devices(self):
        """Test scanning with no devices found."""
        scanner = FlowerCareScanner()

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            devices = await scanner.scan_for_devices(timeout=1.0)

            assert len(devices) == 0

    @pytest.mark.asyncio
    async def test_scan_for_devices_deduplication(self, mock_ble_device):
        """Test device deduplication during scanning."""
        scanner = FlowerCareScanner()

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            def simulate_duplicate_detection(callback_func):
                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]
                # Simulate the same device being detected twice
                callback_func(mock_ble_device, mock_advertisement)
                callback_func(mock_ble_device, mock_advertisement)
                return mock_scanner_instance

            mock_scanner_class.side_effect = simulate_duplicate_detection

            devices = await scanner.scan_for_devices(timeout=1.0)

            # Should only return one device despite being detected twice
            assert len(devices) == 1

    @pytest.mark.asyncio
    async def test_scan_for_devices_timeout_error(self):
        """Test scan timeout handling."""
        scanner = FlowerCareScanner()

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            # Mock asyncio.sleep to raise TimeoutError
            with patch("asyncio.sleep", side_effect=asyncio.TimeoutError):
                with pytest.raises(TimeoutError) as exc_info:
                    await scanner.scan_for_devices(timeout=1.0)

                assert "Scan timeout after 1.0s" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_find_device_by_mac_success(self, mock_ble_device):
        """Test finding device by MAC address."""
        scanner = FlowerCareScanner()

        with patch.object(scanner, "scan_for_devices") as mock_scan:
            mock_device = FlowerCareDevice(mock_ble_device)
            mock_scan.return_value = [mock_device]

            result = await scanner.find_device_by_mac("aa:bb:cc:dd:ee:ff", timeout=1.0)

            assert result == mock_device
            mock_scan.assert_called_once_with(1.0)

    @pytest.mark.asyncio
    async def test_find_device_by_mac_not_found(self, mock_ble_device):
        """Test finding device by MAC address when not found."""
        scanner = FlowerCareScanner()
        mock_ble_device.address = "FF:EE:DD:CC:BB:AA"  # Different address

        with patch.object(scanner, "scan_for_devices") as mock_scan:
            mock_device = FlowerCareDevice(mock_ble_device)
            mock_scan.return_value = [mock_device]

            result = await scanner.find_device_by_mac("aa:bb:cc:dd:ee:ff", timeout=1.0)

            assert result is None

    @pytest.mark.asyncio
    async def test_find_device_by_mac_case_insensitive(self, mock_ble_device):
        """Test finding device by MAC address (case insensitive)."""
        scanner = FlowerCareScanner()

        with patch.object(scanner, "scan_for_devices") as mock_scan:
            mock_device = FlowerCareDevice(mock_ble_device)
            mock_scan.return_value = [mock_device]

            # Test with uppercase MAC
            result = await scanner.find_device_by_mac("AA:BB:CC:DD:EE:FF", timeout=1.0)

            assert result == mock_device

    @pytest.mark.asyncio
    async def test_scan_continuously_with_timeout(self, mock_ble_device):
        """Test continuous scanning with timeout."""
        scanner = FlowerCareScanner()
        detected_devices = []

        def callback(device):
            detected_devices.append(device)

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_instance.__aenter__ = AsyncMock(return_value=mock_scanner_instance)
            mock_scanner_instance.__aexit__ = AsyncMock(return_value=None)

            def mock_scanner_init(detection_callback):
                # Trigger detection callback immediately
                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]
                detection_callback(mock_ble_device, mock_advertisement)
                return mock_scanner_instance

            mock_scanner_class.side_effect = mock_scanner_init

            await scanner.scan_continuously(callback, timeout=0.1)

            assert len(detected_devices) == 1
            assert isinstance(detected_devices[0], FlowerCareDevice)

    @pytest.mark.asyncio
    async def test_scan_continuously_deduplication(self, mock_ble_device):
        """Test continuous scanning deduplication."""
        scanner = FlowerCareScanner()
        detected_devices = []

        def callback(device):
            detected_devices.append(device)

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_instance.__aenter__ = AsyncMock(return_value=mock_scanner_instance)
            mock_scanner_instance.__aexit__ = AsyncMock(return_value=None)

            def mock_scanner_init(detection_callback):
                # Trigger detection callback multiple times for the same device
                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]
                detection_callback(mock_ble_device, mock_advertisement)
                detection_callback(mock_ble_device, mock_advertisement)
                return mock_scanner_instance

            mock_scanner_class.side_effect = mock_scanner_init

            await scanner.scan_continuously(callback, timeout=0.1)

            # Should only call callback once despite multiple detections
            assert len(detected_devices) == 1

    @pytest.mark.asyncio
    async def test_scan_stream_with_devices(self, mock_ble_device):
        """Test streaming scan with devices."""
        scanner = FlowerCareScanner()

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            def simulate_detection(callback_func):
                mock_advertisement = Mock(spec=AdvertisementData)
                mock_advertisement.service_uuids = ["0000fe95-0000-1000-8000-00805f9b34fb"]

                # Simulate device detection after a short delay
                async def delayed_detection():
                    await asyncio.sleep(0.01)
                    callback_func(mock_ble_device, mock_advertisement)

                asyncio.create_task(delayed_detection())
                return mock_scanner_instance

            mock_scanner_class.side_effect = simulate_detection

            devices = []
            async for device in scanner.scan_stream(timeout=0.1):
                devices.append(device)
                break  # Stop after first device

            assert len(devices) == 1
            assert isinstance(devices[0], FlowerCareDevice)

    @pytest.mark.asyncio
    async def test_scan_stream_no_devices(self):
        """Test streaming scan with no devices."""
        scanner = FlowerCareScanner()

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_class.return_value = mock_scanner_instance

            devices = []
            async for device in scanner.scan_stream(timeout=0.1):
                devices.append(device)

            assert len(devices) == 0

    @pytest.mark.asyncio
    async def test_scan_stream_cancellation(self):
        """Test streaming scan cancellation."""
        scanner = FlowerCareScanner()

        with patch("pyflowercare.scanner.BleakScanner") as mock_scanner_class:
            mock_scanner_instance = AsyncMock()
            mock_scanner_instance.__aenter__ = AsyncMock(return_value=mock_scanner_instance)
            mock_scanner_instance.__aexit__ = AsyncMock(return_value=None)
            mock_scanner_class.return_value = mock_scanner_instance

            # Create a task that will be cancelled
            async def scan_task():
                async for device in scanner.scan_stream():
                    pass  # This should run indefinitely

            task = asyncio.create_task(scan_task())
            await asyncio.sleep(0.01)  # Let the task start
            task.cancel()

            with pytest.raises(asyncio.CancelledError):
                await task
