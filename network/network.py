import os, sys
from telnetlib import TELNET_PORT

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
