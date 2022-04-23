from src.vehicle.vehicle_state import VehicleState

class ArbiterPolicy:
    def __init__(self, junction_id:str):
        self.junction_id = junction_id


    def receive_message(self, vehicle):
        return VehicleState.WAITING
    
    
    def on_time_updated(self) -> None:
        pass


class Arbiter:
    def __init__(self, policy:ArbiterPolicy):
        self.policy = policy
