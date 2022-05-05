from src.vehicle.policy.policy import VehiclePolicy
from src.vehicle.vehicle import Vehicle
from src.vehicle.vehicle_state import VehicleState

class CustomVehiclePolicyTemplate(VehiclePolicy):

    def decide_state(self, vehicle:Vehicle, conflicting_vehicles: dict):
        return super().decide_state(vehicle, conflicting_vehicles)
    

    def is_conflicting_same_junction(self, vehicle:Vehicle, other_vehicle:Vehicle) -> bool:
        return super().is_conflicting_same_junction(vehicle, other_vehicle)
    

    def is_conflicting_same_lane(self, vehicle:Vehicle, other_vehicle:Vehicle) -> bool:
        return super().is_conflicting_same_lane(vehicle, other_vehicle)
    

    def is_conflicting_visible(self, vehicle:Vehicle, other_vehicle:Vehicle) -> bool:
        return super().is_conflicting_visible(vehicle, other_vehicle)
    

    def decide_state_no_conflicts(self, vehicle:Vehicle) -> VehicleState:
        return super().decide_state_no_conflicts(vehicle)