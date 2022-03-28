from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle_state import VehicleState

class CustomTestPolicy(Policy):

    def decide_state(self, vehicle, conflicting_vehicles: dict):
        return super().decide_state(vehicle, conflicting_vehicles)
    

    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_same_junction(vehicle, other_vehicle)
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_same_lane(vehicle, other_vehicle)
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        return super().decide_state_no_conflicts(vehicle)