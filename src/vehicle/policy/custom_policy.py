from src.vehicle.policy.policy import VehiclePolicy
import importlib, inspect

class CustomPolicy(VehiclePolicy):
    
    def __init__(self, vehicle, module_path:str):
        super().__init__(vehicle)
        new_path_arr = module_path.replace("/", ".").replace("\\", ".").split(".")
        if new_path_arr[-1] == "py":
            new_path_arr.pop(-1)
        new_path = new_path_arr[0]
        for i in range(1, len(new_path_arr)):
            new_path += "." + new_path_arr[i]
        self.module = importlib.import_module("".join(new_path))
        self.module_path = module_path

        for name, obj in inspect.getmembers(self.module, inspect.isclass):
            if issubclass(obj, VehiclePolicy) and obj != VehiclePolicy and not bool(obj.__subclasses__()):
                self.name = name
                self.policy : VehiclePolicy = obj(vehicle)
                break
    

    def decide_state(self, vehicle, conflicting_vehicles):
        return self.policy.decide_state(vehicle, conflicting_vehicles)