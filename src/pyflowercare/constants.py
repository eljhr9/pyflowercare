from typing import Dict, Final

# Service UUIDs used by FlowerCare devices
SERVICE_UUIDS: Final[Dict[str, str]] = {
    "GENERIC_ACCESS": "00001800-0000-1000-8000-00805f9b34fb",
    "ROOT_SERVICE": "0000fe95-0000-1000-8000-00805f9b34fb",
    "DATA_SERVICE": "00001204-0000-1000-8000-00805f9b34fb",
    "HISTORY_SERVICE": "00001206-0000-1000-8000-00805f9b34fb",
}

# Characteristic UUIDs used by FlowerCare devices
CHARACTERISTIC_UUIDS: Final[Dict[str, str]] = {
    "DEVICE_NAME": "00002a00-0000-1000-8000-00805f9b34fb",
    "MODE_CHANGE": "00001a00-0000-1000-8000-00805f9b34fb",
    "SENSOR_DATA": "00001a01-0000-1000-8000-00805f9b34fb",
    "FIRMWARE_BATTERY": "00001a02-0000-1000-8000-00805f9b34fb",
    "HISTORY_CONTROL": "00001a10-0000-1000-8000-00805f9b34fb",
    "HISTORY_DATA": "00001a11-0000-1000-8000-00805f9b34fb",
    "EPOCH_TIME": "00001a12-0000-1000-8000-00805f9b34fb",
}

# Commands sent to FlowerCare devices
COMMANDS: Final[Dict[str, bytes]] = {
    "REALTIME_DATA": bytes([0xA0, 0x1F]),
    "HISTORY_DATA": bytes([0xA0, 0x00]),
    "HISTORY_READ_INIT": bytes([0xA0, 0x00]),
    "HISTORY_READ_ENTRY": bytes([0xA1, 0x00]),
    "BLINK_LED": bytes([0xFD, 0xFF]),
}

# Device identification constants
DEVICE_NAME_PREFIX: Final[str] = "Flower care"
ADVERTISEMENT_UUID: Final[str] = "0000fe95-0000-1000-8000-00805f9b34fb"
