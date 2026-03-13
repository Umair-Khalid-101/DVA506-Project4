from core.state_machine import StateMachine
from domain.enums import VehicleState
from rules.london import LondonRules
from rules.milan import MilanRules
from rules.rome import RomeRules


CITY_RULES = {
    "london": LondonRules(),
    "milan": MilanRules(),
    "rome": RomeRules()
}


class TelemetryService:
    """
    Handles telemetry-driven lifecycle logic.
    """

    def __init__(self, vehicles, audit_log, active_rentals, rental_service):
        self.vehicles = vehicles
        self.audit = audit_log
        self.active_rentals = active_rentals
        self.rental_service = rental_service

    def process_telemetry_by_id(self, vehicle_id, event):
        vehicle = self.vehicles[vehicle_id]
        self.process_telemetry_event(vehicle, event)

    def process_telemetry_event(self, vehicle, event):
        with vehicle.lock:
            current_state = vehicle.state

            # keep vehicle runtime telemetry in sync
            vehicle.gps = (event.latitude, event.longitude)
            vehicle.battery = event.battery
            vehicle.temperature = event.temperature

            # maintenance vehicles remain isolated from regular telemetry flow
            if current_state == VehicleState.MAINTENANCE:
                return

            rules = CITY_RULES[vehicle.city.value]

            # Unauthorized movement: movement without active usage
            if current_state != VehicleState.IN_USE and event.speed > 1:
                if StateMachine.validate(current_state, VehicleState.EMERGENCY_LOCK):
                    old_state, new_state = StateMachine.transition(
                        vehicle,
                        VehicleState.EMERGENCY_LOCK
                    )
                    self.audit.record(
                        entity_id=vehicle.id,
                        action=f"{old_state.name} -> {new_state.name}",
                        reason="Emergency lock: Unauthorized movement detected"
                    )
                return

            # City-specific movement validation (Rome restricted zone etc.)
            if event.speed > 0:
                is_valid = rules.validate_movement(vehicle)
                if not is_valid and current_state == VehicleState.IN_USE:
                    if StateMachine.validate(current_state, VehicleState.EMERGENCY_LOCK):
                        old_state, new_state = StateMachine.transition(
                            vehicle,
                            VehicleState.EMERGENCY_LOCK
                        )

                        self.audit.record(
                            entity_id=vehicle.id,
                            action=f"{old_state.name} -> {new_state.name}",
                            reason="Emergency lock: Restricted zone entered"
                        )

                        self.rental_service.terminate_active_rental(
                            vehicle,
                            "Rental terminated due to restricted zone entry"
                        )
                    return

            # Overheating
            if event.temperature > 60 and current_state == VehicleState.IN_USE:
                old_state, new_state = StateMachine.transition(
                    vehicle,
                    VehicleState.EMERGENCY_LOCK
                )

                self.audit.record(
                    entity_id=vehicle.id,
                    action=f"{old_state.name} -> {new_state.name}",
                    reason="Emergency lock: Overheating detected"
                )

                self.rental_service.terminate_active_rental(
                    vehicle,
                    "Rental terminated due to overheating"
                )
                return

            # Critical battery
            if event.battery < 5:
                if current_state == VehicleState.IN_USE:
                    self.rental_service.terminate_active_rental(
                        vehicle,
                        "Rental terminated due to critically low battery"
                    )

                if StateMachine.validate(vehicle.state, VehicleState.MAINTENANCE):
                    old_state, new_state = StateMachine.transition(
                        vehicle,
                        VehicleState.MAINTENANCE
                    )

                    self.audit.record(
                        entity_id=vehicle.id,
                        action=f"{old_state.name} -> {new_state.name}",
                        reason="Maintenance required: Battery critically low"
                    )
                return

            # Recovery from emergency lock
            if current_state == VehicleState.EMERGENCY_LOCK:
                if event.temperature <= 60 and event.battery >= 5:
                    if StateMachine.validate(current_state, VehicleState.MAINTENANCE):
                        old_state, new_state = StateMachine.transition(
                            vehicle,
                            VehicleState.MAINTENANCE
                        )
                        self.audit.record(
                            entity_id=vehicle.id,
                            action=f"{old_state.name} -> {new_state.name}",
                            reason="Emergency resolved, moved to maintenance"
                        )