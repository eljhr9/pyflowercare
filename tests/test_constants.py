import pytest

from flowercare.constants import (
    ADVERTISEMENT_UUID,
    CHARACTERISTIC_UUIDS,
    COMMANDS,
    DEVICE_NAME_PREFIX,
    SERVICE_UUIDS,
)


class TestConstants:
    """Test FlowerCare constants."""

    def test_service_uuids_structure(self):
        """Test SERVICE_UUIDS structure and values."""
        expected_keys = ["GENERIC_ACCESS", "ROOT_SERVICE", "DATA_SERVICE", "HISTORY_SERVICE"]

        assert isinstance(SERVICE_UUIDS, dict)
        assert all(key in SERVICE_UUIDS for key in expected_keys)

        # Test UUID format (should be valid UUID strings)
        for key, uuid in SERVICE_UUIDS.items():
            assert isinstance(uuid, str)
            assert len(uuid) == 36  # Standard UUID length
            assert uuid.count("-") == 4  # Standard UUID has 4 hyphens

    def test_service_uuids_values(self):
        """Test specific SERVICE_UUIDS values."""
        assert SERVICE_UUIDS["GENERIC_ACCESS"] == "00001800-0000-1000-8000-00805f9b34fb"
        assert SERVICE_UUIDS["ROOT_SERVICE"] == "0000fe95-0000-1000-8000-00805f9b34fb"
        assert SERVICE_UUIDS["DATA_SERVICE"] == "00001204-0000-1000-8000-00805f9b34fb"
        assert SERVICE_UUIDS["HISTORY_SERVICE"] == "00001206-0000-1000-8000-00805f9b34fb"

    def test_characteristic_uuids_structure(self):
        """Test CHARACTERISTIC_UUIDS structure and values."""
        expected_keys = [
            "DEVICE_NAME",
            "MODE_CHANGE",
            "SENSOR_DATA",
            "FIRMWARE_BATTERY",
            "HISTORY_CONTROL",
            "HISTORY_DATA",
            "EPOCH_TIME",
        ]

        assert isinstance(CHARACTERISTIC_UUIDS, dict)
        assert all(key in CHARACTERISTIC_UUIDS for key in expected_keys)

        # Test UUID format
        for key, uuid in CHARACTERISTIC_UUIDS.items():
            assert isinstance(uuid, str)
            assert len(uuid) == 36  # Standard UUID length
            assert uuid.count("-") == 4  # Standard UUID has 4 hyphens

    def test_characteristic_uuids_values(self):
        """Test specific CHARACTERISTIC_UUIDS values."""
        assert CHARACTERISTIC_UUIDS["DEVICE_NAME"] == "00002a00-0000-1000-8000-00805f9b34fb"
        assert CHARACTERISTIC_UUIDS["MODE_CHANGE"] == "00001a00-0000-1000-8000-00805f9b34fb"
        assert CHARACTERISTIC_UUIDS["SENSOR_DATA"] == "00001a01-0000-1000-8000-00805f9b34fb"
        assert CHARACTERISTIC_UUIDS["FIRMWARE_BATTERY"] == "00001a02-0000-1000-8000-00805f9b34fb"
        assert CHARACTERISTIC_UUIDS["HISTORY_CONTROL"] == "00001a10-0000-1000-8000-00805f9b34fb"
        assert CHARACTERISTIC_UUIDS["HISTORY_DATA"] == "00001a11-0000-1000-8000-00805f9b34fb"
        assert CHARACTERISTIC_UUIDS["EPOCH_TIME"] == "00001a12-0000-1000-8000-00805f9b34fb"

    def test_commands_structure(self):
        """Test COMMANDS structure and values."""
        expected_keys = [
            "REALTIME_DATA",
            "HISTORY_DATA",
            "HISTORY_READ_INIT",
            "HISTORY_READ_ENTRY",
            "BLINK_LED",
        ]

        assert isinstance(COMMANDS, dict)
        assert all(key in COMMANDS for key in expected_keys)

        # Test that all commands are bytes
        for key, command in COMMANDS.items():
            assert isinstance(command, bytes)
            assert len(command) >= 2  # All commands should be at least 2 bytes

    def test_commands_values(self):
        """Test specific COMMANDS values."""
        assert COMMANDS["REALTIME_DATA"] == bytes([0xA0, 0x1F])
        assert COMMANDS["HISTORY_DATA"] == bytes([0xA0, 0x00])
        assert COMMANDS["HISTORY_READ_INIT"] == bytes([0xA0, 0x00])
        assert COMMANDS["HISTORY_READ_ENTRY"] == bytes([0xA1, 0x00])
        assert COMMANDS["BLINK_LED"] == bytes([0xFD, 0xFF])

    def test_device_name_prefix(self):
        """Test DEVICE_NAME_PREFIX constant."""
        assert isinstance(DEVICE_NAME_PREFIX, str)
        assert DEVICE_NAME_PREFIX == "Flower care"
        assert len(DEVICE_NAME_PREFIX) > 0

    def test_advertisement_uuid(self):
        """Test ADVERTISEMENT_UUID constant."""
        assert isinstance(ADVERTISEMENT_UUID, str)
        assert ADVERTISEMENT_UUID == "0000fe95-0000-1000-8000-00805f9b34fb"
        assert len(ADVERTISEMENT_UUID) == 36  # Standard UUID length
        assert ADVERTISEMENT_UUID.count("-") == 4  # Standard UUID has 4 hyphens

    def test_uuid_consistency(self):
        """Test UUID consistency between constants."""
        # ROOT_SERVICE and ADVERTISEMENT_UUID should be the same
        assert SERVICE_UUIDS["ROOT_SERVICE"] == ADVERTISEMENT_UUID

        # HISTORY_DATA and HISTORY_READ_INIT commands should be the same
        assert COMMANDS["HISTORY_DATA"] == COMMANDS["HISTORY_READ_INIT"]

    def test_constants_immutability(self):
        """Test that constants are properly typed as Final."""
        # This is more of a static typing test, but we can verify the structure
        # The Final typing should prevent modification in a type checker

        # Verify all expected constants exist
        constants = [
            SERVICE_UUIDS,
            CHARACTERISTIC_UUIDS,
            COMMANDS,
            DEVICE_NAME_PREFIX,
            ADVERTISEMENT_UUID,
        ]

        for constant in constants:
            assert constant is not None

    def test_uuid_format_validation(self):
        """Test that all UUIDs follow the correct format."""
        import re

        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
        )

        # Check all service UUIDs
        for uuid in SERVICE_UUIDS.values():
            assert uuid_pattern.match(uuid), f"Invalid UUID format: {uuid}"

        # Check all characteristic UUIDs
        for uuid in CHARACTERISTIC_UUIDS.values():
            assert uuid_pattern.match(uuid), f"Invalid UUID format: {uuid}"

        # Check advertisement UUID
        assert uuid_pattern.match(ADVERTISEMENT_UUID), f"Invalid UUID format: {ADVERTISEMENT_UUID}"

    def test_command_byte_values(self):
        """Test that command bytes are in valid range."""
        for command_name, command_bytes in COMMANDS.items():
            for byte_val in command_bytes:
                assert 0 <= byte_val <= 255, f"Invalid byte value in {command_name}: {byte_val}"

    def test_all_constants_types(self):
        """Test that all constants have correct types."""
        assert isinstance(SERVICE_UUIDS, dict)
        assert isinstance(CHARACTERISTIC_UUIDS, dict)
        assert isinstance(COMMANDS, dict)
        assert isinstance(DEVICE_NAME_PREFIX, str)
        assert isinstance(ADVERTISEMENT_UUID, str)
