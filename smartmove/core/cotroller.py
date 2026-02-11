from core.state_machine import StateMachine
from persistence.audit_log import AuditLog
from rules.london import LondonRules
from rules.milan import MilanRules
from rules.rome import RomeRules
from core.pricing import PricingEngine
from domain.enums import VehicleState
from domain.rental import Rental
import uuid

CITY_RULES = {
    "london": LondonRules(),
    "milan": MilanRules(),
    "rome": RomeRules()
}

class SmartMoveCentralController:
    def __init__(self):
        self.audit = AuditLog()
        self.active_rentals = {}


    def start_rental(self, user, vehicle):
        with vehicle.lock:
            if vehicle.state != VehicleState.AVAILABLE:
                raise Exception("Vehicle not available")

            # City rules before unlock
            rules = CITY_RULES[vehicle.city.value]
            rules.on_unlock(vehicle, user)

            vehicle.state = VehicleState.IN_USE

            rental = Rental(
                rental_id=str(uuid.uuid4()),
                user_id=user.id,
                vehicle_id=vehicle.id
            )

            self.active_rentals[vehicle.id] = rental

            self.audit.record(
                vehicle.id,
                "AVAILABLE -> IN_USE",
                "Rental started"
            )

            return rental

    def end_rental(self, vehicle):
        with vehicle.lock:
            rental = self.active_rentals.get(vehicle.id)
            if not rental:
                raise Exception("No active rental")

            rental.end()
            rental.cost = PricingEngine.calculate(rental)

            # City-specific billing rules
            rules = CITY_RULES[vehicle.city.value]
            rules.on_end_rental(rental)

            vehicle.state = VehicleState.AVAILABLE
            del self.active_rentals[vehicle.id]

            self.audit.record(
                vehicle.id,
                "IN_USE -> AVAILABLE",
                f"Rental ended. Cost: {rental.cost}"
            )

            return rental
