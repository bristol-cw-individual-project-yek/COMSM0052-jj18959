import os
import json
from datetime import datetime
import network.network as ntwk

class Logger:
    def log_data_as_json(config_data:dict, step_data:dict, network:ntwk.Network, vehicle_metadata:dict={}, entry_folder_name=""):
        network_data = network.getData()
        data = {
            "network_data"          : network_data,
            "steps"                 : config_data["steps"],
            "vehicle_group_data"    : config_data["vehicle-groups"],
            "vehicle_type_data"     : config_data["vehicle-types"],
            "vehicle_metadata"      : vehicle_metadata,
            "step_data"             : step_data,
        }
        data["network_data"]["network_type"] = config_data["network-type"]
        log_directory_name = "logs"
        if not os.path.exists(log_directory_name):
            os.makedirs(log_directory_name)
        if entry_folder_name == "":
            entry_folder_name = datetime.today().isoformat().replace(":", "-", -1).split(".")[0]
        os.makedirs(log_directory_name + "/" + entry_folder_name)
        with open(log_directory_name + "/" + entry_folder_name + "/" + "data.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            f.close()