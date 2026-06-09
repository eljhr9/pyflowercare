from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SensorData(BaseModel):
    """Sensor data from a FlowerCare device."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    temperature: float = Field(
        ..., description="Temperature in degrees Celsius", ge=-50.0, le=100.0
    )
    brightness: Optional[int] = Field(
        None, description="Light brightness in lux (None if not measured)", ge=0
    )
    moisture: int = Field(..., description="Soil moisture percentage", ge=0, le=100)
    conductivity: Optional[int] = Field(
        None, description="Soil conductivity in µS/cm (None if not measured)", ge=0
    )
    timestamp: Optional[datetime] = Field(None, description="Timestamp when the data was collected")

    def __str__(self) -> str:
        brightness = "N/A" if self.brightness is None else f"{self.brightness} lux"
        conductivity = "N/A" if self.conductivity is None else f"{self.conductivity} µS/cm"
        return (
            f"Temperature: {self.temperature}°C, "
            f"Brightness: {brightness}, "
            f"Moisture: {self.moisture}%, "
            f"Conductivity: {conductivity}"
        )


class DeviceInfo(BaseModel):
    """Information about a FlowerCare device."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    name: str = Field(..., description="Device name", min_length=1)
    mac_address: str = Field(
        ...,
        description="Device MAC address",
        pattern=r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$|^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$",
    )
    firmware_version: Optional[str] = Field(None, description="Device firmware version")
    battery_level: Optional[int] = Field(None, description="Battery level percentage", ge=0, le=100)

    def __str__(self) -> str:
        return (
            f"Device: {self.name} ({self.mac_address}), "
            f"Firmware: {self.firmware_version}, "
            f"Battery: {self.battery_level}%"
        )


class HistoricalEntry(BaseModel):
    """A historical sensor data entry."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    timestamp: datetime = Field(..., description="Timestamp of the historical entry")
    sensor_data: SensorData = Field(..., description="Sensor data for this historical entry")

    def __str__(self) -> str:
        return f"{self.timestamp}: {self.sensor_data}"
