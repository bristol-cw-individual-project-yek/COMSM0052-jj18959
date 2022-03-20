from src.vehicle.vehicle_state import VehicleState

class Policy:
    MIN_WAITING_DISTANCE_FROM_JUNCTION = 10
    MIN_CROSSING_DISTANCE_FROM_JUNCTION = 8
    MIN_DISTANCE_FROM_VEHICLE_SAME_LANE = 10
    MIN_POLICY_IGNORE_DISTANCE = 15
    # Default conflict resolution protocol.
    # If any conflicting vehicles are detected that are driving, the vehicle just stops
    # Otherwise, keep driving
    def decide_state(self, vehicle, conflicting_vehicles:dict):
        for other_vehicle in conflicting_vehicles["same_junction"]:
            if other_vehicle.currentState == VehicleState.DRIVING:
                return VehicleState.WAITING
        return VehicleState.DRIVING