from dataclasses import dataclass
from datetime import datetime
from domain.enums import City

@dataclass(frozen=True)
class TelemetryEvent:
    vehicle_id: str
    user_id: str | None
    city: City
    latitude: float
    longitude: float
    speed: float
    battery: float
    temperature: float
    timestamp: datetime
