import src.vehicle.policy.policy as policy
from src.vehicle.vehicle_state import VehicleState
import src.vehicle.policy.utils as utils

class FirstComeFirstServePolicy(policy.Policy):

    def __init__(self, vehicle) -> None:
        self.vehicles_ahead_of_queue:dict = {}     # Queue containing other vehicles that go first
        super().__init__(vehicle)


    def receive_message_from_vehicle(self, message:policy.VehicleMessage):
        if type(message) == policy.ReserveJunctionMessage:
            if self.vehicle.currentState == VehicleState.CROSSING:
                confirm_or_deny = policy.DenyMessage(self.vehicle.vehicleId)
            else:
                confirm_or_deny = policy.ConfirmMessage(self.vehicle.vehicleId)
                self.received_messages.append(message)
            #message.sender.conflictResolutionPolicy.receive_message_from_vehicle(confirm_or_deny)
            policy.SharedNetwork.send_message(message.senderID, confirm_or_deny)
            

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        return super().decide_state(vehicle, conflicting_vehicles)
    

    def can_remove_from_queue(self, vehicle, other_vehicle) -> bool:
        if not utils.is_in_junction(other_vehicle, vehicle.get_next_junction()):
            return True
        return False
    

    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction(next_junction)
        
        # Always allow other vehicles that are already crossing to pass first
        #if other_vehicle.currentState == VehicleState.CROSSING and vehicle.get_distance_to_junction(next_junction) <= FirstComeFirstServePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
        #    return True
        if vehicle.currentState != VehicleState.CROSSING:
            if other_vehicle in self.vehicles_ahead_of_queue:
                if not self.can_remove_from_queue(vehicle, other_vehicle):
                    return True
                else:
                    self.vehicles_ahead_of_queue.pop(other_vehicle)
            else:
                must_wait = False
                if other_vehicle.get_distance_to_junction(next_junction) < distance_to_junction: 
                    must_wait = True
                elif other_vehicle.get_distance_to_junction(next_junction) == distance_to_junction and other_vehicle.currentTimeSpentWaiting > vehicle.currentTimeSpentWaiting:
                    must_wait = True
                if must_wait and vehicle.get_distance_to_junction(next_junction) <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION:
                    if other_vehicle.currentState != VehicleState.CROSSING:
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
                policy.SharedNetwork.send_message(other_vehicle.vehicleId, reserve_junction_message)
            while len(self.received_messages) > 0:
                message:policy.VehicleMessage = self.received_messages.pop(0)
                if type(message) == policy.DenyMessage:
                    return False
        return True


    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        self.vehicles_ahead_of_queue = {}
        return super().decide_state_no_conflicts(vehicle)