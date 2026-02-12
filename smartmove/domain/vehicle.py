from domain.enums import VehicleState, VehicleType
import threading

class Vehicle:
    def __init__(self, vehicle_id, vtype, city):
        self.id = vehicle_id
        self.type = vtype
        self.city = city
        self.state = VehicleState.AVAILABLE
        
        self.gps = (0.0, 0.0)
        self.battery = 100
        self.temperature = 25
        
        # Critical for concurrency
        self.lock = threading.Lock()
        self.helmet_present = True


    def is_in_use(self):
         return self.state == VehicleState.IN_USE
