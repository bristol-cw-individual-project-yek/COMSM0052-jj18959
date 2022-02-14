from vehicle.policy.policy import Policy
from vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):
    MIN_DISTANCE_FROM_JUNCTION = 8
    MIN_DISTANCE_FROM_VEHICLE = 10

    def decide_state(self, vehicle, conflicting_vehicles:list):
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction()
        for other_vehicle in conflicting_vehicles:
            if other_vehicle.nextJunction.getID() == next_junction.getID() and \
                other_vehicle.get_distance_to_junction() <= distance_to_junction and \
                (vehicle.get_distance_to_vehicle(other_vehicle) <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_VEHICLE or \
                vehicle.get_distance_to_junction() <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_JUNCTION):
                return VehicleState.WAITING
        return VehicleState.DRIVING