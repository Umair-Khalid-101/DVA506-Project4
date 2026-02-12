from core.controller import SmartMoveCentralController
from simulation.simulation_engine import SimulationEngine
import time


def main():
    controller = SmartMoveCentralController()

    simulation = SimulationEngine(controller)

    simulation.bootstrap()
    simulation.start()


    # Keep the main thread alive while background simulation threads run.
    # TelemetrySimulator and RentalSimulator execute in separate threads.
    # If the main thread exits, the entire program would terminate,
    # stopping all simulation activity.
    #
    # The infinite sleep loop prevents the program from exiting.
    # Pressing Ctrl+C raises a KeyboardInterrupt, which allows us to
    # gracefully stop all simulation threads before shutting down.
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        simulation.stop()


if __name__ == "__main__":
    main()
