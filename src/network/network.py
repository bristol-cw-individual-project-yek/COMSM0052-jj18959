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


    def generateFile(self, output_file_name:str):
        if not os.path.exists(Network.TEMP_FILE_DIRECTORY):
            os.makedirs(Network.TEMP_FILE_DIRECTORY)
        
        network_file_name = output_file_name + ".net.xml"
        if not self.network_file_path:
            self.network_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, network_file_name)
            self.generateNetwork(self.network_file_path)
        else:
            network_file_name = os.path.abspath(self.network_file_path)
        
        self.net = sumolib.net.readNet(self.network_file_path)
        
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
        
