import pytest

from flowercare.exceptions import (
    ConnectionError,
    DataParsingError,
    DeviceError,
    FlowerCareError,
    TimeoutError,
)


class TestExceptions:
    """Test FlowerCare exception classes."""

    def test_flowercare_error_base(self):
        """Test base FlowerCareError exception."""
        error = FlowerCareError("Base error")

        assert isinstance(error, Exception)
        assert str(error) == "Base error"

    def test_connection_error_inheritance(self):
        """Test ConnectionError inherits from FlowerCareError."""
        error = ConnectionError("Connection failed")

        assert isinstance(error, FlowerCareError)
        assert isinstance(error, Exception)
        assert str(error) == "Connection failed"

    def test_device_error_inheritance(self):
        """Test DeviceError inherits from FlowerCareError."""
        error = DeviceError("Device operation failed")

        assert isinstance(error, FlowerCareError)
        assert isinstance(error, Exception)
        assert str(error) == "Device operation failed"

    def test_data_parsing_error_inheritance(self):
        """Test DataParsingError inherits from FlowerCareError."""
        error = DataParsingError("Failed to parse data")

        assert isinstance(error, FlowerCareError)
        assert isinstance(error, Exception)
        assert str(error) == "Failed to parse data"

    def test_timeout_error_inheritance(self):
        """Test TimeoutError inherits from FlowerCareError."""
        error = TimeoutError("Operation timed out")

        assert isinstance(error, FlowerCareError)
        assert isinstance(error, Exception)
        assert str(error) == "Operation timed out"

    def test_exception_hierarchy(self):
        """Test the complete exception hierarchy."""
        errors = [
            ConnectionError("test"),
            DeviceError("test"),
            DataParsingError("test"),
            TimeoutError("test"),
        ]

        for error in errors:
            assert isinstance(error, FlowerCareError)
            assert isinstance(error, Exception)

    def test_raising_exceptions(self):
        """Test raising and catching exceptions."""
        with pytest.raises(FlowerCareError):
            raise ConnectionError("Connection test")

        with pytest.raises(ConnectionError):
            raise ConnectionError("Connection test")

        with pytest.raises(FlowerCareError):
            raise DeviceError("Device test")

        with pytest.raises(DeviceError):
            raise DeviceError("Device test")

        with pytest.raises(FlowerCareError):
            raise DataParsingError("Parsing test")

        with pytest.raises(DataParsingError):
            raise DataParsingError("Parsing test")

        with pytest.raises(FlowerCareError):
            raise TimeoutError("Timeout test")

        with pytest.raises(TimeoutError):
            raise TimeoutError("Timeout test")

    def test_exception_messages(self):
        """Test exception messages are preserved."""
        message = "Detailed error message"

        errors = [
            FlowerCareError(message),
            ConnectionError(message),
            DeviceError(message),
            DataParsingError(message),
            TimeoutError(message),
        ]

        for error in errors:
            assert str(error) == message

    def test_empty_exceptions(self):
        """Test exceptions without messages."""
        errors = [
            FlowerCareError(),
            ConnectionError(),
            DeviceError(),
            DataParsingError(),
            TimeoutError(),
        ]

        for error in errors:
            assert str(error) == ""
