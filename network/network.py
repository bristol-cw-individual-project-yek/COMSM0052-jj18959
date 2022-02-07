import os
import xml.etree.ElementTree as ET
import randomTrips

class Network:

    TEMP_FILE_DIRECTORY = "temp"

    def __init__(self):
        self.routeIds = []


    def generateFile(self, output_file_name:str):
        if not os.path.exists(Network.TEMP_FILE_DIRECTORY):
            os.makedirs(Network.TEMP_FILE_DIRECTORY)
        network_file_name = output_file_name + ".net.xml"
        network_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, network_file_name)

        self.generateNetwork(network_file_path)
        
        self.generateRandomRoutes(network_file_path)

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


    def generateRandomRoutes(self, network_file_path:str):
        trip_file_path = network_file_path.replace(".net", "_trips.rou")
        trip_args = []
        trip_args.append("-n=" + network_file_path)
        trip_args.append("-o=" + trip_file_path)
        randomTrips.main(randomTrips.get_options(args=trip_args))
        route_file_path = network_file_path.replace(".net", ".rou")
        routes_cmd = "duarouter -n=" + network_file_path + " -r=" + trip_file_path + " -o=" + route_file_path + " --named-routes=true"
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
        netgen_cmd = "netgenerate --rand --rand.iterations=200 --output-file=" + network_file_path
        os.system(netgen_cmd)
        

