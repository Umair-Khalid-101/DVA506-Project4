import threading
import random
import time
from domain.enums import VehicleState


class RentalSimulator(threading.Thread):

    def __init__(self, controller, vehicles, users, interval=2.0):
        super().__init__()
        self.controller = controller
        self.vehicles = vehicles
        self.users = users
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:

            available = [
                v for v in self.vehicles.values()
                if v.state == VehicleState.AVAILABLE
            ]

            print("Available vehicles:", len(available))

            if available:
                vehicle = random.choice(available)
                user = random.choice(list(self.users.values()))

                try:
                    print("Attempting rental for:", vehicle.id)
                    self.controller.start_rental(user, vehicle)
                    print("Rental started successfully.")
                except Exception as e:
                    print("Rental failed:", e)

            time.sleep(2)


    def stop(self):
        self._running = False
