from datetime import datetime

import pytest
from pydantic import ValidationError

from flowercare.models import DeviceInfo, HistoricalEntry, SensorData


class TestSensorData:
    """Test SensorData Pydantic model."""

    def test_valid_sensor_data_creation(self):
        """Test creating valid sensor data."""
        data = SensorData(temperature=23.5, brightness=150, moisture=65, conductivity=520)

        assert data.temperature == 23.5
        assert data.brightness == 150
        assert data.moisture == 65
        assert data.conductivity == 520
        assert data.timestamp is None

    def test_sensor_data_with_timestamp(self):
        """Test sensor data with timestamp."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        data = SensorData(
            temperature=23.5, brightness=150, moisture=65, conductivity=520, timestamp=timestamp
        )

        assert data.timestamp == timestamp

    def test_temperature_validation(self):
        """Test temperature validation."""
        # Valid temperature
        SensorData(temperature=25.0, brightness=100, moisture=50, conductivity=300)

        # Invalid temperature - too low
        with pytest.raises(ValidationError) as exc_info:
            SensorData(temperature=-60.0, brightness=100, moisture=50, conductivity=300)
        assert "greater than or equal to -50" in str(exc_info.value)

        # Invalid temperature - too high
        with pytest.raises(ValidationError) as exc_info:
            SensorData(temperature=110.0, brightness=100, moisture=50, conductivity=300)
        assert "less than or equal to 100" in str(exc_info.value)

    def test_brightness_validation(self):
        """Test brightness validation."""
        # Valid brightness
        SensorData(temperature=25.0, brightness=0, moisture=50, conductivity=300)

        # Invalid brightness - negative
        with pytest.raises(ValidationError) as exc_info:
            SensorData(temperature=25.0, brightness=-1, moisture=50, conductivity=300)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_moisture_validation(self):
        """Test moisture validation."""
        # Valid moisture
        SensorData(temperature=25.0, brightness=100, moisture=0, conductivity=300)
        SensorData(temperature=25.0, brightness=100, moisture=100, conductivity=300)

        # Invalid moisture - too low
        with pytest.raises(ValidationError) as exc_info:
            SensorData(temperature=25.0, brightness=100, moisture=-1, conductivity=300)
        assert "greater than or equal to 0" in str(exc_info.value)

        # Invalid moisture - too high
        with pytest.raises(ValidationError) as exc_info:
            SensorData(temperature=25.0, brightness=100, moisture=101, conductivity=300)
        assert "less than or equal to 100" in str(exc_info.value)

    def test_conductivity_validation(self):
        """Test conductivity validation."""
        # Valid conductivity
        SensorData(temperature=25.0, brightness=100, moisture=50, conductivity=0)

        # Invalid conductivity - negative
        with pytest.raises(ValidationError) as exc_info:
            SensorData(temperature=25.0, brightness=100, moisture=50, conductivity=-1)
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            SensorData(
                temperature=25.0,
                brightness=100,
                moisture=50,
                conductivity=300,
                extra_field="not allowed",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_string_representation(self):
        """Test string representation."""
        data = SensorData(temperature=23.5, brightness=150, moisture=65, conductivity=520)

        expected = (
            "Temperature: 23.5°C, Brightness: 150 lux, Moisture: 65%, Conductivity: 520 µS/cm"
        )
        assert str(data) == expected


class TestDeviceInfo:
    """Test DeviceInfo Pydantic model."""

    def test_valid_device_info_creation(self):
        """Test creating valid device info."""
        info = DeviceInfo(name="Flower care", mac_address="AA:BB:CC:DD:EE:FF")

        assert info.name == "Flower care"
        assert info.mac_address == "AA:BB:CC:DD:EE:FF"
        assert info.firmware_version is None
        assert info.battery_level is None

    def test_device_info_with_optional_fields(self):
        """Test device info with optional fields."""
        info = DeviceInfo(
            name="Flower care",
            mac_address="AA:BB:CC:DD:EE:FF",
            firmware_version="3.3.6",
            battery_level=85,
        )

        assert info.firmware_version == "3.3.6"
        assert info.battery_level == 85

    def test_name_validation(self):
        """Test name validation."""
        # Valid name
        DeviceInfo(name="Flower care", mac_address="AA:BB:CC:DD:EE:FF")

        # Invalid name - empty
        with pytest.raises(ValidationError) as exc_info:
            DeviceInfo(name="", mac_address="AA:BB:CC:DD:EE:FF")
        assert "at least 1 character" in str(exc_info.value)

        # Test string stripping
        info = DeviceInfo(name="  Flower care  ", mac_address="AA:BB:CC:DD:EE:FF")
        assert info.name == "Flower care"

    def test_mac_address_validation(self):
        """Test MAC address validation."""
        # Valid MAC addresses
        valid_macs = [
            "AA:BB:CC:DD:EE:FF",
            "aa:bb:cc:dd:ee:ff",
            "AA-BB-CC-DD-EE-FF",
            "D2EA1A46-C089-00D1-6B25-0E7FC729CF44",  # UUID format
        ]

        for mac in valid_macs:
            DeviceInfo(name="Test", mac_address=mac)

        # Invalid MAC addresses
        invalid_macs = ["invalid", "AA:BB:CC:DD:EE", "GG:HH:II:JJ:KK:LL"]

        for mac in invalid_macs:
            with pytest.raises(ValidationError):
                DeviceInfo(name="Test", mac_address=mac)

    def test_battery_level_validation(self):
        """Test battery level validation."""
        # Valid battery levels
        DeviceInfo(name="Test", mac_address="AA:BB:CC:DD:EE:FF", battery_level=0)
        DeviceInfo(name="Test", mac_address="AA:BB:CC:DD:EE:FF", battery_level=100)

        # Invalid battery levels
        with pytest.raises(ValidationError) as exc_info:
            DeviceInfo(name="Test", mac_address="AA:BB:CC:DD:EE:FF", battery_level=-1)
        assert "greater than or equal to 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            DeviceInfo(name="Test", mac_address="AA:BB:CC:DD:EE:FF", battery_level=101)
        assert "less than or equal to 100" in str(exc_info.value)

    def test_string_representation(self):
        """Test string representation."""
        info = DeviceInfo(
            name="Flower care",
            mac_address="AA:BB:CC:DD:EE:FF",
            firmware_version="3.3.6",
            battery_level=85,
        )

        expected = "Device: Flower care (AA:BB:CC:DD:EE:FF), Firmware: 3.3.6, Battery: 85%"
        assert str(info) == expected


class TestHistoricalEntry:
    """Test HistoricalEntry Pydantic model."""

    def test_valid_historical_entry_creation(self, sample_sensor_data):
        """Test creating valid historical entry."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        entry = HistoricalEntry(timestamp=timestamp, sensor_data=sample_sensor_data)

        assert entry.timestamp == timestamp
        assert entry.sensor_data == sample_sensor_data

    def test_historical_entry_validation(self):
        """Test historical entry validation."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)

        # Invalid sensor data
        with pytest.raises(ValidationError):
            HistoricalEntry(timestamp=timestamp, sensor_data="not sensor data")

    def test_string_representation(self, sample_sensor_data):
        """Test string representation."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        entry = HistoricalEntry(timestamp=timestamp, sensor_data=sample_sensor_data)

        expected = f"{timestamp}: {sample_sensor_data}"
        assert str(entry) == expected

    def test_extra_fields_forbidden(self, sample_sensor_data):
        """Test that extra fields are forbidden."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)

        with pytest.raises(ValidationError) as exc_info:
            HistoricalEntry(
                timestamp=timestamp, sensor_data=sample_sensor_data, extra_field="not allowed"
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)
