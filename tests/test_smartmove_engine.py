from smartmove.domain.vehicle import Vehicle
from smartmove.domain.enums import VehicleType, City, VehicleState
from smartmove.core.controller import SmartMoveCentralController
from smartmove.core.pricing import PricingEngine
from smartmove.domain.telemetry_event import TelemetryEvent
from datetime import datetime
import time
import unittest

class TestSmartMoveEngine(unittest.TestCase):

    def test_rental_price(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V1", VehicleType.SCOOTER, City.LONDON)
        user = type("User", (), {"id": "U1"})()
        priceEngine = PricingEngine()
        rental = controller.start_rental(user, vehicle)
        time.sleep(2)
        controller.end_rental(vehicle)
        assert priceEngine.calculate(rental) == 0.01
        pass

    def test_low_battery_during_trip(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V2", VehicleType.SCOOTER, City.LONDON)
        user = type("User", (), {"id": "U2"})()
        rental = controller.start_rental(user, vehicle)
        date = datetime.now()
        event = TelemetryEvent(vehicle.id, city=City.LONDON, latitude=0.0, longitude=0.0, speed=0, battery=4, temperature=30, timestamp=date)
        controller.process_telemetry_event(vehicle, event)
        assert(vehicle.state.value == VehicleState.MAINTENANCE.value)
        pass

    def test_emergency_lock_theft_detection(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V3", VehicleType.SCOOTER, City.LONDON)
        date = datetime.now()
        event = TelemetryEvent(vehicle.id, city=City.LONDON, latitude=0.0, longitude=0.0, speed=2, battery=100, temperature=30, timestamp=date)
        controller.process_telemetry_event(vehicle, event)
        assert(vehicle.state.value == VehicleState.EMERGENCY_LOCK.value)
        pass

    def test_overheating_during_trip(self):
        controller = SmartMoveCentralController()
        vehicle = Vehicle("V2", VehicleType.SCOOTER, City.LONDON)
        user = type("User", (), {"id": "U2"})()
        rental = controller.start_rental(user, vehicle)
        date = datetime.now()
        event = TelemetryEvent(vehicle.id, city=City.LONDON, latitude=0.0, longitude=0.0, speed=0, battery=100, temperature=61, timestamp=date)
        controller.process_telemetry_event(vehicle, event)
        assert(vehicle.state.value == VehicleState.EMERGENCY_LOCK.value)
        pass
    
if __name__ == "__main__":
    unittest.main()