from domain.vehicle import Vehicle
from domain.enums import VehicleType, City
from core.cotroller import SmartMoveCentralController
import time

controller = SmartMoveCentralController()

vehicle = Vehicle("V1", VehicleType.SCOOTER, City.LONDON)
user = type("User", (), {"id": "U1"})()

rental = controller.start_rental(user, vehicle)
time.sleep(2)
controller.end_rental(vehicle)
