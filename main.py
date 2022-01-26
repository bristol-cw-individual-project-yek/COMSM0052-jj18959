from cgi import test
import os, sys
import dotenv
import traci
import sumolib
from vehicle_shepherd import VehicleShepherd

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

ENV = dotenv.dotenv_values(".env")


def run_simulation(vehicleIds_to_routes:dict):
    if ("--no-gui" in sys.argv):
        sumoBinary = sumolib.checkBinary("sumo")
    else:
        sumoBinary = sumolib.checkBinary("sumo-gui")
    sumoCmd = [sumoBinary, "-c", ENV["configPath"], "--collision.check-junctions", "--collision.action", "warn"]

    traci.start(sumoCmd)

    vehicle_shepherd = VehicleShepherd()
    vehicle_shepherd.add_vehicles(vehicleIds_to_routes)
    
    step = 0
    while step < 100 and len(vehicle_shepherd.vehicles) > 0:
        traci.simulationStep()
        vIds_to_be_removed = []

        vehicle_shepherd.update_vehicles()
        # Print collisions that are currently happening
        print(traci.simulation.getCollisions())
        
        step += 1
    
    traci.close()


if __name__ == "__main__":
    vehicleIds_to_routes = {
        "aaa"   :   "route_0",
        "bbb"   :   "route_1"
    }
    run_simulation(vehicleIds_to_routes)
