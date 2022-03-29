from src.vehicle.policy.policy import Policy
from src.vehicle.vehicle_state import VehicleState

class FirstComeFirstServePolicy(Policy):

    def __init__(self) -> None:
        self.vehicles_ahead_of_queue:dict = {}     # Queue containing other vehicles that go first
        super().__init__()


    def decide_state(self, vehicle, conflicting_vehicles:dict):
        return super().decide_state(vehicle, conflicting_vehicles)
    

    def can_get_priority(self, vehicle, other_vehicle) -> bool:
        if other_vehicle.currentTimeSpentWaiting < vehicle.currentTimeSpentWaiting:
            return True
        return False
    

    def is_conflicting_same_junction(self, vehicle, other_vehicle) -> bool:
        next_junction = vehicle.nextJunction
        distance_to_junction = vehicle.get_distance_to_junction(next_junction)
        
        # Always allow other vehicles that are already crossing to pass first
        if other_vehicle.currentState == VehicleState.CROSSING and vehicle.get_distance_to_junction(next_junction) <= FirstComeFirstServePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
            return True
        if vehicle.currentState != VehicleState.CROSSING:
            if other_vehicle in self.vehicles_ahead_of_queue:
                if not self.can_get_priority(vehicle, other_vehicle):
                    return True
                else:
                    self.vehicles_ahead_of_queue.pop(other_vehicle)
            else:
                must_wait = False
                if other_vehicle.get_distance_to_junction(next_junction) < distance_to_junction: 
                    must_wait = True
                elif other_vehicle.get_distance_to_junction(next_junction) == distance_to_junction and other_vehicle.currentTimeSpentWaiting > vehicle.currentTimeSpentWaiting:
                    must_wait = True
                if must_wait and vehicle.get_distance_to_junction(next_junction) <= FirstComeFirstServePolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
                    if other_vehicle.currentState != VehicleState.CROSSING:
                        self.vehicles_ahead_of_queue[other_vehicle] = True
                    return True
        return False
    

    def is_conflicting_same_lane(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_same_lane(vehicle, other_vehicle)
    

    def is_conflicting_visible(self, vehicle, other_vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def decide_state_no_conflicts(self, vehicle) -> VehicleState:
        self.vehicles_ahead_of_queue = {}
        return super().decide_state_no_conflicts(vehicle)