from core.controller import SmartMoveCentralController
from simulation.simulation_engine import SimulationEngine
import time


def main():
    controller = SmartMoveCentralController()

    simulation = SimulationEngine(controller)

    simulation.bootstrap()
    simulation.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        simulation.stop()


if __name__ == "__main__":
    main()
