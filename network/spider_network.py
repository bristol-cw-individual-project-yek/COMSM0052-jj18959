import os
from network.network import Network

class SpiderNetwork(Network):

    def generateNetwork(self, network_file_path):
        netgen_cmd = "netgenerate --spider --output-file=" + network_file_path
        settings_cmd = ""
        for key in self.settings:
            settings_cmd += " --spider." + str(key) + "=" + str(self.settings[key])
        netgen_cmd += settings_cmd
        os.system(netgen_cmd)