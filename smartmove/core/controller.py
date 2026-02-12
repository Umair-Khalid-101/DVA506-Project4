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

            current_state = vehicle.state

            # Do nothing if already in maintenance
            if current_state == VehicleState.MAINTENANCE:
                return

            # --------------------------------------------------
            # Unauthorized movement (theft detection)
            # --------------------------------------------------
            if current_state != VehicleState.IN_USE and event.speed > 1:

                if StateMachine.validate(current_state, VehicleState.EMERGENCY_LOCK):

                    old, new = StateMachine.transition(
                        vehicle,
                        VehicleState.EMERGENCY_LOCK
                    )

                    self.audit.record(
                        vehicle.id,
                        f"{old.name} -> {new.name}",
                        "Emergency lock: Unauthorized movement detected"
                    )

                return

            # --------------------------------------------------
            # Overheating
            # --------------------------------------------------
            if event.temperature > 60:

                if current_state == VehicleState.IN_USE:

                    old, new = StateMachine.transition(
                        vehicle,
                        VehicleState.EMERGENCY_LOCK
                    )

                    self.audit.record(
                        vehicle.id,
                        f"{old.name} -> {new.name}",
                        "Emergency lock: Overheating detected"
                    )

                    # Terminate rental if active
                    rental = self.active_rentals.get(vehicle.id)
                    if rental:
                        rental.end()
                        del self.active_rentals[vehicle.id]

                return

            # --------------------------------------------------
            # Critical low battery
            # --------------------------------------------------
            if event.battery < 5:

                # If rental active, terminate first
                if current_state == VehicleState.IN_USE:
                    rental = self.active_rentals.get(vehicle.id)
                    if rental:
                        rental.end()
                        del self.active_rentals[vehicle.id]

                # Move to maintenance if allowed
                if StateMachine.validate(vehicle.state, VehicleState.MAINTENANCE):

                    old, new = StateMachine.transition(
                        vehicle,
                        VehicleState.MAINTENANCE
                    )

                    self.audit.record(
                        vehicle.id,
                        f"{old.name} -> {new.name}",
                        "Maintenance required: Battery critically low"
                    )

                return

            # --------------------------------------------------
            # Recovery from emergency lock (optional behavior)
            # --------------------------------------------------
            if current_state == VehicleState.EMERGENCY_LOCK:

                # If conditions are normal again, move to maintenance
                if event.temperature <= 60 and event.battery >= 5:

                    if StateMachine.validate(current_state, VehicleState.MAINTENANCE):

                        old, new = StateMachine.transition(
                            vehicle,
                            VehicleState.MAINTENANCE
                        )

                        self.audit.record(
                            vehicle.id,
                            f"{old.name} -> {new.name}",
                            "Emergency resolved, moved to maintenance"
                        )

                return


