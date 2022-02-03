import os, sys
import xml.etree.ElementTree as ET

class Network:

    TEMP_FILE_DIRECTORY = "temp"

    def __init__(self):
        pass


    def generateNetwork(self, output_file_name:str):
        if not os.path.exists(Network.TEMP_FILE_DIRECTORY):
            os.makedirs(Network.TEMP_FILE_DIRECTORY)
        path = os.path.join(Network.TEMP_FILE_DIRECTORY, output_file_name)
        netgenCmd = "netgenerate --grid=true --output-file=" + path
        os.system(netgenCmd)
        networkTree : ET = ET.parse(path)
        root = networkTree.getroot()
        location = None
        edges = []
        connections = []
        junctions = []
        for child in root:
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
