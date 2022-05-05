import src.vehicle.policy.policy as policy
from src.vehicle.vehicle_state import VehicleState
import src.vehicle.policy.utils as utils

class FirstComeFirstServePolicy(policy.VehiclePolicy):

    def __init__(self, vehicle) -> None:
        self.vehicles_ahead_of_queue:dict = {}     # Queue containing other vehicles that go first
        super().__init__(vehicle)
        self.time_spent_waiting = 0


    def process_query_data(self, _):
        response_data:dict = {
            "time_spent_waiting"  : self.time_spent_waiting
        }
        return response_data
            

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        state = super().decide_state(vehicle, conflicting_vehicles)
        if state == VehicleState.WAITING:
            self.time_spent_waiting += 1
        else:
            self.time_spent_waiting = 0
        return state
    

    def can_remove_from_queue(self, vehicle, other_vehicle) -> bool:
        message = policy.QueryMessage(self.vehicle.vehicleId, "")
        policy.SharedNetwork.send_message_to_vehicle(other_vehicle.vehicleId, message)
        data = self.message_buffer.pop(-1).data
        if data["time_spent_waiting"] <= self.time_spent_waiting:
            return True
        return False
    

    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction(next_junction)
        
        if vehicle.currentState != VehicleState.CROSSING:
            if other_vehicle in self.vehicles_ahead_of_queue:
                if not self.can_remove_from_queue(vehicle, other_vehicle):
                    return True
                else:
                    self.vehicles_ahead_of_queue.pop(other_vehicle)
            else:
                must_wait = False
                message = policy.QueryMessage(self.vehicle.vehicleId, "")
                policy.SharedNetwork.send_message_to_vehicle(other_vehicle.vehicleId, message)
                data = self.message_buffer.pop(-1).data
                if other_vehicle.get_distance_to_junction(next_junction) < distance_to_junction: 
                    must_wait = True
                elif other_vehicle.get_distance_to_junction(next_junction) == distance_to_junction and data["time_spent_waiting"] > self.time_spent_waiting:
                    must_wait = True
                if must_wait and vehicle.get_distance_to_junction(next_junction) <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION:
                    self.vehicles_ahead_of_queue[other_vehicle] = True
                    return True
        return False
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_same_lane(vehicle, other_vehicle)
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def confirm_no_conflicts(self, vehicle, new_state, conflicting_vehicles: dict):
        if new_state == VehicleState.CROSSING:
            reserve_junction_message = policy.ReserveJunctionMessage(vehicle.vehicleId, vehicle.nextJunction.getID())
            for other_vehicle in conflicting_vehicles["same_junction"]:
                policy.SharedNetwork.send_message_to_vehicle(other_vehicle.vehicleId, reserve_junction_message)
            while len(self.message_buffer) > 0:
                message:policy.VehicleMessage = self.message_buffer.pop(0)
                if type(message) == policy.DenyMessage:
                    return False
        self.vehicles_ahead_of_queue = {}
        return True


    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        return super().decide_state_no_conflicts(vehicle)
