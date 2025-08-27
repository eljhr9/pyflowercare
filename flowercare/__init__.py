from .device import FlowerCareDevice
from .exceptions import (
    ConnectionError,
    DataParsingError,
    DeviceError,
    FlowerCareError,
    TimeoutError,
)
from .logging import setup_logging
from .models import DeviceInfo, HistoricalEntry, SensorData
from .scanner import FlowerCareScanner

__version__: str = "0.1.0"
__all__ = [
    "FlowerCareDevice",
    "FlowerCareScanner",
    "FlowerCareError",
    "ConnectionError",
    "DeviceError",
    "DataParsingError",
    "TimeoutError",
    "SensorData",
    "DeviceInfo",
    "HistoricalEntry",
    "setup_logging",
]
