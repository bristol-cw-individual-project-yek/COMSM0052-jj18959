from vehicle_state import VehicleState

class VehicleProtocol:
    
    # Default conflict resolution protocol.
    # If any conflicting vehicles are detected that are driving, the vehicle just stops
    # Otherwise, keep driving
    def decide_state(self, vehicle, conflicting_vehicles):
        for other_vehicle in conflicting_vehicles:
            if other_vehicle.currentState == VehicleState.DRIVING:
                return VehicleState.WAITING
        return VehicleState.DRIVING