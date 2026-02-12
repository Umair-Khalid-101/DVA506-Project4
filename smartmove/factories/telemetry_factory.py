# factories/telemetry_factory.py
import random
from domain.telemetry_snapshot import TelemetrySnapshot
from dataclasses import dataclass
from datetime import datetime
from domain.telemetry_event import TelemetryEvent

class TelemetryFactory:
    """
    Simulates vehicle hardware telemetry.
    """

    @staticmethod
    def create_initial(vehicle) -> TelemetrySnapshot:
        return TelemetrySnapshot(
            latitude=vehicle.latitude,
            longitude=vehicle.longitude,
            speed=0.0,
            battery=random.uniform(60, 100),
            temperature=random.uniform(20, 35)
        )

    @staticmethod
    def next_snapshot(
        vehicle,
        previous: TelemetrySnapshot
    ) -> TelemetrySnapshot:

        speed = (
            random.uniform(5, vehicle.max_speed)
            if vehicle.is_in_use()
            else 0.0
        )

        return TelemetrySnapshot(
            latitude=previous.latitude + random.uniform(-0.00005, 0.00005),
            longitude=previous.longitude + random.uniform(-0.00005, 0.00005),
            speed=speed,
            battery=max(previous.battery - random.uniform(0.02, 0.08), 0),
            temperature=previous.temperature + random.uniform(-0.2, 0.6)
        )
    
    @staticmethod
    def to_event(vehicle, snapshot: TelemetrySnapshot) -> TelemetryEvent:
        return TelemetryEvent(
            vehicle_id=vehicle.id,
            user_id=vehicle.current_user_id,
            city=vehicle.city,
            latitude=snapshot.latitude,
            longitude=snapshot.longitude,
            speed=snapshot.speed,
            battery=snapshot.battery,
            temperature=snapshot.temperature,
            timestamp=datetime.utcnow()
        )
