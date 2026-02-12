from .factories.vehicle_factory import VehicleFactory
from .factories.user_factory import UserFactory
from .factories.telemetry_factory import TelemetryFactory
from .telemetry_simulator import TelemetrySimulator

from domain.enums import City
from persistence.storage import (
    vehicles_exist,
    users_exist,
    load_vehicles,
    load_users,
    save_vehicles,
    save_users
)


class SimulationEngine:

    def __init__(self, controller):
        self.controller = controller
        self.vehicles = {}
        self.users = {}
        self.telemetry_factory = TelemetryFactory()
        self.telemetry_simulator = None

    # -------------------------
    # Setup world
    # -------------------------
    def bootstrap(self):

        if vehicles_exist():
            print("Loading vehicles from disk")
            self.vehicles = load_vehicles()
        else:
            print("Creating vehicle fleet")
            self.vehicles = VehicleFactory.create_fleet(
                size=10_000,
                city_distribution={
                    City.LONDON: 0.4,
                    City.MILAN: 0.3,
                    City.ROME: 0.3
                }
            )
            save_vehicles(self.vehicles)

        if users_exist():
            print("Loading users from disk")
            self.users = load_users()
        else:
            print("Creating users")
            self.users = UserFactory.create_users(2_000)
            save_users(self.users)

        print("Initializing telemetry for all vehicles")

        for vehicle in self.vehicles.values():
            snapshot = self.telemetry_factory.create_initial(vehicle)
            vehicle.telemetry = snapshot

        print("Telemetry initialized")

    # -------------------------
    # Start telemetry simulation
    # -------------------------
    def start(self):

        self.telemetry_simulator = TelemetrySimulator(
            vehicles=self.vehicles,
            telemetry_factory=self.telemetry_factory,
            controller=self.controller,
            interval=1.0
        )

        self.telemetry_simulator.start()
        print("Telemetry simulation running...")

    # -------------------------
    # Stop simulation
    # -------------------------
    def stop(self):
        if self.telemetry_simulator:
            print("Stopping simulation...")
            self.telemetry_simulator.stop()
            self.telemetry_simulator.join()
            print("Simulation stopped")
