from vehicle.policy.policy import Policy
from vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()
        
        for other_vehicle in conflicting_vehicles["same_junction"]:
            if (other_vehicle.get_distance_to_junction(next_junction) < distance_to_junction or \
                other_vehicle.currentState == VehicleState.CROSSING) and \
                vehicle.get_distance_to_junction(next_junction) <= FirstComeFirstServePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION and other_vehicle.currentState != VehicleState.WAITING:
                return VehicleState.WAITING
        
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if vehicle.get_distance_to_vehicle(other_vehicle) <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
                other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
                return VehicleState.WAITING
        
        if distance_to_junction <= FirstComeFirstServePolicy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING