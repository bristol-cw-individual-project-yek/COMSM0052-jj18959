from src.vehicle.vehicle_state import VehicleState
from enum import Enum
import src.vehicle.policy.utils as utils

# TODO: Move all this communication stuff to new file?
class VehicleMessage():
    def __init__(self, senderID:str) -> None:
        self.senderID:str = senderID


class ReserveJunctionMessage(VehicleMessage):
    def __init__(self, senderID:str, junctionID:str) -> None:
        super().__init__(senderID)
        self.junctionID:str = junctionID


class ConfirmMessage(VehicleMessage):
    def __init__(self, senderID:str) -> None:
        super().__init__(senderID)


class DenyMessage(VehicleMessage):
    def __init__(self, senderID:str) -> None:
        super().__init__(senderID)


class QueryMessage(VehicleMessage):
    def __init__(self, senderID:str, data) -> None:
        self.data = data
        super().__init__(senderID)


class ResponseMessage(VehicleMessage):
    def __init__(self, senderID:str, data) -> None:
        self.data = data
        super().__init__(senderID)


class SharedNetwork():
    vehicle_id_to_policy:dict = {}
    arbiter_id_to_policy:dict = {}

    def send_message_to_vehicle(recipient_id:str, message:VehicleMessage):
        try:
            recipient_policy = SharedNetwork.vehicle_id_to_policy[recipient_id]
            recipient_policy.receive_message_from_vehicle(message)
        except KeyError:
            print(f"Failed to send message to {recipient_id}")
            raise
    
    def send_message_to_arbiter(junction_id:str, vehicle):
        try:
            arbiter_policy = SharedNetwork.arbiter_id_to_policy[junction_id]
            return arbiter_policy.receive_message(vehicle)
        except KeyError:
            print(f"Failed to send message to {junction_id}")
            raise
    

    def has_arbiter(junction_id:str):
        return junction_id in SharedNetwork.arbiter_id_to_policy



class VehiclePolicy:
    """Default conflict resolution protocol.

    If any conflicting vehicles are detected that are driving, the vehicle just stops.

    Otherwise, keep driving.
    """
    MIN_WAITING_DISTANCE_FROM_JUNCTION = 10
    MIN_CROSSING_DISTANCE_FROM_JUNCTION = 9
    MIN_DISTANCE_FROM_VEHICLE_SAME_LANE = 10
    MIN_POLICY_IGNORE_DISTANCE = 15


    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.message_buffer:list = []
        SharedNetwork.vehicle_id_to_policy[vehicle.vehicleId] = self


    def process_query_data(self, query_data):
        return query_data


    def receive_message_from_vehicle(self, message:VehicleMessage):
        if type(message) == ReserveJunctionMessage:
            if self.vehicle.currentState == VehicleState.CROSSING:
                confirm_or_deny = DenyMessage(self.vehicle.vehicleId)
            else:
                confirm_or_deny = ConfirmMessage(self.vehicle.vehicleId)
                self.message_buffer.append(message)
            SharedNetwork.send_message_to_vehicle(message.senderID, confirm_or_deny)
        if type(message) == QueryMessage:
            data = message.data
            response = ResponseMessage(self.vehicle.vehicleId, self.process_query_data(data))
            SharedNetwork.send_message_to_vehicle(message.senderID, response)
        if type(message) == ResponseMessage:
            self.message_buffer.append(message)
        if type(message) == ConfirmMessage or type(message) == DenyMessage:
            self.message_buffer.append(message)


    def handle_state_at_junction(self, conflicting_vehicles:dict):
        junction_id = self.vehicle.nextJunction.getID()
        must_wait_at_junction = False
        while len(self.message_buffer) > 0:
            message:VehicleMessage = self.message_buffer.pop(0)
            if type(message) == ReserveJunctionMessage and message.junctionID == self.vehicle.nextJunction.getID():
                must_wait_at_junction = True
        if self.vehicle.get_distance_to_junction() <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION:
            if must_wait_at_junction:
                return VehicleState.WAITING 
            for other_vehicle in conflicting_vehicles["same_junction"]:
                if self.is_conflicting_same_junction(self.vehicle, other_vehicle):
                    return VehicleState.WAITING
            return VehicleState.CROSSING
        return VehicleState.DRIVING
    

    def decide_state(self, conflicting_vehicles:dict):
        junction_id = self.vehicle.nextJunction.getID()
        if self.vehicle.get_distance_to_junction() <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION and SharedNetwork.has_arbiter(junction_id):
            return SharedNetwork.send_message_to_arbiter(junction_id, self.vehicle)
        else:
            return self._decide_state(self.vehicle, conflicting_vehicles)

    
    def _decide_state(self, vehicle, conflicting_vehicles:dict):

        for other_vehicle in conflicting_vehicles["same_lane"]:
            if self.is_conflicting_same_lane(vehicle, other_vehicle):
                return VehicleState.WAITING

        for other_vehicle in conflicting_vehicles["visible"]:
            if self.is_conflicting_visible(vehicle, other_vehicle):
                return VehicleState.WAITING

        #state = self.decide_state_no_conflicts(vehicle)
        state = self.handle_state_at_junction(conflicting_vehicles)
        no_conflicts = self.confirm_no_conflicts(vehicle, state, conflicting_vehicles)

        if no_conflicts:
            return state
        else:
            return VehicleState.WAITING

    
    def confirm_no_conflicts(self, vehicle, new_state, conflicting_vehicles:dict):
        return True


    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        if other_vehicle.currentState == VehicleState.CROSSING and vehicle.get_distance_to_junction() <= VehiclePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
            return True
        return False
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        if vehicle.currentState != VehicleState.CROSSING:
            next_junction = vehicle.nextJunction
            distance_to_junction = vehicle.get_distance_to_junction()
            if vehicle.get_distance_to_vehicle(other_vehicle) <= VehiclePolicy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
                other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
                return True
        return False
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return False
    

    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        distance_to_junction = vehicle.get_distance_to_junction()
        if distance_to_junction <= VehiclePolicy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING
