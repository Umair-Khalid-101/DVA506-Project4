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
            old_state, new_state = StateMachine.transition(vehicle, VehicleState.IN_USE)

            self.audit.record(
                vehicle.id,
                f"{old_state.name} -> {new_state.name}",
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

            old_state, new_state = StateMachine.transition(vehicle, VehicleState.AVAILABLE)
            del self.active_rentals[vehicle.id]

            self.audit.record(
                vehicle.id,
                f"{old_state.name} -> {new_state.name}",
                f"Rental ended. Cost: {rental.cost}"
            )

            return rental
    def process_telemetry_event(self, vehicle, event):
        with vehicle.lock:
            print(
            f"[TELEMETRY] "
            f"Vehicle={vehicle.id} | "
            f"Battery={event.battery:.2f}% | "
            f"Temp={event.temperature:.2f}°C"
        )

            if event.temperature > 60:
                print(f"🔥 Overheat detected for {vehicle.id}")

            if event.battery < 5:
                print(f"🔋 Low battery for {vehicle.id}")

