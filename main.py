import os, sys
import shutil
from time import time
import dotenv
import src.network.network as ntwk
import src.network.grid_network as grid
import src.network.spider_network as spider
import traci
import sumolib
from src.vehicle import vehicle_shepherd
import yaml
from src.logger.logger import Logger
from traci._simulation import Collision
import src.maps.map_builder as map_builder
from src.maps.bounding_box import BoundingBox
from src.stats.metric_calculator import MetricCalculator

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
        route_seed = CONFIG["route-seed"]
    except KeyError:
        route_seed = 0
    try:
        if CONFIG["network-type"] == "local":
            network = ntwk.Network({}, route_seed=route_seed, network_file_path=CONFIG["network-file-path"])
        elif CONFIG["network-type"] == "osm":
            osm_settings = CONFIG["osm-area-settings"]
            origin_lat = osm_settings["origin-latitude"]
            origin_long = osm_settings["origin-longitude"]
            width = osm_settings["width"]
            height = osm_settings["height"]
            bbox:BoundingBox = BoundingBox.from_origin(origin_lat=origin_lat, origin_long=origin_long, width=width, height=height)

            # TODO: Decouple this, as well as the one in network/network.py
            if not os.path.exists(ntwk.Network.TEMP_FILE_DIRECTORY):
                os.makedirs(ntwk.Network.TEMP_FILE_DIRECTORY)
            osm_path = map_builder.get_osm_area(bbox, f"{ntwk.Network.TEMP_FILE_DIRECTORY}/results")
            file_path = map_builder.build_map_from_osm(osm_path)
            network = ntwk.Network({}, route_seed=route_seed, network_file_path=file_path)
        elif CONFIG["network-type"] == "random":
            network = ntwk.Network(CONFIG["random-settings"], route_seed=route_seed)
        elif CONFIG["network-type"] == "grid":
            network = grid.GridNetwork(CONFIG["grid-settings"], route_seed=route_seed)
        elif CONFIG["network-type"] == "spider":
            network = spider.SpiderNetwork(CONFIG["spider-settings"], route_seed=route_seed)
    except KeyError as e:
        print("Key missing from config.yaml: " + str(e))
        raise(e)
    except Exception as e:
        raise e
    return network


def run_simulation(has_gui:bool=False, log_data:bool=False):
    shutil.rmtree("temp", ignore_errors=True)
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
    shepherd.add_vehicle_types(CONFIG["vehicle-types"])
    shepherd.add_vehicles(CONFIG["vehicle-groups"], road_network.routeIds)

    vehicle_metadata = shepherd.get_vehicle_metadata()
    
    step = 0
    data = {}
    collision_data = {}
    num_of_collisions = 0
    while step < route_steps and len(shepherd.vehicles) > 0:
        data[step] = shepherd.update_vehicles()
        traci.simulationStep()
        # Print collisions that are currently happening
        collisions = traci.simulation.getCollisions()
        collisionDict = {}
        for i in range(len(collisions)):
            collision: Collision = collisions[i]
            collisionDict[i] = {
                "collider"      : collision.collider,
                "victim"        : collision.victim,
                "collisionType" : collision.type,
                "lane"          : collision.lane,
                "pos"           : collision.pos
            }
        if len(collisionDict) > 0:
            # TODO: Handle duplicate collisions
            collision_data[step] = collisionDict
            num_of_collisions += len(collisionDict)
        step += 1
    
    traci.close()

    metrics = {
        "wait_time_metrics"  : MetricCalculator.calculate(vehicles=shepherd.vehicles),
        "num_of_collisions" : num_of_collisions
    }

    print(metrics)

    if log_data:
        Logger.log_data_as_json(config_data=CONFIG, step_data=data, network=road_network, collision_data=collision_data, vehicle_metadata=vehicle_metadata, metrics=metrics)
    shutil.rmtree("temp")


def test_osm_get():
    map_builder.get_osm_area(BoundingBox(-2.65, 51, -2.5943, 52), "test_files/results")


if __name__ == "__main__":
    # TODO: Replace w/ config(?)
    has_gui = False
    log_data = True
    if "--gui" in sys.argv:
        has_gui = True
    if "--log" in sys.argv:
        log_data = True
    run_simulation(has_gui=has_gui, log_data=log_data)
