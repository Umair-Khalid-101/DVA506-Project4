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
        self.active_rentals = {}  # vehicle_id -> Rental

    # ----------------------------
    # VALIDATION HELPERS
    # ----------------------------
    def _validate_user(self, user):
        if user is None or not getattr(user, "id", None):
            raise Exception("Invalid user")

    def _validate_vehicle(self, vehicle):
        if vehicle is None or not getattr(vehicle, "id", None):
            raise Exception("Invalid vehicle")

    def _user_has_active_rental(self, user_id: str) -> bool:
        return any(r.user_id == user_id for r in self.active_rentals.values())

    # ----------------------------
    # SINGLE STATE TRANSITION GATEWAY
    # ----------------------------
    def transition_vehicle(self, vehicle, target_state: VehicleState, reason: str, telemetry: dict | None = None):
        """
        Single entry-point for ALL vehicle state changes.
        Ensures:
          - state machine validation
          - audit logging
          - rollback on audit failure (in-memory consistency)
        """
        telemetry = telemetry or {}

        with vehicle.lock:
            current_state = vehicle.state

            # Validate via state machine (+ guards)
            if not StateMachine.validate(current_state, target_state, vehicle=vehicle, reason=reason, telemetry=telemetry):
                raise Exception(f"Invalid transition: {current_state.value} -> {target_state.value} ({reason})")

            # Snapshot for rollback
            snapshot = (current_state, vehicle.gps, vehicle.battery, vehicle.temperature)

            try:
                # Apply transition
                vehicle.state = target_state

                # Audit it (LAB requirement)
                self.audit.record(
                    entity_id=vehicle.id,
                    action=f"{current_state.value} -> {target_state.value}",
                    reason=reason
                )
            except Exception:
                # Rollback in-memory if audit fails
                vehicle.state, vehicle.gps, vehicle.battery, vehicle.temperature = snapshot
                raise

    # ----------------------------
    # RENTAL FLOW
    # ----------------------------
    def start_rental(self, user, vehicle):
        self._validate_user(user)
        self._validate_vehicle(vehicle)

        # Prevent one user renting multiple vehicles at once (optional but good)
        if self._user_has_active_rental(user.id):
            raise Exception("User already has an active rental")

        with vehicle.lock:
            if vehicle.state != VehicleState.AVAILABLE:
                raise Exception("Vehicle not available")

            # City rules before unlock
            rules = CITY_RULES[vehicle.city.value]
            rules.on_unlock(vehicle, user)

        # Use transition gateway (re-locks internally; ok, but we avoided holding lock during rules)
        self.transition_vehicle(vehicle, VehicleState.IN_USE, "Rental started")

        rental = Rental(
            rental_id=str(uuid.uuid4()),
            user_id=user.id,
            vehicle_id=vehicle.id
        )

        self.active_rentals[vehicle.id] = rental
        return rental

    def end_rental(self, vehicle):
        self._validate_vehicle(vehicle)

        rental = self.active_rentals.get(vehicle.id)
        if not rental:
            raise Exception("No active rental")

        rental.end()
        rental.cost = PricingEngine.calculate(rental)

        # City-specific billing rules
        rules = CITY_RULES[vehicle.city.value]
        rules.on_end_rental(rental)

        # Remove rental first? (depends)
        # If you want strict consistency, transition + audit first, then delete.
        self.transition_vehicle(vehicle, VehicleState.AVAILABLE, f"Rental ended. Cost: {rental.cost}")

        del self.active_rentals[vehicle.id]
        return rental

    # ----------------------------
    # TELEMETRY HELPERS (optional)
    # ----------------------------
    def has_active_rental(self, vehicle_id: str) -> bool:
        return vehicle_id in self.active_rentals
