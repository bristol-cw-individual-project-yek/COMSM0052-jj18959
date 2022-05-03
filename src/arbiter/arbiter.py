from src.vehicle.vehicle_state import VehicleState
from src.vehicle.policy.policy import SharedNetwork

class ArbiterPolicy:
    def __init__(self, junction_id:str):
        self.junction_id = junction_id
        SharedNetwork.arbiter_id_to_policy[junction_id] = self


    def receive_request(self, vehicle):
        return VehicleState.WAITING
    
    
    def on_time_updated(self) -> None:
        pass


class Arbiter:
    def __init__(self, policy:ArbiterPolicy):
        self.policy = policy


class ArbiterManager:
    def __init__(self) -> None:
        self.__junction_to_arbiter:dict = {}
    

    def assign_arbiter_to_junction(self, junction_id:str, arbiter:Arbiter):
        self.__junction_to_arbiter[junction_id] = arbiter
    

    def has_arbiter(self, junction_id:str):
        return junction_id in self.__junction_to_arbiter
    

    def send_message_to_arbiter(self, junction_id:str, vehicle):
        try:
            arbiter:Arbiter = self.__junction_to_arbiter[junction_id]
            return arbiter.policy.receive_request(vehicle)
        except KeyError:
            pass
    

    def update(self):
        for j_id in self.__junction_to_arbiter:
            self.__junction_to_arbiter[j_id].policy.on_time_updated()


    def reset():
        ArbiterManager.__junction_to_arbiter.clear()
