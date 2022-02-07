from cgi import test
import os, sys
import shutil
from time import time
import dotenv
import network.network as ntwk
import network.grid_network as grid
import network.spider_network as spider
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


def run_simulation(vehicleIds_to_routes:dict, has_gui:bool=False):
    temp_file_name = "tmp_" + str(round(time()))
    road_network = grid.GridNetwork()
    path = road_network.generateFile(temp_file_name)
    if not has_gui:
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
    shutil.rmtree("temp")


if __name__ == "__main__":
    # TODO: Replace w/ config
    vehicleIds_to_routes = {
        "aaa"   :   "r0",
    }
    if "--gui" in sys.argv:
        run_simulation(vehicleIds_to_routes, has_gui=True)
    else:
        run_simulation(vehicleIds_to_routes, has_gui=False)
