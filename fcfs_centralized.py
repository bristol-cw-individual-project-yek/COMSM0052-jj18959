from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle import Vehicle
from src.vehicle.vehicle_state import VehicleState
import traci
import copy

class FCFS_CentralizedPolicy(Policy):

    junction_to_queue:dict              = {}
    junction_to_last_update_time:dict   = {}


    def can_swap(self, vehicle: Vehicle, queue:list, index:int) -> bool:
        other_veh:Vehicle = queue[index]
        if vehicle.get_distance_to_junction() < other_veh.get_distance_to_junction():
            return True
        elif vehicle.get_distance_to_junction() == other_veh.get_distance_to_junction() and vehicle.currentTimeSpentWaiting > other_veh.currentTimeSpentWaiting:
            return True
        else:
            return False


    def insert_into_queue(self, vehicle:Vehicle, junction_id:str) -> None:
        queue:list = FCFS_CentralizedPolicy.junction_to_queue[junction_id]
        if not vehicle in queue:
            index = len(queue) - 1
            found:bool = False
            while index >= 0 and not found:
                if self.can_swap(vehicle, queue, index):
                    index -= 1
                else:
                    found = True
            queue.insert(index + 1, vehicle)


    def request_state_at_junction(self, vehicle:Vehicle, vehicles:list, junction_id:str) -> VehicleState:
        current_time = traci.simulation.getTime()
        if not junction_id in FCFS_CentralizedPolicy.junction_to_queue:
            FCFS_CentralizedPolicy.junction_to_queue[junction_id] = []
        if not junction_id in FCFS_CentralizedPolicy.junction_to_last_update_time or FCFS_CentralizedPolicy.junction_to_last_update_time[junction_id] < current_time:
            FCFS_CentralizedPolicy.junction_to_last_update_time[junction_id] = current_time
            for v in vehicles:
                self.insert_into_queue(v, junction_id)
        if not FCFS_CentralizedPolicy.junction_to_queue[junction_id][0] in vehicles:
            FCFS_CentralizedPolicy.junction_to_queue[junction_id].pop(0)
        if FCFS_CentralizedPolicy.junction_to_queue[junction_id][0] == vehicle:
            return VehicleState.CROSSING
        return VehicleState.WAITING    


    def decide_state(self, vehicle:Vehicle, conflicting_vehicles: dict):
        if vehicle.get_distance_to_junction() <= FCFS_CentralizedPolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION and vehicle.currentState != VehicleState.CROSSING:
            #if len(conflicting_vehicles["same_junction"]) > 0:
            junction_id = vehicle.get_next_junction().getID()
            vehicles = copy.copy(conflicting_vehicles["same_junction"])
            vehicles.append(vehicle)
            return self.request_state_at_junction(vehicle, vehicles, junction_id)
        
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if self.is_conflicting_same_lane(vehicle, other_vehicle):
                return VehicleState.WAITING
        
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