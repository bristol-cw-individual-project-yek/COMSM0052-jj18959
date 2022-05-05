import os
import json
from datetime import datetime
import src.road_network.road_network as ntwk
import matplotlib.pyplot as plt


def plot_distribution(distribution:list, x_label:str, y_label:str, min:int, max:int, destination:str):
    plt.clf()
    num_of_bins = (max - min) // 5
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.hist(distribution, bins=num_of_bins)
    plt.savefig(destination)


class Logger:
    LOG_DIRECTORY_NAME:str = "logs"
    DATA_DIRECTORY_NAME:str = "simulations"

    def create_data_folder(entry_folder_name:str="") -> str:
        """
        Create a folder for new data entries.

        Returns the name of the folder created.
        """
        
        if not os.path.exists(Logger.LOG_DIRECTORY_NAME):
            os.makedirs(Logger.LOG_DIRECTORY_NAME)
        if entry_folder_name == "":
            entry_folder_name:str = datetime.today().isoformat().replace(":", "-", -1).split(".")[0]
        
        log_entry_directory_path = Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name
        if not os.path.exists(log_entry_directory_path):
            os.makedirs(log_entry_directory_path)
        simulation_directory_path = Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/" + Logger.DATA_DIRECTORY_NAME
        if not os.path.exists(simulation_directory_path):
            os.makedirs(simulation_directory_path)
        return entry_folder_name
    

    def log_overview(metrics_entire_set:dict, used_seeds:list, entry_folder_name:str):
        overview_str = Logger.get_overview_string(metrics_entire_set, str(used_seeds))
        with open(Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/overview.txt", "w") as f:
            f.write(overview_str)
            f.close()
        total_wait_times_path = Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/total_wait_times.png"
        junction_wait_times_path = Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/junction_wait_times.png"
        plot_distribution(metrics_entire_set["wait_time_metrics"]["total-wait-time"]["samples"], "Total wait time (turns)", "Number of vehicles", 0, metrics_entire_set["wait_time_metrics"]["total-wait-time"]["max"], total_wait_times_path)
        plot_distribution(metrics_entire_set["wait_time_metrics"]["wait-times-per-junction"]["samples"],"Junction wait time (turns)", "Number of vehicles", 0, metrics_entire_set["wait_time_metrics"]["wait-times-per-junction"]["max"], junction_wait_times_path)
        with open(Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/total_wait_times.csv", "w") as f:
            total_wait_time_stats:dict = metrics_entire_set["wait_time_metrics"]["total-wait-time"]
            tw_samples = total_wait_time_stats["samples"]
            output_str = ""
            for sample in tw_samples:
                output_str += str(sample) + ",\n"
            f.write(output_str)
            f.close()
        with open(Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/wait_times_per_junction.csv", "w") as f:
            wait_time_per_junction_stats:dict = metrics_entire_set["wait_time_metrics"]["wait-times-per-junction"]
            wt_samples = wait_time_per_junction_stats["samples"]
            output_str = ""
            for sample in wt_samples:
                output_str += str(sample) + ",\n"
            f.write(output_str)
            f.close()


    def log_data_as_json(config_data:dict, step_data:dict, network:ntwk.RoadNetwork, collision_data:dict, entry_folder_name:str, vehicle_metadata:dict={}, metrics:dict={}, simulation_number:int=0) -> None:
        network_data = network.getData()
        vehicle_group_data = config_data["vehicle-groups"]
        custom_policies = {}

        # Get any custom policies
        for groupId in vehicle_group_data:
            group = vehicle_group_data[groupId]
            if group["policy-type"] == "custom" and "policy-path" in group:
                custom_policies[groupId] = group["policy-path"]
        
        # Record custom policies if necessary
        try:
            Logger.record_custom_policies(custom_policies, Logger.LOG_DIRECTORY_NAME, entry_folder_name)
        except FileExistsError:
            pass

        # Replace paths with the relative file path of the records
        for groupId in custom_policies:
            custom_policies[groupId] = groupId + "/" + os.path.basename(custom_policies[groupId])

        data = {
            "network_data"          : network_data,
            "steps"                 : config_data["steps"],
            "metrics"               : metrics,
            "vehicle_group_data"    : vehicle_group_data,
            "custom_policies"       : custom_policies,
            "vehicle_type_data"     : config_data["vehicle-types"],
            "vehicle_metadata"      : vehicle_metadata,
            "collision_data"        : collision_data,
            "step_data"             : step_data,
        }
        data["network_data"]["network_type"] = config_data["network-type"]
        
        with open(Logger.LOG_DIRECTORY_NAME + "/" + entry_folder_name + "/" + Logger.DATA_DIRECTORY_NAME + "/" + "sim_" + str(simulation_number) + ".json", "w") as f:
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
    

    def get_overview_string(metrics:dict, seeds:list) -> str:
        result = "\n------------RESULTS------------\n"
        seed_str = f"Seeds used: {str(seeds)}\n\n"
        collision_str = "Number of collisions: " + str(metrics["num_of_collisions"])
        total_wait_time_stats:dict = metrics["wait_time_metrics"]["total-wait-time"]
        tw_mean = total_wait_time_stats["mean"]
        tw_median = total_wait_time_stats["median"]
        tw_min = total_wait_time_stats["min"]
        tw_max = total_wait_time_stats["max"]
        tw_skew = total_wait_time_stats["skew"]
        tw_kurtosis = total_wait_time_stats["kurtosis"]
        tw_samples = total_wait_time_stats["samples"]
        total_wait_time_str = f"""
Total wait time stats:
    Mean    :   {tw_mean}
    Median  :   {tw_median} 
    Min     :   {tw_min} 
    Max     :   {tw_max} 
    Skew    :   {tw_skew}
    Kurtosis:   {tw_kurtosis}
    """
        wait_time_per_junction_stats:dict = metrics["wait_time_metrics"]["wait-times-per-junction"]
        wt_mean = wait_time_per_junction_stats["mean"]
        wt_median = wait_time_per_junction_stats["median"]
        wt_min = wait_time_per_junction_stats["min"]
        wt_max = wait_time_per_junction_stats["max"]
        wt_skew = wait_time_per_junction_stats["skew"]
        wt_kurtosis = wait_time_per_junction_stats["kurtosis"]
        wt_samples = wait_time_per_junction_stats["samples"]
        wait_time_per_junction_str = f"""
Wait time per junction stats:
    Mean    :   {wt_mean}
    Median  :   {wt_median} 
    Min     :   {wt_min} 
    Max     :   {wt_max} 
    Skew    :   {wt_skew} 
    Kurtosis:   {wt_kurtosis} 
    """
        result += seed_str + collision_str + "\n" + total_wait_time_str + "\n" + wait_time_per_junction_str
        result += "\n-------------------------------\n"
        return result