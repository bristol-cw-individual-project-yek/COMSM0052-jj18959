import os
import xml.etree.ElementTree as ET

import randomTrips
import sumolib

class Network:

    TEMP_FILE_DIRECTORY:str = "temp"

    def __init__(self, settings:dict, seed:int, network_file_path:str = None, route_file_path:str = None):
        self.routeIds:list = []
        self.settings:dict = settings
        self.net:sumolib.net.Net = None
        self.seed:int = seed
        self.network_file_path = network_file_path
        self.route_file_path = route_file_path
        self.internal_lane_data:dict = {}
        self.connection_data:dict = {}


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
        if not self.network_file_path:
            self.network_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, network_file_name)
            self.generateNetwork(self.network_file_path)
        else:
            network_file_name = os.path.abspath(self.network_file_path)
        
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
        
        if self.route_file_path:
            pass
        else:
            self.route_file_path = self.generateRandomRoutes(self.network_file_path)
        sumo_cfg_file_name = output_file_name + ".sumocfg"
        sumo_root = ET.Element("configuration")
        sumo_tree = ET.ElementTree(sumo_root)
        sumo_input = ET.SubElement(sumo_root, "input")
        sumo_network_elem = ET.SubElement(sumo_input, "net-file")
        sumo_network_elem.set("value",network_file_name)
        sumo_route_elem = ET.SubElement(sumo_input, "route-files")
        sumo_route_elem.set("value", self.route_file_path.replace(Network.TEMP_FILE_DIRECTORY + "\\", ""))
        sumo_path = os.path.join(Network.TEMP_FILE_DIRECTORY, sumo_cfg_file_name)
        sumo_tree.write(sumo_path, encoding="utf-8")

        print(sumo_path)

        return sumo_path


    def generateRandomRoutes(self, network_file_path:str, route_steps:int=100, route_seed:int=None) -> str:
        trip_file_path = network_file_path.replace(".net", "_trips.rou")
        trip_args = []
        trip_args.append("-n=" + network_file_path)
        trip_args.append("-o=" + trip_file_path)
        if route_seed:
            trip_args.append("--seed=" + str(route_seed))
        else:
            trip_args.append("--seed=" + str(self.seed))
        randomTrips.main(randomTrips.get_options(args=trip_args))
        route_file_path = network_file_path.replace(".net", ".rou")
        routes_cmd = "duarouter -n=" + network_file_path + " -r=" + trip_file_path + " -o=" + route_file_path + " --named-routes=true --route-steps=" + str(route_steps)
        os.system(routes_cmd)

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
        return route_file_path


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
        

