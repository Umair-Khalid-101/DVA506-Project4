from domain.enums import VehicleState

VALID_TRANSITIONS = {
    VehicleState.AVAILABLE: {VehicleState.RESERVED, VehicleState.MAINTENANCE, VehicleState.RELOCATING},
    VehicleState.RESERVED: {VehicleState.IN_USE, VehicleState.AVAILABLE},
    VehicleState.IN_USE: {VehicleState.AVAILABLE, VehicleState.MAINTENANCE, VehicleState.EMERGENCY_LOCK},
    VehicleState.MAINTENANCE: {VehicleState.AVAILABLE},
    VehicleState.EMERGENCY_LOCK: {VehicleState.MAINTENANCE},
    VehicleState.RELOCATING: {VehicleState.AVAILABLE}
}

class StateMachine:
    """
    Validates vehicle state transitions.
    This class does NOT mutate the vehicle; it only checks if a transition is allowed.

    In addition to the transition graph, it applies LAB-required guard conditions:
      - MAINTENANCE: allowed only when fault is present OR battery is low.
      - EMERGENCY_LOCK: allowed only when overheating OR theft alarm is detected.
    """

    # You can document these thresholds in your PDF
    MAINTENANCE_BATTERY_THRESHOLD = 10     # <=10% can enter Maintenance
    BATTERY_CRITICAL_THRESHOLD = 5         # <5% used for "critical" actions (telemetry)
    OVERHEAT_TEMP_THRESHOLD = 60           # >60°C triggers emergency lock

    @staticmethod
    def validate(current, target, *, vehicle=None, reason: str = "", telemetry: dict | None = None) -> bool:
        # 1) Basic transition edge validation
        if target not in VALID_TRANSITIONS.get(current, set()):
            return False

        telemetry = telemetry or {}
        reason_l = (reason or "").lower()

        # If vehicle is not provided, we can only validate the graph
        if vehicle is None:
            return True

        # 2) Guard: entering MAINTENANCE requires fault or low battery
        if target == VehicleState.MAINTENANCE:
            battery = getattr(vehicle, "battery", None)
            fault = bool(telemetry.get("fault", False))

            low_battery = (
                battery is not None
                and battery <= StateMachine.MAINTENANCE_BATTERY_THRESHOLD
            )

            # Allow if fault/low battery OR reason text indicates relevant condition
            if not (fault or low_battery or "battery" in reason_l or "fault" in reason_l):
                return False

        # 3) Guard: entering EMERGENCY_LOCK requires overheating or theft
        if target == VehicleState.EMERGENCY_LOCK:
            temp = getattr(vehicle, "temperature", None)
            theft = bool(telemetry.get("theft", False))

            overheating = (
                temp is not None
                and temp > StateMachine.OVERHEAT_TEMP_THRESHOLD
            )

            if not (overheating or theft or "overheat" in reason_l or "theft" in reason_l):
                return False

        return True
