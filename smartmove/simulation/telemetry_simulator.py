import threading
import time


class TelemetrySimulator(threading.Thread):

    def __init__(self, vehicles, telemetry_factory, controller, interval=1.0):
        super().__init__(daemon=False)
        self.vehicles = vehicles
        self.telemetry_factory = telemetry_factory
        self.controller = controller
        self.interval = interval
        self.running = True

    def run(self):
        try:
            while self.running:
                for vehicle in self.vehicles.values():

                    previous_snapshot = vehicle.telemetry

                    snapshot = self.telemetry_factory.next_snapshot(
                        vehicle,
                        previous_snapshot
                    )

                    with vehicle.lock:
                        vehicle.telemetry = snapshot

                    event = self.telemetry_factory.to_event(
                        vehicle,
                        snapshot
                    )

                    self.controller.process_telemetry_event(vehicle, event)

                time.sleep(self.interval)

        except Exception as e:
            print("Telemetry thread crashed:", e)
            raise


    def stop(self):
        self.running = False
