from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        return super().decide_state(vehicle, conflicting_vehicles)
    

    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()
        if (other_vehicle.get_distance_to_junction(next_junction) < distance_to_junction or \
            other_vehicle.currentState == VehicleState.CROSSING) and \
            vehicle.get_distance_to_junction(next_junction) <= FirstComeFirstServePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION and other_vehicle.currentState != VehicleState.WAITING:
            return True
        return False
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()
        if vehicle.get_distance_to_vehicle(other_vehicle) <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
            other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
            return True
        return False
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        distance_to_junction = vehicle.get_distance_to_junction()
        if distance_to_junction <= FirstComeFirstServePolicy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING