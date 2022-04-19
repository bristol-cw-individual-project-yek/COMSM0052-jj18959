from fcfs_centralized import FCFS_CentralizedPolicy
from src.vehicle.vehicle import Vehicle

class FCFS_SVO_Policy(FCFS_CentralizedPolicy):

    def can_swap(self, vehicle: Vehicle, other_vehicle: Vehicle) -> bool:
        reserved_time_old = type(self).reserved_times[vehicle]
        other_reserved_time_old = type(self).reserved_times[other_vehicle]

        arrival_time_new = self.get_arrival_time(other_reserved_time_old, vehicle)
        #other_arrival_time_new = self.get_arrival_time(reserved_time_old, other_vehicle)
        print(f"Old reserved time:{reserved_time_old}, other old reserved time: {other_reserved_time_old}, new arrival: {arrival_time_new}")

        veh_svo_utility_old = vehicle.get_social_value_orientation_utility_one_to_one(other_vehicle, reserved_time_old, other_reserved_time_old)
        veh_svo_utility_new = vehicle.get_social_value_orientation_utility_one_to_one(other_vehicle, other_reserved_time_old, arrival_time_new)

        other_svo_utility_old = other_vehicle.get_social_value_orientation_utility_one_to_one(vehicle, other_reserved_time_old, reserved_time_old)
        other_svo_utility_new = other_vehicle.get_social_value_orientation_utility_one_to_one(vehicle, arrival_time_new, other_reserved_time_old)

        print(f"Comparing {veh_svo_utility_old} with {veh_svo_utility_new} and {other_svo_utility_old} with {other_svo_utility_new}")
        if veh_svo_utility_new > veh_svo_utility_old and other_svo_utility_new > other_svo_utility_old:
            print("Can swap")
            return True
        else:
            return False