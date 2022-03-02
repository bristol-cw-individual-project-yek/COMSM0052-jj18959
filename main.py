from cgi import test
from datetime import date, datetime
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
import json

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
        stream.close()
except:
    pass


def get_network():
    try:
        if CONFIG["network-type"] == "random":
            network = ntwk.Network(CONFIG["random-settings"], route_seed=CONFIG["route-seed"])
        elif CONFIG["network-type"] == "grid":
            network = grid.GridNetwork(CONFIG["grid-settings"], route_seed=CONFIG["route-seed"])
        elif CONFIG["network-type"] == "spider":
            network = spider.SpiderNetwork(CONFIG["spider-settings"], route_seed=CONFIG["route-seed"])
        return network
    except:
        pass


def run_simulation(has_gui:bool=False, log_data:bool=False):
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

    shepherd = vehicle_shepherd.VehicleShepherd(road_network, log_data=log_data)
    shepherd.add_vehicle_types(CONFIG["vehicle-types"])
    shepherd.add_vehicles(CONFIG["vehicle-groups"], road_network.routeIds)
    print(shepherd.vehicles)
    
    step = 0
    data = {}
    while step < route_steps and len(shepherd.vehicles) > 0:
        traci.simulationStep()

        if log_data:
            data[step] = shepherd.update_vehicles()
        # Print collisions that are currently happening
        #print(traci.simulation.getCollisions())
        
        step += 1
    
    traci.close()
    if log_data:
        log_data_as_json(step_data=data, network=road_network)
    shutil.rmtree("temp")


def log_data_as_json(step_data:dict, network:ntwk.Network, filename=""):
    network_data = network.getData()
    data = {
        "network_data"          : network_data,
        "steps"                 : CONFIG["steps"],
        "vehicle_group_data"    : CONFIG["vehicle-groups"],
        "vehicle_type_data"     : CONFIG["vehicle-types"],
        "step_data"             : step_data,
    }
    data["network_data"]["network_type"] = CONFIG["network-type"]
    directory_name = "logs"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    if filename == "":
        filename = datetime.today().isoformat().replace(":", "-", -1).split(".")[0]
    if not filename.endswith(".json"):
        filename += ".json"
    with open(directory_name + "/" + filename, "w") as f:
        f.write(json.dumps(data, indent=4))
        f.close()


if __name__ == "__main__":
    # TODO: Replace w/ config(?)
    has_gui = False
    log_data = True
    if "--gui" in sys.argv:
        has_gui = True
    if "--log" in sys.argv:
        log_data = True
    run_simulation(has_gui=has_gui, log_data=log_data)
