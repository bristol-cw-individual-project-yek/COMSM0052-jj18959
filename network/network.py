import os
import xml.etree.ElementTree as ET

class Network:

    TEMP_FILE_DIRECTORY = "temp"

    def __init__(self):
        pass


    def generateNetwork(self, output_file_name:str):
        if not os.path.exists(Network.TEMP_FILE_DIRECTORY):
            os.makedirs(Network.TEMP_FILE_DIRECTORY)
        network_file_name = output_file_name + ".net.xml"
        network_file_path = os.path.join(Network.TEMP_FILE_DIRECTORY, network_file_name)
        netgen_cmd = "netgenerate --grid=true --output-file=" + network_file_path
        os.system(netgen_cmd)
        network_tree : ET = ET.parse(network_file_path)
        network_root = network_tree.getroot()
        location = None
        edges = []
        connections = []
        junctions = []
        for child in network_root:
            attrib = child.attrib
            if child.tag == "edge":
                edges.append(attrib)
            if child.tag == "location":
                location = attrib
            if child.tag == "junction":
                junctions.append(attrib)
            if child.tag == "connection":
                connections.append(attrib)
        print("Edges: ", len(edges))
        print("Connections: ", len(connections))
        print("Junctions: ", len(junctions))

        sumo_cfg_file_name = output_file_name + ".sumocfg"
        sumo_root = ET.Element("configuration")
        sumo_tree = ET.ElementTree(sumo_root)
        sumo_input = ET.SubElement(sumo_root, "input")
        sumo_network_elem = ET.SubElement(sumo_input, "net-file")
        sumo_network_elem.set("value",network_file_name)
        sumo_path = os.path.join(Network.TEMP_FILE_DIRECTORY, sumo_cfg_file_name)
        sumo_tree.write(sumo_path, encoding="utf-8")

        print(sumo_path)

        return sumo_path

