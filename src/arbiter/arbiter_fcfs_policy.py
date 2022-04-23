from arbiter.arbiter import ArbiterPolicy
from src.vehicle.vehicle_state import VehicleState
import traci

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


    def receive_message(self, vehicle):
        current_time = traci.simulation.getTime()
        if vehicle not in self.reserved_times:
            self.insert_into_queue(vehicle, current_time)
        reserved_time = self.reserved_times[vehicle]
        if current_time >= reserved_time:
            return VehicleState.CROSSING
        else:
            return VehicleState.WAITING
    

    def on_time_updated(self):
        self.update_junction_data()
    

    def update_junction_data(self):
        current_time = traci.simulation.getCurrentTime()
        to_be_removed = []
        for v in self.arrival_times:
            if (v.get_next_junction().getID() != self.junction_id or not v.isActive) and type(self).arrival_times[v] < current_time:
                to_be_removed.append(v)
        for v in to_be_removed:
            self.reserved_times.pop(v)
            self.arrival_times.pop(v)