import os
from network.network import Network

class GridNetwork(Network):

    def generateNetwork(self, network_file_path):
        netgen_cmd = "netgenerate --grid --output-file=" + network_file_path
        settings_cmd = ""
        for key in self.settings:
            settings_cmd += " --grid." + str(key) + "=" + str(self.settings[key])
        netgen_cmd += settings_cmd
        os.system(netgen_cmd)