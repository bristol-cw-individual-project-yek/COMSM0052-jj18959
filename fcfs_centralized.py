from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle import Vehicle
from src.vehicle.vehicle_state import VehicleState
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
        if vehicle.get_distance_to_junction() < other_vehicle.get_distance_to_junction():
            return True
        else:
            return False


    def insert_into_queue(self, vehicle:Vehicle, junction_id:str) -> None:
        queue:list = FCFS_CentralizedPolicy.junction_to_queue[junction_id]
        if not vehicle in queue:
            index = len(queue) - 1
            found:bool = False
            while index >= 0 and not found:
                other_veh:Vehicle = queue[index]
                if self.can_swap(vehicle, other_veh):
                    index -= 1
                else:
                    found = True
            queue.insert(index + 1, vehicle)
    

    def get_initial_reserve_time(self, vehicle:Vehicle, junction_id:str, current_time:float) -> float:
        if not junction_id in FCFS_CentralizedPolicy.junction_to_vehicles:
            FCFS_CentralizedPolicy.junction_to_vehicles[junction_id] = []
        result = current_time
        if len(FCFS_CentralizedPolicy.junction_to_vehicles[junction_id]) == 0:
            return result
        else:
            for other_vehicle in FCFS_CentralizedPolicy.junction_to_vehicles[junction_id]:
                if other_vehicle.get_next_junction().getID() == junction_id and other_vehicle.isActive:
                    result = max(result, FCFS_CentralizedPolicy.arrival_times[other_vehicle])
            return result
    

    def reset_junction_data(current_time:float):
        for junction_id in FCFS_CentralizedPolicy.junction_to_vehicles:
            to_be_removed = []
            for v in FCFS_CentralizedPolicy.junction_to_vehicles[junction_id]:
                if (v.get_next_junction().getID() != junction_id or not v.isActive) and FCFS_CentralizedPolicy.arrival_times[v] < current_time:
                    to_be_removed.append(v)
            for v in to_be_removed:
                FCFS_CentralizedPolicy.junction_to_vehicles[junction_id].remove(v)
                FCFS_CentralizedPolicy.reserved_times.pop(v)
                FCFS_CentralizedPolicy.arrival_times.pop(v)


    def request_state_at_junction(self, vehicle:Vehicle, vehicles:list, junction_id:str) -> VehicleState:
        current_time = traci.simulation.getTime()
        if FCFS_CentralizedPolicy.last_recorded_time != current_time:
            FCFS_CentralizedPolicy.last_recorded_time = current_time
            FCFS_CentralizedPolicy.reset_junction_data(current_time)
            #print(f"---------Step: {current_time}---------")
            #print("Reserved:")
            #self.print_schedule(FCFS_CentralizedPolicy.reserved_times)
            #print("Arrival:")
            #self.print_schedule(FCFS_CentralizedPolicy.arrival_times)
            #print("--------------------------------------")
        if vehicle in FCFS_CentralizedPolicy.reserved_times:
            if FCFS_CentralizedPolicy.reserved_times[vehicle] > current_time:
                return VehicleState.WAITING
            else:
                return VehicleState.CROSSING
        else:
            reserved_time = self.get_initial_reserve_time(vehicle, junction_id, current_time)
            arrival_time = reserved_time + vehicle.get_time_to_cross_next_junction()
            #is_clear = True
            #to_be_removed = []
            for other_vehicle in FCFS_CentralizedPolicy.junction_to_vehicles[junction_id]:
                if other_vehicle.get_next_junction().getID() == junction_id and other_vehicle.isActive:
                    if (not self.can_swap(vehicle, other_vehicle)) or other_vehicle.currentState == VehicleState.CROSSING:
                        #is_clear = False
                        pass
                    else:
                        try:
                            temp_reserved_time = FCFS_CentralizedPolicy.arrival_times[other_vehicle]
                            FCFS_CentralizedPolicy.reserved_times[other_vehicle] = reserved_time
                            FCFS_CentralizedPolicy.arrival_times[other_vehicle] = reserved_time + other_vehicle.get_time_to_cross_next_junction()
                            reserved_time = temp_reserved_time
                            arrival_time = reserved_time + vehicle.get_time_to_cross_next_junction()
                        except Exception as e:
                            raise e
                else:
                    pass
                    #if FCFS_CentralizedPolicy.arrival_times[other_vehicle] < current_time:
                        #to_be_removed.append(other_vehicle)
            #for v in to_be_removed:
            #    FCFS_CentralizedPolicy.junction_to_vehicles[junction_id].remove(v)
            #    FCFS_CentralizedPolicy.reserved_times.pop(v) 
            FCFS_CentralizedPolicy.reserved_times[vehicle] = reserved_time
            FCFS_CentralizedPolicy.arrival_times[vehicle] =  arrival_time
            FCFS_CentralizedPolicy.junction_to_vehicles[junction_id].append(vehicle)
            if current_time >= reserved_time:
                return VehicleState.CROSSING
            else:
                return VehicleState.WAITING  


    def decide_state(self, vehicle:Vehicle, conflicting_vehicles: dict):
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if self.is_conflicting_same_lane(vehicle, other_vehicle):
                return VehicleState.WAITING

        if vehicle.get_distance_to_junction() <= FCFS_CentralizedPolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION and vehicle.currentState != VehicleState.CROSSING:
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