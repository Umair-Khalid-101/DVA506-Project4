import random
from datetime import datetime
from domain.telemetry_snapshot import TelemetrySnapshot
from domain.telemetry_event import TelemetryEvent
from domain.enums import VehicleState


class TelemetryFactory:

    @staticmethod
    def create_initial(vehicle) -> TelemetrySnapshot:
        lat, lon = vehicle.gps

        return TelemetrySnapshot(
            latitude=lat,
            longitude=lon,
            speed=0.0,
            battery=vehicle.battery,
            temperature=vehicle.temperature
        )

    @staticmethod
    def next_snapshot(vehicle, previous: TelemetrySnapshot) -> TelemetrySnapshot:

        if vehicle.state == VehicleState.IN_USE:
            speed = random.uniform(5, 25)
        else:
            speed = 0.0

        lat_shift = random.uniform(-0.00005, 0.00005)
        lon_shift = random.uniform(-0.00005, 0.00005)

        new_battery = max(previous.battery - random.uniform(0.02, 0.08), 0)
        new_temperature = previous.temperature + random.uniform(-0.2, 0.6)

        return TelemetrySnapshot(
            latitude=previous.latitude + lat_shift,
            longitude=previous.longitude + lon_shift,
            speed=speed,
            battery=new_battery,
            temperature=new_temperature
        )

    @staticmethod
    def to_event(vehicle, snapshot: TelemetrySnapshot) -> TelemetryEvent:
        return TelemetryEvent(
            vehicle_id=vehicle.id,
            city=vehicle.city,
            latitude=snapshot.latitude,
            longitude=snapshot.longitude,
            speed=snapshot.speed,
            battery=snapshot.battery,
            temperature=snapshot.temperature,
            timestamp=datetime.utcnow()
        )
