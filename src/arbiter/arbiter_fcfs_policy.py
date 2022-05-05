from src.arbiter.arbiter import ArbiterPolicy
from src.vehicle.vehicle_state import VehicleState

class ArbiterFCFSPolicy(ArbiterPolicy):

    def __init__(self, junction_id:str):
        self.queue:list = []
        self.reserved_times:dict = {}
        self.arrival_times:dict = {}
        super().__init__(junction_id)


    def update_reserved_times(self, index):
        index += 1
        while index < len(self.queue):
            last_vehicle = self.queue[index - 1]
            this_vehicle = self.queue[index]
            self.reserved_times[this_vehicle] = self.arrival_times[last_vehicle]
            self.arrival_times[this_vehicle] = self.get_arrival_time(self.reserved_times[this_vehicle], this_vehicle)
            index += 1


    def can_swap(self, vehicle, other_vehicle) -> bool:
        return False


    def get_initial_reserve_time(self, vehicle, current_time:float) -> float:
        result = current_time
        if len(self.queue) == 0:
            return result
        else:
            for other_vehicle in self.queue:
                if other_vehicle.get_next_junction().getID() == self.junction_id and other_vehicle.isActive:
                    result = max(result, self.arrival_times[other_vehicle])
            return result
    

    def get_arrival_time(self, reserved_time, vehicle):
        return reserved_time + (vehicle.get_time_to_cross_next_junction())


    def insert_into_queue(self, vehicle, current_time:int) -> None:
        reserved_time = self.get_initial_reserve_time(vehicle, current_time)
        arrival_time = self.get_arrival_time(reserved_time, vehicle)
        self.reserved_times[vehicle] = reserved_time
        self.arrival_times[vehicle] = arrival_time
        index = len(self.queue) - 1
        position_found = False
        while index >= 0 and not position_found:
            other_vehicle = self.queue[index]
            if (not self.can_swap(vehicle, other_vehicle)) or other_vehicle.currentState == VehicleState.CROSSING:
                position_found = True
            else:
                reserved_time = self.reserved_times[other_vehicle]
                self.reserved_times[vehicle] = reserved_time
                arrival_time = self.get_arrival_time(reserved_time, vehicle)
                self.arrival_times[vehicle] = arrival_time
                index -= 1
        index += 1
        self.queue.insert(index, vehicle)
        self.update_reserved_times(index)


    def receive_request(self, vehicle):
        if vehicle not in self.reserved_times:
            self.insert_into_queue(vehicle, self.current_time)
        reserved_time = self.reserved_times[vehicle]
        if self.current_time >= reserved_time:
            return VehicleState.CROSSING
        else:
            return VehicleState.WAITING
    

    def on_time_updated(self, time):
        self.update_junction_data()
        super().on_time_updated(time)
    

    def update_junction_data(self):
        to_be_removed = []
        for v in self.arrival_times:
            if (v.get_next_junction().getID() != self.junction_id or not v.isActive) and self.arrival_times[v] < self.current_time:
                to_be_removed.append(v)
        for v in to_be_removed:
            self.reserved_times.pop(v)
            self.arrival_times.pop(v)