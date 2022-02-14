from vehicle.policy.policy import Policy
from vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):
    MIN_DISTANCE_FROM_JUNCTION = 8
    MIN_DISTANCE_FROM_VEHICLE = 10

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()
        
        for other_vehicle in conflicting_vehicles["same_junction"]:
            other_junction_id = next_junction.getID()
            junction_id = other_vehicle.nextJunction.getID()
            if junction_id == other_junction_id and \
                other_vehicle.get_distance_to_junction() <= distance_to_junction and \
                vehicle.get_distance_to_junction() <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_JUNCTION and \
                other_vehicle.currentState == VehicleState.DRIVING:
                return VehicleState.WAITING
        
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if vehicle.get_distance_to_vehicle(other_vehicle) <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_VEHICLE and \
                other_vehicle.get_distance_to_junction() <= distance_to_junction:
                return VehicleState.WAITING

        return VehicleState.DRIVING