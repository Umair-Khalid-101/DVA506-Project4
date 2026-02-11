from domain.enums import VehicleState

class TelemetryProcessor:
    def __init__(self, controller):
        self.controller = controller

    def process(self, vehicle, data: dict):
        # Update telemetry safely
        with vehicle.lock:
            vehicle.gps = data["gps"]
            vehicle.battery = data["battery"]
            vehicle.temperature = data["temperature"]

        # LAB rules: overheating => emergency lock (only makes sense if moved/active rental etc.)
        if vehicle.temperature > 60:
            self.controller.transition_vehicle(
                vehicle,
                VehicleState.EMERGENCY_LOCK,
                "Overheating",
                telemetry={"overheat": True}
            )

        # LAB: battery critical => maintenance (you can choose threshold for maintenance)
        if vehicle.battery < 5:
            self.controller.transition_vehicle(
                vehicle,
                VehicleState.MAINTENANCE,
                "Battery critical",
                telemetry={"battery_critical": True}
            )

        # Theft alarm example: moved without active rental
        moved = data.get("moved_meters", 0)
        if moved > 0 and not self.controller.has_active_rental(vehicle.id):
            self.controller.transition_vehicle(
                vehicle,
                VehicleState.EMERGENCY_LOCK,
                "Theft alarm: movement without active rental",
                telemetry={"theft": True}
            )
