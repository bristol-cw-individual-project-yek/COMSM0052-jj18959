from src.arbiter.arbiter_fcfs_policy import ArbiterFCFSPolicy
from src.vehicle.vehicle import Vehicle

class Arbiter_FCFS_SVO_Policy(ArbiterFCFSPolicy):

    def can_swap(self, v_i: Vehicle, v_j: Vehicle) -> bool:
        t_i = self.reserved_times[v_i]
        t_j = self.get_arrival_time(t_i, v_j)

        t_j_new = t_i
        t_i_new = self.get_arrival_time(t_j_new, v_i)
        
        u_j_old = v_j.get_svo_utility_one_to_one(v_i, t_j, t_i)
        u_j_new = v_j.get_svo_utility_one_to_one(v_i, t_j_new, t_i_new)

        u_i_old = v_i.get_svo_utility_one_to_one(v_j, t_i, t_j)
        u_i_new = v_i.get_svo_utility_one_to_one(v_j, t_i_new, t_j_new)

        if (u_j_new > u_j_old and u_i_new > u_i_old):
            return True
        else:
            return False