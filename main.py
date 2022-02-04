from cgi import test
import os, sys
from time import time
import dotenv
import network.network as ntwk
import traci
import sumolib
import vehicle
from vehicle import vehicle_shepherd

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

ENV = dotenv.dotenv_values(".env")


def run_simulation(vehicleIds_to_routes:dict):
    temp_file_name = "tmp_" + str(round(time()))
    road_network = ntwk.Network()
    path = road_network.generateNetwork(temp_file_name)
    if ("--no-gui" in sys.argv):
        sumoBinary = sumolib.checkBinary("sumo")
    else:
        sumoBinary = sumolib.checkBinary("sumo-gui")
    sumoCmd = [sumoBinary, "-c", path, "--collision.check-junctions", "--collision.action", "warn"]

    print(sumoCmd)

    traci.start(sumoCmd)

    shepherd = vehicle_shepherd.VehicleShepherd()
    shepherd.add_vehicles(vehicleIds_to_routes)
    
    step = 0
    while step < 100 and len(shepherd.vehicles) > 0:
        traci.simulationStep()

        shepherd.update_vehicles()
        # Print collisions that are currently happening
        #print(traci.simulation.getCollisions())
        
        step += 1
    
    traci.close()


if __name__ == "__main__":
    vehicleIds_to_routes = {
        "aaa"   :   "route_0",
        "bbb"   :   "route_1"
    }
    run_simulation(vehicleIds_to_routes)
