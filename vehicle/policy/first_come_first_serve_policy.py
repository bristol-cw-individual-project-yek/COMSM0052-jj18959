from vehicle.policy.policy import Policy
from vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):
    def decide_state(self, vehicle, conflicting_vehicles:list):
        distance_to_junction = vehicle.get_distance_to_junction()
        for other_vehicle in conflicting_vehicles:
            if other_vehicle.get_distance_to_junction() <= distance_to_junction:
                return VehicleState.WAITING
        return VehicleState.DRIVING