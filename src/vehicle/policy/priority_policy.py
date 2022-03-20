from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle_state import VehicleState

class PriorityPolicy(Policy):

    def decide_state(self, vehicle, conflicting_vehicles:dict):
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()

        if vehicle.currentState != VehicleState.CROSSING:
            for other_vehicle in conflicting_vehicles["same_junction"]:
                # Aside from checking for priority, we also need to ignore vehicles with a higher priority in the same lane
                # to avoid stopping when a higher priority vehicle is behind this one (the loop below handles the case where
                # it is in front). We also need to check the higher priority vehicle's distance to the junction, so that the
                # vehicle with lower priority doesn't needlessly stop while there is still space to move (and cause traffic jams).
                if ((other_vehicle.priority < vehicle.priority and not other_vehicle in conflicting_vehicles["same_lane"] and other_vehicle.get_distance_to_junction(next_junction) < PriorityPolicy.MIN_POLICY_IGNORE_DISTANCE) or \
                    other_vehicle.currentState == VehicleState.CROSSING) and\
                    vehicle.get_distance_to_junction(next_junction) <= PriorityPolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION and other_vehicle.currentState != VehicleState.WAITING:
                    return VehicleState.WAITING
            
            for other_vehicle in conflicting_vehicles["same_lane"]:
                if vehicle.get_distance_to_vehicle(other_vehicle) < PriorityPolicy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
                    other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
                    return VehicleState.WAITING
        
        if distance_to_junction <= PriorityPolicy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING