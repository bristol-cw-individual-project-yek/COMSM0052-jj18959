from fcfs_centralized import FCFS_CentralizedPolicy
from src.vehicle.vehicle import Vehicle

class FCFS_SVO_Policy(FCFS_CentralizedPolicy):

    def can_swap(self, vehicle: Vehicle, other_vehicle: Vehicle) -> bool:
        reserved_time = type(self).reserved_times[vehicle]
        other_reserved_time = type(self).reserved_times[vehicle]
        veh_svo_utility_old = vehicle.get_social_value_orientation_utility_one_to_one(other_vehicle, reserved_time, other_reserved_time)
        veh_svo_utility_new = vehicle.get_social_value_orientation_utility_one_to_one(other_vehicle, other_reserved_time, reserved_time)
        other_svo_utility_old = other_vehicle.get_social_value_orientation_utility_one_to_one(vehicle, other_reserved_time, reserved_time)
        other_svo_utility_new = other_vehicle.get_social_value_orientation_utility_one_to_one(vehicle, reserved_time, other_reserved_time)
        if veh_svo_utility_new > veh_svo_utility_old and other_svo_utility_new > other_svo_utility_old:
            return True
        else:
            return False