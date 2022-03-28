from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):

    def __init__(self) -> None:
        self.vehicles_ahead_of_queue:dict = {}     # Queue containing other vehicles that go first
        super().__init__()


    def decide_state(self, vehicle, conflicting_vehicles:dict):
        return super().decide_state(vehicle, conflicting_vehicles)
    

    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        if vehicle.currentState != VehicleState.CROSSING:
            next_junction = vehicle.nextJunction
            distance_to_junction = vehicle.get_distance_to_junction(next_junction)
            if other_vehicle in self.vehicles_ahead_of_queue:
                print(f"Conflict: {vehicle.vehicleId} and {other_vehicle.vehicleId} ({other_vehicle.vehicleId} ahead of queue)")
                return True
            else:
                must_wait = False
                if other_vehicle.get_distance_to_junction(next_junction) < distance_to_junction: 
                    print(f"Conflict: {vehicle.vehicleId} and {other_vehicle.vehicleId} (time spent waiting)")
                    must_wait = True
                elif other_vehicle.get_distance_to_junction(next_junction) == distance_to_junction and other_vehicle.timeSpentWaiting > vehicle.timeSpentWaiting:
                    print(f"Conflict: {vehicle.vehicleId} and {other_vehicle.vehicleId} (distance)")
                    must_wait = True
                elif other_vehicle.currentState == VehicleState.CROSSING:
                    print(f"Conflict: {vehicle.vehicleId} and {other_vehicle.vehicleId} ({other_vehicle.vehicleId} crossing)")
                    must_wait = True
                if must_wait and vehicle.get_distance_to_junction(next_junction) <= FirstComeFirstServePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
                    if other_vehicle.currentState != VehicleState.CROSSING:
                        self.vehicles_ahead_of_queue[other_vehicle] = True
                    return True
        return False
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        if vehicle.currentState != VehicleState.CROSSING:
            next_junction = vehicle.nextJunction
            distance_to_junction = vehicle.get_distance_to_junction()
            if vehicle.get_distance_to_vehicle(other_vehicle) <= FirstComeFirstServePolicy.MIN_DISTANCE_FROM_VEHICLE_SAME_LANE and \
                other_vehicle.get_distance_to_junction(next_junction) <= distance_to_junction:
                return True
        return False
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        self.vehicles_ahead_of_queue = {}
        distance_to_junction = vehicle.get_distance_to_junction()
        if distance_to_junction <= FirstComeFirstServePolicy.MIN_CROSSING_DISTANCE_FROM_JUNCTION:
            return VehicleState.CROSSING

        return VehicleState.DRIVING