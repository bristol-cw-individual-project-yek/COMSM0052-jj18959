from numpy import True_
from src.vehicle.vehicle_state import VehicleState


class Policy:
    """Default conflict resolution protocol.

    If any conflicting vehicles are detected that are driving, the vehicle just stops.

    Otherwise, keep driving.
    """
    MIN_WAITING_DISTANCE_FROM_JUNCTION = 10
    MIN_CROSSING_DISTANCE_FROM_JUNCTION = 9
    MIN_DISTANCE_FROM_VEHICLE_SAME_LANE = 10
    MIN_POLICY_IGNORE_DISTANCE = 15

    
    def decide_state(self, vehicle, conflicting_vehicles:dict):
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if self.is_conflicting_same_lane(vehicle, other_vehicle):
                return VehicleState.WAITING

        if vehicle.get_distance_to_junction() <= type(self).MIN_WAITING_DISTANCE_FROM_JUNCTION:
            for other_vehicle in conflicting_vehicles["same_junction"]:
                if self.is_conflicting_same_junction(vehicle, other_vehicle):
                    return VehicleState.WAITING
        
        for other_vehicle in conflicting_vehicles["visible"]:
            if self.is_conflicting_visible(vehicle, other_vehicle):
                return VehicleState.WAITING
        
        return self.decide_state_no_conflicts(vehicle)

    
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
