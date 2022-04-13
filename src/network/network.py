import os
import shutil
import xml.etree.ElementTree as ET
import yaml

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
        print(scenario_file_path)


    def create_edge_id(self, from_edge_id:str, to_edge_id:str) -> str:
        return from_edge_id + "->" + to_edge_id


    def create_network_from_yaml(self, yaml_file_path:str):
        new_network:sumolib.net.Net = sumolib.net.Net()
        try: 
            with open(yaml_file_path, "r") as stream:
                scenario_data = yaml.safe_load(stream)
                stream.close()
        except FileNotFoundError as e:
            raise e
        network_data = scenario_data["network"]
        nodes = network_data["nodes"]
        node_ids_to_connections:dict = {}

        # Add nodes
        for node in nodes:
            node_id:str = node["id"]
            to_nodes:list = node["connections"]
            node_ids_to_connections[node_id] = to_nodes
            location:tuple = tuple(node["location"])
            try:
                node_type:str = node["type"]
            except KeyError:
                node_type = "priority"
            new_network.addNode(id=node_id, type=node_type, coord=location)
        
        # Add edges and lanes
        for node_id in node_ids_to_connections:
            for other_node_info in node_ids_to_connections[node_id]:
                if type(other_node_info) == str:
                    other_node_id = other_node_info
                    num_of_lanes = 1
                elif type(other_node_info) == dict:
                    other_node_id = other_node_info["toNode"]
                    num_of_lanes = other_node_info["lanes"]
                edge_id = self.create_edge_id(node_id, other_node_id)
                edge = new_network.addEdge(id=edge_id, fromID=node_id, toID= other_node_id, prio=-1, function=None, name=None)
                for i in range(num_of_lanes):
                    lane = new_network.addLane(edge=edge, speed=None, length=None, width=None)
                print(lane.getID())
        
        # Create connections between edges and lanes

        print(new_network)

        print(new_network.getEdges(withInternal=True))



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
        
        network_file_name = output_file_name + ".net.xml"
        temp_network_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, network_file_name)
        if not self.network_file_path:
            self.network_file_path = temp_network_file_path
            self.generateNetwork(self.network_file_path)
        else:
            shutil.copy(os.path.abspath(self.network_file_path), temp_network_file_path)
        
        self.net = sumolib.net.readNet(self.network_file_path, withInternal=True)

        # Store info about internal edge lengths
        net_tree = ET.ElementTree()
        net_tree.parse(self.network_file_path)
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
        
        route_file_name = output_file_name + ".rou.xml"
        temp_route_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, route_file_name)
        if self.route_file_path:
            shutil.copy(os.path.abspath(self.route_file_path), temp_route_file_path)
        else:
            self.route_file_path = self.generateRandomRoutes(temp_network_file_path, dest=temp_route_file_path)
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
        

