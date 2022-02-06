import os
import xml.etree.ElementTree as ET
import randomTrips

class Network:

    TEMP_FILE_DIRECTORY = "temp"

    def __init__(self):
        pass


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
        trip_args = []
        trip_args.append("-n=" + network_file_path)
        trip_args.append("-o=" + network_file_path.replace(".net", ".rou"))
        randomTrips.main(randomTrips.get_options(args=trip_args))


    def generateNetwork(self, network_file_path:str):
        netgen_cmd = "netgenerate --rand --rand.iterations=200 --output-file=" + network_file_path
        os.system(netgen_cmd)
        

