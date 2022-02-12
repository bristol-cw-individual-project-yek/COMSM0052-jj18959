from vehicle.vehicle_policy import VehiclePolicy
import importlib

class CustomPolicy(VehiclePolicy):
    
    def __init__(self, module_path:str):
        self.module_path = importlib.import_module(module_path)
    

    def decide_state(self, vehicle, conflicting_vehicles):
        getattr(self.module_path, "decide_state")(vehicle, conflicting_vehicles)