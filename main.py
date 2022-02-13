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
from vehicle import vehicle_shepherd
import yaml

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

ENV = dotenv.dotenv_values(".env")
try: 
    with open("config.yaml", "r") as stream:
        CONFIG = yaml.safe_load(stream)
except:
    pass


def get_network():
    try:
        if CONFIG["network-type"] == "random":
            network = ntwk.Network(CONFIG["random-settings"])
        elif CONFIG["network-type"] == "grid":
            network = grid.GridNetwork(CONFIG["grid-settings"])
        elif CONFIG["network-type"] == "spider":
            network = spider.SpiderNetwork(CONFIG["spider-settings"])
        return network
    except:
        pass


def run_simulation(has_gui:bool=False):
    temp_file_name = "tmp_" + str(round(time()))
    road_network:ntwk.Network = get_network()
    route_steps = CONFIG["steps"]
    path = road_network.generateFile(temp_file_name)
    if not has_gui:
        sumoBinary = sumolib.checkBinary("sumo")
    else:
        sumoBinary = sumolib.checkBinary("sumo-gui")
    sumoCmd = [sumoBinary, "-c", path, "--collision.check-junctions", "--collision.action", "warn"]

    print(sumoCmd)

    traci.start(sumoCmd)

    shepherd = vehicle_shepherd.VehicleShepherd(road_network)
    shepherd.add_vehicles(CONFIG["vehicle-groups"], road_network.routeIds)
    print(shepherd.vehicles)
    
    step = 0
    while step < route_steps and len(shepherd.vehicles) > 0:
        traci.simulationStep()

        shepherd.update_vehicles()
        # Print collisions that are currently happening
        #print(traci.simulation.getCollisions())
        
        step += 1
    
    traci.close()
    shutil.rmtree("temp")


if __name__ == "__main__":
    print(CONFIG)
    # TODO: Replace w/ config
    if "--gui" in sys.argv:
        run_simulation(has_gui=True)
    else:
        run_simulation(has_gui=False)
