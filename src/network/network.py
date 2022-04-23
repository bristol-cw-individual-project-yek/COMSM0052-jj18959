import os
import random
import shutil
import xml.etree.ElementTree as ET
import yaml
from typing import Union
from xml.dom import minidom

import randomTrips
import sumolib

class Network:

    TEMP_FILE_DIRECTORY:str = "temp"

    def __init__(self, settings:dict, seed:int, network_file_path:str = None, route_file_path:str = None, scenario_file_path:str=None):
        self.routeIds:list = []
        self.settings:dict = settings
        self.net:sumolib.net.Net = None
        self.seed:int = seed
        self.network_file_path = network_file_path
        self.route_file_path = route_file_path
        self.internal_lane_data:dict = {}
        self.connection_data:dict = {}
        self.scenario_file_path:str = scenario_file_path
        self.route_probability_thresholds:list = []
        self.total_route_probability_weights:float = 0.0
        self.rng:random.Random = random.Random(seed)
        self.junction_ids:list = []


    def get_random_route_id(self) -> str:
        rand_num = self.rng.random() * self.total_route_probability_weights
        found = False
        index = 0
        while index < len(self.route_probability_thresholds) and not found:
            route_and_threshold:tuple = self.route_probability_thresholds[index]
            if rand_num < route_and_threshold[1]:
                found = True
            index += 1
        index -= 1
        return self.route_probability_thresholds[index][0]


    def create_edge_id(self, from_edge_id:str, to_edge_id:str) -> str:
        return from_edge_id + "-" + to_edge_id


    def get_to_node_info(self, to_node_info:Union[str, dict]) -> dict:
        if type(to_node_info) == str:
            return {
                "toNode"    : to_node_info,
                "lanes"     : 1,
                "canUTurn"  : False,
            }
        elif type(to_node_info) == dict:
            return to_node_info


    def create_network_from_yaml(self, output_file_name:str, yaml_file_path:str) -> str:
        try: 
            with open(yaml_file_path, "r") as stream:
                scenario_data = yaml.safe_load(stream)
                stream.close()
        except FileNotFoundError as e:
            raise e
        network_data = scenario_data["network"]
        nodes = network_data["nodes"]
        node_ids_to_connections:dict = {}
        node_ids_to_incoming_lane_ids:dict = {}

        edge_root = ET.Element("edges")
        edge_elem_tree = ET.ElementTree(edge_root)
        node_root = ET.Element("nodes")
        node_elem_tree = ET.ElementTree(node_root)

        # Record nodes and connections
        for node in nodes:
            node_id:str = node["id"]
            to_nodes:list = node["connections"]
            node_ids_to_connections[node_id] = to_nodes
            
        
        # Add edges and lanes
        for node_id in node_ids_to_connections:
            for to_node_info in node_ids_to_connections[node_id]:
                data = self.get_to_node_info(to_node_info)
                to_node_id = data["toNode"]
                num_of_lanes = data["lanes"]
                edge_id = self.create_edge_id(node_id, to_node_id)
                edge_attrib = {
                    "id"        : edge_id,
                    "from"      : node_id,
                    "to"        : to_node_id,
                    "priority"  : "-1",
                    "numLanes"  : str(num_of_lanes)
                }
                edge_elem = ET.Element("edge", attrib=edge_attrib)
                edge_root.append(edge_elem)
                if not to_node_id in node_ids_to_incoming_lane_ids:
                    node_ids_to_incoming_lane_ids[to_node_id] = []
        
        # Actually add nodes
        for node in nodes:
            node_id:str = node["id"]
            to_nodes:list = node["connections"]
            location:tuple = tuple(node["location"])
            try:
                node_type:str = node["type"]
            except KeyError:
                node_type = "priority"
            node_attrib = {
                "id"        : node_id,
                "x"         : str(location[0]),
                "y"         : str(location[1]),
                "type"      : node_type
            }
            node_elem = ET.Element("node", node_attrib)
            node_root.append(node_elem)
        
        edge_file_name = Network.TEMP_FILE_DIRECTORY + "\\" + output_file_name + ".edg.xml"
        edge_elem_tree.write(edge_file_name)

        node_file_name = Network.TEMP_FILE_DIRECTORY + "\\" + output_file_name + ".nod.xml"
        node_elem_tree.write(node_file_name)

        network_output_file_path = Network.TEMP_FILE_DIRECTORY + "\\" + output_file_name + ".net.xml"
        os.system(f"netconvert --node-files={node_file_name} --edge-files={edge_file_name} --output-file={network_output_file_path} --lefthand=true")
        return network_output_file_path


    def create_routes_from_yaml(self, output_file_name:str, yaml_file_path:str) -> str:
        try: 
            with open(yaml_file_path, "r") as stream:
                scenario_data = yaml.safe_load(stream)
                stream.close()
        except FileNotFoundError as e:
            raise e
        route_data = scenario_data["routes"]
        route_root = ET.Element("routes")
        route_elem_tree = ET.ElementTree(route_root)

        route_num = 0
        for route_dict in route_data:
            path = route_dict["path"]
            edges_str = ""
            for index in range(len(path) - 1):
                edges_str += self.create_edge_id(path[index], path[index+1]) + " "
            edges_str = edges_str.strip()
            route_id = str(route_num)
            route_attrib = {
                "id"    : route_id,
                "edges" : edges_str
            }
            route_elem = ET.Element("route", attrib=route_attrib)
            route_root.append(route_elem)
            if "probabilityWeight" in route_dict:
                weight: float = route_dict["probabilityWeight"]
            else:
                weight: float = 1.0
            route_and_threshold:tuple = (route_id, self.total_route_probability_weights + weight)
            self.route_probability_thresholds.append(route_and_threshold)
            self.total_route_probability_weights += weight
            route_num += 1
        print(self.route_probability_thresholds)
        route_output_file_path = Network.TEMP_FILE_DIRECTORY + "\\" + output_file_name + ".rou.xml"
        route_elem_tree.write(route_output_file_path)
        
        return route_output_file_path


    def getConnectionLength(self, fromEdgeId: str, toEdgeId: str) -> float:
        try:
            connectionId = fromEdgeId + "-" + toEdgeId
            internal_lane_id:str = self.connection_data[connectionId]["internal"]
            internal_lane_data:dict = self.internal_lane_data[internal_lane_id]
            length:float = float(internal_lane_data["length"])
            internal_from_edge_list = internal_lane_id.split("_")
            internal_from_edge_list.pop()
            internal_from_edge_id = "_".join(internal_from_edge_list)
            length += self.getConnectionLength(internal_from_edge_id, toEdgeId)
            return length
        except KeyError:
            return 0


    def generateFile(self, output_file_name:str, route_seed:int=None):
        if not os.path.exists(Network.TEMP_FILE_DIRECTORY):
            os.makedirs(Network.TEMP_FILE_DIRECTORY)
        
        if self.scenario_file_path:
            temp_network_file_path = self.create_network_from_yaml(output_file_name, self.scenario_file_path)
            network_file_name = os.path.basename(temp_network_file_path)
        else:
            network_file_name = output_file_name + ".net.xml"
            temp_network_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, network_file_name)
            if not self.network_file_path:
                #self.network_file_path = temp_network_file_path
                self.generateNetwork(temp_network_file_path)
            else:
                shutil.copy(os.path.abspath(self.network_file_path), temp_network_file_path)
            
        self.net = sumolib.net.readNet(temp_network_file_path, withInternal=True)

        # Store info about internal edge lengths
        net_tree = ET.ElementTree()
        net_tree.parse(temp_network_file_path)
        root = net_tree.getroot()
        edges = root.findall("edge")
        for edge in edges:
            if "function" in edge.attrib and edge.attrib["function"] == "internal":
                for lane in edge.findall("lane"):
                    lane_id = lane.attrib["id"]
                    self.internal_lane_data[lane_id] = {}
                    self.internal_lane_data[lane_id]["length"] = lane.attrib["length"]
        connections = root.findall("connection")
        for con in connections:
            connection_id = con.attrib["from"] + "-" + con.attrib["to"]
            self.connection_data[connection_id] = {}
            try:
                self.connection_data[connection_id]["internal"] = con.attrib["via"]
            except:
                pass
        junctions = root.findall("junction")
        for junc in junctions:
            junction_id = junc.attrib["id"]
            self.junction_ids.append(junction_id)
        
        has_routes = False
        if self.scenario_file_path:
            try:
                temp_route_file_path = self.create_routes_from_yaml(output_file_name, self.scenario_file_path)
                route_file_name = os.path.basename(temp_route_file_path)
                self.prepare_route_file(temp_route_file_path)
                has_routes = True
            except KeyError:
                pass
        if not has_routes:
            route_file_name = output_file_name + ".rou.xml"
            temp_route_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, route_file_name)
            if self.route_file_path:
                shutil.copy(os.path.abspath(self.route_file_path), temp_route_file_path)
            else:
                self.generateRandomRoutes(temp_network_file_path, dest=temp_route_file_path)
            self.prepare_route_file(temp_route_file_path)
            
        sumo_cfg_file_name = output_file_name + ".sumocfg"
        sumo_root = ET.Element("configuration")
        sumo_tree = ET.ElementTree(sumo_root)
        sumo_input = ET.SubElement(sumo_root, "input")
        sumo_network_elem = ET.SubElement(sumo_input, "net-file")
        sumo_network_elem.set("value",network_file_name)
        sumo_route_elem = ET.SubElement(sumo_input, "route-files")
        sumo_route_elem.set("value", route_file_name)
        sumo_path = os.path.join(Network.TEMP_FILE_DIRECTORY, sumo_cfg_file_name)
        sumo_tree.write(sumo_path, encoding="utf-8")

        print(sumo_path)

        return sumo_path


    def generateRandomRoutes(self, network_file_path:str, dest:str=None, route_steps:int=100, route_seed:int=None) -> str:
        trip_file_path = network_file_path.replace(".net", "_trips.rou")
        trip_args = []
        trip_args.append("-n=" + network_file_path)
        trip_args.append("-o=" + trip_file_path)
        if route_seed:
            trip_args.append("--seed=" + str(route_seed))
        else:
            trip_args.append("--seed=" + str(self.seed))
        randomTrips.main(randomTrips.get_options(args=trip_args))
        if dest:
            route_file_path = dest
        else:
            route_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, os.path.basename(network_file_path.replace(".net", ".rou")))
        routes_cmd = "duarouter -n=" + network_file_path + " -r=" + trip_file_path + " -o=" + route_file_path + " --named-routes=true --route-steps=" + str(route_steps)
        os.system(routes_cmd)

        route_tree = ET.ElementTree()
        route_tree.parse(route_file_path)
        route_root = route_tree.getroot()
        for child in route_root:
            if child.tag == "route":
                route_id = child.attrib["id"]
                self.route_probability_thresholds.append(tuple([route_id, self.total_route_probability_weights + 1.0]))
                self.total_route_probability_weights += 1.0

        return route_file_path
    

    def prepare_route_file(self, route_file_path:str):
        # Remove any generated vehicles from the file - we will define those ourselves.
        route_tree = ET.ElementTree()
        route_tree.parse(route_file_path)
        root = route_tree.getroot()
        children = root.getchildren()
        self.routeIds.clear()
        for child in children:
            if child.tag == "vehicle":
                root.remove(child)
            elif child.tag == "route":
                self.routeIds.append(child.attrib["id"])
        route_tree.write(route_file_path, "utf-8")
        


    def generateNetwork(self, network_file_path:str):
        netgen_cmd = "netgenerate --rand" + " --output-file=" + network_file_path
        settings_cmd = ""
        for key in self.settings:
            if key == "bidi-probability":
                settings_cmd += " --bidi-probability=" + str(self.settings[key])
            elif key == "seed":
                settings_cmd += " --seed=" + str(self.settings[key])
            else:
                settings_cmd += " --rand." + str(key) + "=" + str(self.settings[key])
        netgen_cmd += settings_cmd
        os.system(netgen_cmd)
    

    def getData(self) -> dict:
        data = {
            "settings"      : self.settings,
            "seed"    : self.seed
        }
        return data
        

