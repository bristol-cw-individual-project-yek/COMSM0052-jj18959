from vehicle.policy.policy import Policy
from vehicle.vehicle_state import VehicleState

class PriorityPolicy(Policy):
    MIN_WAITING_DISTANCE_FROM_JUNCTION = 10
    MIN_CROSSING_DISTANCE_FROM_JUNCTION = 8
    MIN_DISTANCE_FROM_VEHICLE_SAME_LANE = 10

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()

        #if vehicle.currentState == VehicleState.DRIVING or vehicle.currentState == VehicleState.WAITING:
        for other_vehicle in conflicting_vehicles["same_junction"]:
            if ((other_vehicle.priority < vehicle.priority and not other_vehicle in conflicting_vehicles["same_lane"]) or \
                other_vehicle.currentState == VehicleState.CROSSING) and \
                vehicle.get_distance_to_junction(next_junction) <= PriorityPolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION and other_vehicle.currentState != VehicleState.WAITING:
                return VehicleState.WAITING
        
        for other_vehicle in conflicting_vehicles["same_lane"]:
            if vehicle.get_distance_to_vehicle(other_vehicle) < PriorityPolicy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
                other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
                #print("Same lane conflict")
                return VehicleState.WAITING
        
        if distance_to_junction <= PriorityPolicy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING