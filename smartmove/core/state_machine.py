from domain.enums import VehicleState

VALID_TRANSITIONS = {
    VehicleState.AVAILABLE: {VehicleState.RESERVED, VehicleState.MAINTENANCE},
    VehicleState.RESERVED: {VehicleState.IN_USE, VehicleState.AVAILABLE},
    VehicleState.IN_USE: {
        VehicleState.AVAILABLE,
        VehicleState.MAINTENANCE,
        VehicleState.EMERGENCY_LOCK
    },
    VehicleState.MAINTENANCE: {VehicleState.AVAILABLE},
    VehicleState.EMERGENCY_LOCK: {VehicleState.MAINTENANCE},
    VehicleState.RELOCATING: {VehicleState.AVAILABLE}
}

class StateMachine:
    @staticmethod
    def validate(current, target):
        return target in VALID_TRANSITIONS.get(current, set())
