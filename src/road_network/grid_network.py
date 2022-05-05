import os
from src.road_network.road_network import RoadNetwork

class GridNetwork(RoadNetwork):

    def generateNetwork(self, network_file_path):
        netgen_cmd = "netgenerate --grid --output-file=" + network_file_path
        settings_cmd = ""
        for key in self.settings:
            settings_cmd += " --grid." + str(key) + "=" + str(self.settings[key])
        netgen_cmd += settings_cmd
        os.system(netgen_cmd)