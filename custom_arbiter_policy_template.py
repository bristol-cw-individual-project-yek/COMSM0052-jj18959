

from src.arbiter.arbiter import ArbiterPolicy


class CustomArbiterPolicyTemplate(ArbiterPolicy):
    def __init__(self, junction_id:str):
        super().__init__(junction_id)


    def receive_message(self, vehicle):
        return super().receive_message(vehicle)
    
    
    def on_time_updated(self) -> None:
        super().on_time_updated()