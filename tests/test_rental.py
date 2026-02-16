from smartmove.domain.vehicle import Vehicle
from smartmove.domain.enums import VehicleType, City
from smartmove.core.controller import SmartMoveCentralController
from smartmove.core.pricing import PricingEngine
import time

def test_rental_price():
    controller = SmartMoveCentralController()

    vehicle = Vehicle("V1", VehicleType.SCOOTER, City.LONDON)
    user = type("User", (), {"id": "U1"})()

    rental = controller.start_rental(user, vehicle)
    time.sleep(2)
    controller.end_rental(vehicle)

    priceEngine = PricingEngine()

    assert priceEngine.calculate(rental) == 0.01