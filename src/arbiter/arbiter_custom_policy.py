from src.arbiter.arbiter import ArbiterPolicy
import importlib, inspect

class ArbiterCustomPolicy(ArbiterPolicy):
    
    def __init__(self, junction_id:str, module_path:str):
        super().__init__(junction_id)
        new_path_arr = module_path.replace("/", ".").replace("\\", ".").split(".")
        if new_path_arr[-1] == "py":
            new_path_arr.pop(-1)
        new_path = new_path_arr[0]
        for i in range(1, len(new_path_arr)):
            new_path += "." + new_path_arr[i]
        self.module = importlib.import_module("".join(new_path))
        self.module_path = module_path

        for name, obj in inspect.getmembers(self.module, inspect.isclass):
            if issubclass(obj, ArbiterPolicy) and obj != ArbiterPolicy and not bool(obj.__subclasses__()):
                self.name = name
                self.policy : ArbiterPolicy = obj(junction_id)
                break
    

    def receive_message(self, vehicle):
        return self.policy.receive_message(vehicle)