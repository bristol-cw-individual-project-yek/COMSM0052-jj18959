import os
import json
from datetime import datetime
import network.network as ntwk

class Logger:
    def log_data_as_json(config_data:dict, step_data:dict, network:ntwk.Network, collision_data:dict, vehicle_metadata:dict={}, entry_folder_name="") -> None:
        log_directory_name = "logs"
        if not os.path.exists(log_directory_name):
            os.makedirs(log_directory_name)
        if entry_folder_name == "":
            entry_folder_name = datetime.today().isoformat().replace(":", "-", -1).split(".")[0]
        os.makedirs(log_directory_name + "/" + entry_folder_name)

        network_data = network.getData()
        vehicle_group_data = config_data["vehicle-groups"]
        custom_policies = {}

        # Get any custom policies
        for groupId in vehicle_group_data:
            group = vehicle_group_data[groupId]
            if group["policy-type"] == "custom" and "policy-path" in group:
                custom_policies[groupId] = group["policy-path"]
        
        # Record custom policies
        Logger.record_custom_policies(custom_policies, log_directory_name, entry_folder_name)

        # Replace paths with the relative file path of the records
        for groupId in custom_policies:
            custom_policies[groupId] = groupId + "/" + os.path.basename(custom_policies[groupId])

        data = {
            "network_data"          : network_data,
            "steps"                 : config_data["steps"],
            "vehicle_group_data"    : vehicle_group_data,
            "custom_policies"       : custom_policies,
            "vehicle_type_data"     : config_data["vehicle-types"],
            "vehicle_metadata"      : vehicle_metadata,
            "collision_data"        : collision_data,
            "step_data"             : step_data,
        }
        data["network_data"]["network_type"] = config_data["network-type"]
        
        with open(log_directory_name + "/" + entry_folder_name + "/" + "data.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            f.close()
    

    def record_custom_policies(custom_policies:dict, log_directory_name:str, entry_folder_name:str):
        for groupId in custom_policies:
            path:str = custom_policies[groupId]
            with open(path, "r") as original_file:
                contents = original_file.read()
                original_file.close()
            os.makedirs(log_directory_name + "/" + entry_folder_name + "/" + groupId)
            new_file_name = os.path.basename(path)
            with open(log_directory_name + "/" + entry_folder_name + "/" + groupId + "/" + new_file_name, "w") as copy_file:
                copy_file.write(contents)
                copy_file.close()