class FlowerCareError(Exception):
    """Base exception for FlowerCare library."""

    pass


class ConnectionError(FlowerCareError):
    """Raised when connection to device fails."""

    pass


class DeviceError(FlowerCareError):
    """Raised when device operation fails."""

    pass


class DataParsingError(FlowerCareError):
    """Raised when sensor data parsing fails."""

    pass


class TimeoutError(FlowerCareError):
    """Raised when operation times out."""

    pass
