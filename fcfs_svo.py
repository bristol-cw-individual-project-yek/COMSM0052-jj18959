from fcfs_centralized import FCFS_CentralizedPolicy
from src.vehicle.vehicle import Vehicle

class FCFS_SVO_Policy(FCFS_CentralizedPolicy):

    def can_swap(self, vehicle: Vehicle, other_vehicle: Vehicle) -> bool:
        if vehicle.get_social_value_orientation_utility_one_to_one(other_vehicle) > other_vehicle.get_social_value_orientation_utility_one_to_one(vehicle):
            return True
        else:
            return False