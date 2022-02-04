import os
from network.network import Network

class GridNetwork(Network):

    def generateNetwork(self, network_file_path):
        netgen_cmd = "netgenerate --grid --output-file=" + network_file_path
        os.system(netgen_cmd)