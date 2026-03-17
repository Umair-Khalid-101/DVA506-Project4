import unittest
from datetime import datetime
from smartmove.domain.vehicle import Vehicle
from smartmove.domain.enums import VehicleType, City, VehicleState
from smartmove.domain.telemetry_event import TelemetryEvent
from smartmove.core.controller import SmartMoveCentralController


class TestTelemetry(unittest.TestCase):

    def test_low_battery_during_trip(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V1", VehicleType.SCOOTER, City.LONDON)
        user = type("User", (), {"id": "U1"})()

        controller.start_rental(user, vehicle)

        event = TelemetryEvent(
            vehicle.id,
            city=City.LONDON,
            latitude=0.0,
            longitude=0.0,
            speed=0,
            battery=4,
            temperature=30,
            timestamp=datetime.now()
        )

        controller.process_telemetry_event(vehicle, event)
        self.assertEqual(vehicle.state.value, VehicleState.MAINTENANCE.value)

    def test_overheating_during_trip(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V2", VehicleType.SCOOTER, City.LONDON)
        user = type("User", (), {"id": "U2"})()

        controller.start_rental(user, vehicle)

        event = TelemetryEvent(
            vehicle.id,
            city=City.LONDON,
            latitude=0.0,
            longitude=0.0,
            speed=0,
            battery=100,
            temperature=61,
            timestamp=datetime.now()
        )

        controller.process_telemetry_event(vehicle, event)
        self.assertEqual(vehicle.state.value, VehicleState.EMERGENCY_LOCK.value)

    def test_theft_detection_when_vehicle_moves_without_rental(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V3", VehicleType.SCOOTER, City.LONDON)

        event = TelemetryEvent(
            vehicle.id,
            city=City.LONDON,
            latitude=0.0,
            longitude=0.0,
            speed=2,
            battery=100,
            temperature=30,
            timestamp=datetime.now()
        )

        controller.process_telemetry_event(vehicle, event)
        self.assertEqual(vehicle.state.value, VehicleState.EMERGENCY_LOCK.value)

    def test_no_theft_when_vehicle_is_not_moving(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V4", VehicleType.SCOOTER, City.LONDON)

        event = TelemetryEvent(
            vehicle.id,
            city=City.LONDON,
            latitude=0.0,
            longitude=0.0,
            speed=0,
            battery=100,
            temperature=30,
            timestamp=datetime.now()
        )

        controller.process_telemetry_event(vehicle, event)
        self.assertNotEqual(vehicle.state.value, VehicleState.EMERGENCY_LOCK.value)


if __name__ == "__main__":
    unittest.main()