from src.vehicle.vehicle_state import VehicleState
from enum import Enum
import src.vehicle.policy.utils as utils


class VehicleMessage():
    def __init__(self, senderID:str) -> None:
        self.senderID:str = senderID


class ReserveJunctionMessage(VehicleMessage):
    def __init__(self, senderID:str, junctionID:str) -> None:
        super().__init__(senderID)
        self.junctionID:str = junctionID


class Policy:
    """Default conflict resolution protocol.

    If any conflicting vehicles are detected that are driving, the vehicle just stops.

    Otherwise, keep driving.
    """
    MIN_WAITING_DISTANCE_FROM_JUNCTION = 10
    MIN_CROSSING_DISTANCE_FROM_JUNCTION = 9
    MIN_DISTANCE_FROM_VEHICLE_SAME_LANE = 10
    MIN_POLICY_IGNORE_DISTANCE = 15


    def __init__(self):
        self.received_messages:list = []


    def receive_message_from_vehicle(self, message:VehicleMessage):
        self.received_messages.append(message)

    
    def decide_state(self, vehicle, conflicting_vehicles:dict):
        must_wait_at_junction = False
        while len(self.received_messages) > 0:
            message:VehicleMessage = self.received_messages.pop(0)
            print(type(message))
            if type(message) == ReserveJunctionMessage and message.junctionID == vehicle.nextJunction.getID():
                print("Received message")
                must_wait_at_junction = True

        for other_vehicle in conflicting_vehicles["same_lane"]:
            if self.is_conflicting_same_lane(vehicle, other_vehicle):
                return VehicleState.WAITING

        if vehicle.get_distance_to_junction() <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION:
            if must_wait_at_junction:
                print("Forced to wait")
                return VehicleState.WAITING 
            for other_vehicle in conflicting_vehicles["same_junction"]:
                if self.is_conflicting_same_junction(vehicle, other_vehicle):
                    return VehicleState.WAITING
        
        for other_vehicle in conflicting_vehicles["visible"]:
            if self.is_conflicting_visible(vehicle, other_vehicle):
                return VehicleState.WAITING

        state = self.decide_state_no_conflicts(vehicle)
        self.send_messages_no_conflicts(vehicle, state, conflicting_vehicles)

        return state

    
    def send_messages_no_conflicts(self, vehicle, new_state, conflicting_vehicles:dict):
        if new_state == VehicleState.CROSSING:
            reserve_junction_message = ReserveJunctionMessage(vehicle.vehicleId, vehicle.nextJunction.getID())
            for other_vehicle in conflicting_vehicles["same_junction"]:
                # TODO: Make this a straight call to the other vehicle
                other_vehicle.conflictResolutionPolicy.receive_message_from_vehicle(reserve_junction_message)


    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        if other_vehicle.currentState == VehicleState.CROSSING and vehicle.get_distance_to_junction() <= Policy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
            return True
        return False
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        if vehicle.currentState != VehicleState.CROSSING:
            next_junction = vehicle.nextJunction
            distance_to_junction = vehicle.get_distance_to_junction()
            if vehicle.get_distance_to_vehicle(other_vehicle) <= Policy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
                other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
                return True
        return False
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return False
    

    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        distance_to_junction = vehicle.get_distance_to_junction()
        if distance_to_junction <= Policy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING
