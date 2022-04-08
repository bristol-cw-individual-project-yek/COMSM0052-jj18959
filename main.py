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


def display_metrics(metrics:dict):
    print("\n------------RESULTS------------\n")
    collision_str = "Number of collisions: " + str(metrics["num_of_collisions"])
    total_wait_time_stats:dict = metrics["wait_time_metrics"]["total-wait-time"]
    tw_mean = total_wait_time_stats["mean"]
    tw_median = total_wait_time_stats["median"]
    tw_min = total_wait_time_stats["min"]
    tw_max = total_wait_time_stats["max"]
    tw_skew = total_wait_time_stats["skew"]
    tw_kurtosis = total_wait_time_stats["kurtosis"]
    total_wait_time_str = f"""
Total wait time stats:
    Mean    :   {tw_mean}
    Median  :   {tw_median} 
    Min     :   {tw_min} 
    Max     :   {tw_max} 
    Skew    :   {tw_skew}
    Kurtosis:   {tw_kurtosis}
    """
    wait_time_per_junction_stats:dict = metrics["wait_time_metrics"]["wait-times-per-junction"]
    wt_mean = wait_time_per_junction_stats["mean"]
    wt_median = wait_time_per_junction_stats["median"]
    wt_min = wait_time_per_junction_stats["min"]
    wt_max = wait_time_per_junction_stats["max"]
    wt_skew = wait_time_per_junction_stats["skew"]
    wt_kurtosis = wait_time_per_junction_stats["kurtosis"]
    wait_time_per_junction_str = f"""
Wait time per junction stats:
    Mean    :   {wt_mean}
    Median  :   {wt_median} 
    Min     :   {wt_min} 
    Max     :   {wt_max} 
    Skew    :   {wt_skew} 
    Kurtosis:   {wt_kurtosis} 
    """
    print(collision_str + "\n" + total_wait_time_str + "\n" + wait_time_per_junction_str)
    print("-------------------------------")


def run_simulation(has_gui:bool=False, log_data:bool=False, number_of_runs:int=1):
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
    ongoing_collisions = {}

    num_of_collisions = 0
    while step < route_steps and len(shepherd.vehicles) > 0:
        data[step] = shepherd.update_vehicles()
        traci.simulationStep()

        # Collect data on any collisions that are happening
        collisions = traci.simulation.getCollisions()
        collisionDict = {}
        for i in range(len(collisions)):
            collision: Collision = collisions[i]
            collisionId = collision.collider + "-" + collision.victim
            collisionDict[collisionId] = {
                "collider"      : collision.collider,
                "victim"        : collision.victim,
                "collisionType" : collision.type,
                "lane"          : collision.lane,
                "pos"           : collision.pos
            }

        # Remove duplicate collisions
        # This isn't perfect, but it gets rid of the majority of duplicate collisions
        toBeRemoved = []
        for collisionId in ongoing_collisions:
            cId:str = collisionId
            colliderAndVictim = cId.split("-")
            cIdAlt = colliderAndVictim[1] + "-" + colliderAndVictim[0]
            if cId in collisionDict:
                collisionDict.pop(cId)
            else:
                toBeRemoved.append(cId)
            if cIdAlt in collisionDict:
                collisionDict.pop(cIdAlt)
            else:
                toBeRemoved.append(cIdAlt)
        for c in toBeRemoved:
            ongoing_collisions.pop(c, "")
        
        # If there are any collisions left, record them
        if len(collisionDict) > 0:
            collision_data[step] = collisionDict

            # This is to remove duplicate collisions
            ongoing_collisions.update(collisionDict)

            num_of_collisions += len(collisionDict)
        step += 1
    
    traci.close()

    metrics = {
        "wait_time_metrics"  : MetricCalculator.calculate(vehicles=shepherd.vehicles),
        "num_of_collisions" : num_of_collisions
    }

    display_metrics(metrics)

    if log_data:
        Logger.log_data_as_json(config_data=CONFIG, step_data=data, network=road_network, collision_data=collision_data, vehicle_metadata=vehicle_metadata, metrics=metrics)
    shutil.rmtree("temp")


def test_osm_get():
    map_builder.get_osm_area(BoundingBox(-2.65, 51, -2.5943, 52), "test_files/results")


if __name__ == "__main__":
    # TODO: Replace w/ config(?)
    has_gui = True
    log_data = True
    number_of_runs = 1
    
    for arg in sys.argv:
        if arg == "--no-gui":
            has_gui = False
        elif arg == "--no-log":
            log_data = False
        elif arg.startswith("-n=") or arg.startswith("--number="):
            try:
                arg_elems = arg.split("=")
                assert(len(arg_elems) == 2)
                number_of_runs = int(arg_elems[1])
            except Exception as e:
                raise e
        elif arg != "python" and arg != "main.py":
            raise ValueError(f"Unknown argument: {arg}")
    run_simulation(has_gui=has_gui, log_data=log_data, number_of_runs=number_of_runs)
