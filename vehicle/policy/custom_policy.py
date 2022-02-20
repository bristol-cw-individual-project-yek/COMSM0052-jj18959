from vehicle.policy.policy import Policy
import importlib

class CustomPolicy(Policy):
    
    def __init__(self, module_path:str):
        new_path_arr = module_path.replace("/", ".").replace("\\", ".").split(".")
        if new_path_arr[-1] == "py":
            new_path_arr.pop(-1)
        new_path = new_path_arr[0]
        for i in range(1, len(new_path_arr)):
            new_path += "." + new_path_arr[i]
        self.module_path = importlib.import_module("".join(new_path))
    

    def decide_state(self, vehicle, conflicting_vehicles):
        getattr(self.module_path, "decide_state")(vehicle, conflicting_vehicles)