import os
import xml.etree.ElementTree as ET

import randomTrips
import sumolib

class Network:

    TEMP_FILE_DIRECTORY = "temp"

    def __init__(self, settings:dict, route_seed:int, network_file_path:str = None):
        self.routeIds:list = []
        self.settings:dict = settings
        self.net:sumolib.net.Net = None
        self.route_seed:int = route_seed
        self.network_file_path = network_file_path
        self.internal_lane_data:dict = {}
        self.connection_data:dict = {}


    def getConnectionLength(self, fromEdgeId: str, toEdgeId: str):
        connectionId = fromEdgeId + "-" + toEdgeId
        laneId = self.connection_data[connectionId]["internal"]
        length = self.internal_lane_data[laneId]["length"]
        return length


    def generateFile(self, output_file_name:str):
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
            if "via" in con.attrib:
                connection_id = con.attrib["from"] + "-" + con.attrib["to"]
                self.connection_data[connection_id] = {}
                self.connection_data[connection_id]["internal"] = con.attrib["via"]
        print(self.internal_lane_data)
        print(self.connection_data)
        #        root.remove(child)
        #    elif child.tag == "route":
        #        self.routeIds.append(child.attrib["id"])

        
        self.generateRandomRoutes(self.network_file_path)

        sumo_cfg_file_name = output_file_name + ".sumocfg"
        sumo_root = ET.Element("configuration")
        sumo_tree = ET.ElementTree(sumo_root)
        sumo_input = ET.SubElement(sumo_root, "input")
        sumo_network_elem = ET.SubElement(sumo_input, "net-file")
        sumo_network_elem.set("value",network_file_name)
        sumo_route_elem = ET.SubElement(sumo_input, "route-files")
        sumo_route_elem.set("value", network_file_name.replace(".net", ".rou"))
        sumo_path = os.path.join(Network.TEMP_FILE_DIRECTORY, sumo_cfg_file_name)
        sumo_tree.write(sumo_path, encoding="utf-8")

        print(sumo_path)

        return sumo_path


    def generateRandomRoutes(self, network_file_path:str, route_steps:int=100):
        trip_file_path = network_file_path.replace(".net", "_trips.rou")
        trip_args = []
        trip_args.append("-n=" + network_file_path)
        trip_args.append("-o=" + trip_file_path)
        trip_args.append("--seed=" + str(self.route_seed))
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


    def generateNetwork(self, network_file_path:str):
        netgen_cmd = "netgenerate --rand" + " --output-file=" + network_file_path
        settings_cmd = " --bidi-probability=" + str(self.settings["bidi-probability"])
        for key in self.settings:
            if not key == "bidi-probability":
                settings_cmd += " --rand." + str(key) + "=" + str(self.settings[key])
        netgen_cmd += settings_cmd
        os.system(netgen_cmd)
    

    def getData(self) -> dict:
        data = {
            "settings"      : self.settings,
            "route_seed"    : self.route_seed
        }
        return data
        

