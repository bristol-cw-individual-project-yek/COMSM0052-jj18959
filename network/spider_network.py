import os
from network.network import Network

class SpiderNetwork(Network):

    def generateNetwork(self, network_file_path):
        netgen_cmd = "netgenerate --spider --output-file=" + network_file_path
        os.system(netgen_cmd)