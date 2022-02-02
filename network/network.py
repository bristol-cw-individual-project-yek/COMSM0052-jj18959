import os, sys

class Network:

    def __init__(self):
        pass


    def generateNetwork(self, output_file_name:str):
        netgenCmd = "netgenerate --grid=true --output-file=" + output_file_name
        os.system(netgenCmd)
