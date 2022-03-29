from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle import Vehicle
from src.vehicle.vehicle_state import VehicleState
import copy

class SVOGroupPolicy(Policy):

    def decide_state(self, vehicle:Vehicle, conflicting_vehicles: dict):
        print("aaa")
        if vehicle.get_distance_to_junction() <= SVOGroupPolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
            other_vehicles_at_junction = conflicting_vehicles["same_junction"]
            svo_utility = vehicle.get_social_value_orientation_utility_group_average(other_vehicles_at_junction)
            for other_vehicle in other_vehicles_at_junction:
                ov:Vehicle = other_vehicle
                others = copy.copy(other_vehicles_at_junction)
                others.add(vehicle)
                others.remove(ov)
                other_svo_utility = ov.get_social_value_orientation_utility_group_average(others)
                print(f"Comparing {svo_utility} with {other_svo_utility}")
                if svo_utility < other_svo_utility:
                    return VehicleState.WAITING
        
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