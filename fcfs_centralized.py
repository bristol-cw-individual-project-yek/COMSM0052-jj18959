from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle import Vehicle
from src.vehicle.vehicle_state import VehicleState
import src.vehicle.policy.utils as utils
import traci
import copy

class FCFS_CentralizedPolicy(Policy):
    junction_to_vehicles:dict = {}
    reserved_times:dict = {}
    arrival_times:dict = {}
    last_recorded_time:float = 0


    def print_schedule(self, schedule:dict):
        print("{")
        for veh in schedule:
            vehId = veh.vehicleId
            print(f"    {vehId}:{str(schedule[veh])}")
        print("}")


    def can_swap(self, vehicle: Vehicle, other_vehicle:Vehicle) -> bool:
        return False


    def insert_into_queue(self, vehicle:Vehicle, junction_id:str, current_time:int) -> None:
        reserved_time = self.get_initial_reserve_time(vehicle, junction_id, current_time)
        arrival_time = self.get_arrival_time(reserved_time, vehicle)
        type(self).reserved_times[vehicle] = reserved_time
        type(self).arrival_times[vehicle] = arrival_time
        index = len(type(self).junction_to_vehicles[junction_id]) - 1
        position_found = False
        while index >= 0 and not position_found:
            other_vehicle:Vehicle = type(self).junction_to_vehicles[junction_id][index]
            if (not self.can_swap(vehicle, other_vehicle)) or other_vehicle.currentState == VehicleState.CROSSING:
                position_found = True
            else:
                reserved_time = type(self).reserved_times[other_vehicle]
                type(self).reserved_times[vehicle] = reserved_time
                arrival_time = self.get_arrival_time(reserved_time, vehicle)
                type(self).arrival_times[vehicle] = arrival_time
                index -= 1
        index += 1
        type(self).junction_to_vehicles[junction_id].insert(index, vehicle)
        self.update_reserved_times(junction_id, index)
    

    def get_initial_reserve_time(self, vehicle:Vehicle, junction_id:str, current_time:float) -> float:
        result = current_time
        if len(type(self).junction_to_vehicles[junction_id]) == 0:
            return result
        else:
            for other_vehicle in type(self).junction_to_vehicles[junction_id]:
                if other_vehicle.get_next_junction().getID() == junction_id and other_vehicle.isActive:
                    result = max(result, type(self).arrival_times[other_vehicle])
            return result
    

    def update_junction_data(self, current_time:float):
        for junction_id in type(self).junction_to_vehicles:
            to_be_removed = []
            for v in type(self).junction_to_vehicles[junction_id]:
                if (v.get_next_junction().getID() != junction_id or not v.isActive): #and type(self).arrival_times[v] < current_time:
                    to_be_removed.append(v)
            for v in to_be_removed:
                type(self).junction_to_vehicles[junction_id].remove(v)
                type(self).reserved_times.pop(v)
                type(self).arrival_times.pop(v)



    def get_arrival_time(self, reserved_time, vehicle):
        return reserved_time + (vehicle.get_time_to_cross_next_junction() * 1.2)


    def update_reserved_times(self, junction_id:str, index):
        queue = type(self).junction_to_vehicles[junction_id]
        index += 1
        while index < len(queue):
            last_vehicle:Vehicle = queue[index - 1]
            this_vehicle:Vehicle = queue[index]
            type(self).reserved_times[this_vehicle] = type(self).arrival_times[last_vehicle]
            type(self).arrival_times[this_vehicle] = self.get_arrival_time(type(self).reserved_times[this_vehicle], this_vehicle)
            index += 1


    def request_state_at_junction(self, vehicle:Vehicle, vehicles:list, junction_id:str) -> VehicleState:
        if not junction_id in type(self).junction_to_vehicles:
            type(self).junction_to_vehicles[junction_id] = []
        current_time = traci.simulation.getTime()
        if vehicle not in type(self).reserved_times:
            self.insert_into_queue(vehicle, junction_id, current_time)
        reserved_time = type(self).reserved_times[vehicle]
        if current_time >= reserved_time:
            return VehicleState.CROSSING
        else:
            return VehicleState.WAITING  


    def decide_state(self, vehicle:Vehicle, conflicting_vehicles: dict):
        current_time = traci.simulation.getTime()
        if type(self).last_recorded_time != current_time:
            type(self).last_recorded_time = current_time
            self.update_junction_data(current_time)
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if self.is_conflicting_same_lane(vehicle, other_vehicle):
                return VehicleState.WAITING

        if vehicle.get_distance_to_junction() <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION and vehicle.currentState != VehicleState.CROSSING:
            junction_id = vehicle.get_next_junction().getID()
            vehicles = copy.copy(conflicting_vehicles["same_junction"])
            vehicles.append(vehicle)
            return self.request_state_at_junction(vehicle, vehicles, junction_id)
        
        for other_vehicle in conflicting_vehicles["visible"]:
            if self.is_conflicting_visible(vehicle, other_vehicle):
                return VehicleState.WAITING
        
        return self.decide_state_no_conflicts(vehicle)
    

    def is_conflicting_same_junction(self, vehicle:Vehicle, other_vehicle:Vehicle) -> bool:
        return super().is_conflicting_same_junction(vehicle, other_vehicle)
    

    def is_conflicting_same_lane(self, vehicle:Vehicle, other_vehicle:Vehicle) -> bool:
        return super().is_conflicting_same_lane(vehicle, other_vehicle)
    

    def is_conflicting_visible(self, vehicle:Vehicle, other_vehicle:Vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def decide_state_no_conflicts(self, vehicle:Vehicle) -> VehicleState:
        return super().decide_state_no_conflicts(vehicle)