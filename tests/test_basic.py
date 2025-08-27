import pytest

from pyflowercare import DeviceInfo, FlowerCareDevice, FlowerCareScanner, SensorData, setup_logging
from pyflowercare.exceptions import FlowerCareError


def test_imports():
    """Test that all main components can be imported."""
    assert FlowerCareDevice is not None
    assert FlowerCareScanner is not None
    assert SensorData is not None
    assert DeviceInfo is not None
    assert setup_logging is not None


def test_exceptions():
    """Test exception hierarchy."""
    error = FlowerCareError("test")
    assert isinstance(error, Exception)
    assert str(error) == "test"


def test_sensor_data_creation():
    """Test creating SensorData with Pydantic."""
    data = SensorData(temperature=23.5, brightness=150, moisture=65, conductivity=520)

    assert data.temperature == 23.5
    assert data.brightness == 150
    assert data.moisture == 65
    assert data.conductivity == 520


def test_device_info_creation():
    """Test creating DeviceInfo with Pydantic."""
    info = DeviceInfo(name="Test Device", mac_address="AA:BB:CC:DD:EE:FF")

    assert info.name == "Test Device"
    assert info.mac_address == "AA:BB:CC:DD:EE:FF"


def test_pydantic_validation():
    """Test Pydantic validation."""
    # Valid data should work
    SensorData(temperature=25.0, brightness=100, moisture=50, conductivity=300)

    # Invalid data should raise ValidationError
    with pytest.raises(Exception):  # Pydantic ValidationError
        SensorData(temperature=-100.0, brightness=100, moisture=50, conductivity=300)
