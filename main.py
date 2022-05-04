import os, sys
import random
import shutil
from time import time
import dotenv
import src.road_network.road_network as ntwk
import src.road_network.grid_network as grid
import src.road_network.spider_network as spider
import traci
import sumolib
from src import simulation_manager
import yaml
from src.logger.logger import Logger
from traci._simulation import Collision
import src.maps.map_builder as map_builder
from src.maps.bounding_box import BoundingBox
from src.stats.metric_calculator import MetricCalculator
import src.arbiter.arbiter as arbiter

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
    raise

SCENARIO_FOLDER_PATH = "scenarios"


def get_random_seed():
    try:
        return int(CONFIG["seed"])
    except KeyError:
        return 0


def get_network(seed=None):
    if not seed:
        seed = get_random_seed()
    try:
        if CONFIG["network-type"] == "yaml":
            try:
                scenario_name:str = CONFIG["scenario-name"]
                if not scenario_name.endswith(".yaml"):
                    scenario_name += ".yaml"
            except KeyError:
                raise
            network = ntwk.RoadNetwork({}, seed=seed, scenario_file_path=SCENARIO_FOLDER_PATH + "\\" + scenario_name)
        elif CONFIG["network-type"] == "local":
            try:
                network_file_path = CONFIG["network-file-path"]
            except KeyError:
                raise
            try:
                route_file_path = CONFIG["route-file-path"]
                network = ntwk.RoadNetwork({}, seed=seed, network_file_path=network_file_path, route_file_path=route_file_path)
            except KeyError:
                network = ntwk.RoadNetwork({}, seed=seed, network_file_path=network_file_path)
        elif CONFIG["network-type"] == "osm":
            osm_settings = CONFIG["osm-area-settings"]
            origin_lat = osm_settings["origin-latitude"]
            origin_long = osm_settings["origin-longitude"]
            width = osm_settings["width"]
            height = osm_settings["height"]
            bbox:BoundingBox = BoundingBox.from_origin(origin_lat=origin_lat, origin_long=origin_long, width=width, height=height)

            # TODO: Decouple this, as well as the one in network/network.py
            if not os.path.exists(ntwk.RoadNetwork.TEMP_FILE_DIRECTORY):
                os.makedirs(ntwk.RoadNetwork.TEMP_FILE_DIRECTORY)
            osm_path = map_builder.get_osm_area(bbox, f"{ntwk.RoadNetwork.TEMP_FILE_DIRECTORY}/results")
            file_path = map_builder.build_map_from_osm(osm_path)
            network = ntwk.RoadNetwork({}, seed=seed, network_file_path=file_path)
        elif CONFIG["network-type"] == "random":
            network = ntwk.RoadNetwork(CONFIG["random-settings"], seed=seed)
        elif CONFIG["network-type"] == "grid":
            network = grid.GridNetwork(CONFIG["grid-settings"], seed=seed)
        elif CONFIG["network-type"] == "spider":
            network = spider.SpiderNetwork(CONFIG["spider-settings"], seed=seed)
    except KeyError as e:
        print("Key missing from config.yaml: " + str(e))
        raise(e)
    except Exception as e:
        raise e
    return network


def run_simulation(has_gui:bool=False, log_data:bool=False, number_of_runs:int=1, entry_name:str=""):
    shutil.rmtree("temp", ignore_errors=True)
    temp_file_name = "tmp_" + str(round(time()))
    route_steps = CONFIG["steps"]
    seed:int = get_random_seed()
    rng:random.Random = random.Random()
    rng.seed(seed)
    if log_data:
        folder_name:str = Logger.create_data_folder(entry_name)
    used_seeds:list = []

    all_metrics_list = []
    total_collisions = 0

    for simulation_number in range(number_of_runs):
        if number_of_runs > 1:
            run_seed = rng.randint(0, 1000000000)
        else:
            run_seed = seed
        road_network:ntwk.RoadNetwork = get_network(run_seed)
        path = road_network.generateFile(temp_file_name, route_seed=run_seed)
        if not has_gui or number_of_runs > 1:
            sumoBinary = sumolib.checkBinary("sumo")
        else:
            sumoBinary = sumolib.checkBinary("sumo-gui")
        sumoCmd = [sumoBinary, "-c", path, "--collision.check-junctions", "--collision.action", "warn"]
        print(sumoCmd)

        traci.start(sumoCmd)

        shepherd = simulation_manager.SimulationManager(road_network, seed=run_seed)
        shepherd.add_vehicle_types(CONFIG["vehicle-types"])
        shepherd.add_vehicles(CONFIG["vehicle-groups"])
        if "arbiters" in CONFIG:
            shepherd.add_arbiters(CONFIG["arbiters"])

        vehicle_metadata = shepherd.get_vehicle_metadata()
        
        data = {}
        collision_data = {}
        ongoing_collisions = {}
        num_of_collisions = 0

        # Perform at least one step in the simulation
        step = 1
        data[step] = shepherd.update()
        traci.simulationStep()
        while step < route_steps and shepherd.has_active_vehicles():
            data[step] = shepherd.update()
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
        total_collisions += num_of_collisions

        all_metrics_list.append(metrics)
        Logger.get_overview_string(metrics, seeds=run_seed)
        used_seeds.append(run_seed)
        if log_data:
            Logger.log_data_as_json(config_data=CONFIG, step_data=data, network=road_network, collision_data=collision_data, entry_folder_name=folder_name, vehicle_metadata=vehicle_metadata, metrics=metrics, simulation_number=simulation_number)
    shutil.rmtree("temp")
    metrics_entire_set = {
        "wait_time_metrics"  : MetricCalculator.calculate_multiple_runs(all_metrics_list),
        "num_of_collisions" : total_collisions
    }
    overview:str = Logger.get_overview_string(metrics_entire_set, str(used_seeds))
    print(overview)
    if log_data:
        Logger.log_overview(metrics_entire_set, used_seeds, folder_name)


def test_osm_get():
    map_builder.get_osm_area(BoundingBox(-2.65, 51, -2.5943, 52), "test_files/results")


if __name__ == "__main__":
    # TODO: Replace w/ config(?)
    has_gui = True
    log_data = True
    number_of_runs = 1
    entry_name = ""
    
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
        elif arg.startswith("-o=") or arg.startswith("--output_folder_name="):
            try:
                arg_elems = arg.split("=")
                assert(len(arg_elems) == 2)
                entry_name = str(arg_elems[1])
            except Exception as e:
                raise e
        elif arg != "python" and arg != "main.py":
            raise ValueError(f"Unknown argument: {arg}")
    run_simulation(has_gui=has_gui, log_data=log_data, number_of_runs=number_of_runs, entry_name=entry_name)
