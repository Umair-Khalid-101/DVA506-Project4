# (process_telemetry_event()) must be refactored for this class to pass
import unittest
from datetime import datetime
from smartmove.domain.vehicle import Vehicle
from smartmove.domain.enums import VehicleType, City, VehicleState
from smartmove.domain.telemetry_event import TelemetryEvent
from smartmove.core.controller import SmartMoveCentralController


class TestCityRules(unittest.TestCase):

    def test_milan_helmet_presence_required_for_moped(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V1", VehicleType.MOPED, City.MILAN)
        vehicle.helmet_present = False
        user = type("User", (), {"id": "U1"})()

        with self.assertRaises(Exception):
            controller.start_rental(user, vehicle)

    def test_milan_moped_with_helmet_can_start(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V2", VehicleType.MOPED, City.MILAN)
        vehicle.helmet_present = True
        user = type("User", (), {"id": "U2"})()

        rental = controller.start_rental(user, vehicle)

        self.assertIsNotNone(rental)
        self.assertEqual(vehicle.state.value, VehicleState.IN_USE.value)

    def test_london_congestion_charge_applied(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V3", VehicleType.SCOOTER, City.LONDON)
        user = type("User", (), {"id": "U3"})()

        rental = controller.start_rental(user, vehicle)
        controller.end_rental(vehicle)

        self.assertGreaterEqual(rental.cost, 5.0)

    # def test_rome_restricted_zone_enters_emergency_lock(self):
    #     controller = SmartMoveCentralController()
    #     vehicle = Vehicle("V4", VehicleType.SCOOTER, City.ROME)
    #     user = type("User", (), {"id": "U4"})()

    #     controller.start_rental(user, vehicle)

    #     event = TelemetryEvent(
    #         vehicle.id,
    #         city=City.ROME,
    #         latitude=42.0,
    #         longitude=0.0,
    #         speed=0,
    #         battery=100,
    #         temperature=30,
    #         timestamp=datetime.now()
    #     )

    #     controller.process_telemetry_event(vehicle, event)
    #     self.assertEqual(vehicle.state.value, VehicleState.EMERGENCY_LOCK.value)

    # def test_rome_outside_restricted_zone_does_not_lock(self):
    #     controller = SmartMoveCentralController()
    #     vehicle = Vehicle("V5", VehicleType.SCOOTER, City.ROME)
    #     user = type("User", (), {"id": "U5"})()

    #     controller.start_rental(user, vehicle)

    #     event = TelemetryEvent(
    #         vehicle.id,
    #         city=City.ROME,
    #         latitude=41.0,
    #         longitude=0.0,
    #         speed=0,
    #         battery=100,
    #         temperature=30,
    #         timestamp=datetime.now()
    #     )

    #     controller.process_telemetry_event(vehicle, event)
    #     self.assertEqual(vehicle.state.value, VehicleState.IN_USE.value)


if __name__ == "__main__":
    unittest.main()