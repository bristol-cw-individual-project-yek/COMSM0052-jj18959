from src.arbiter.arbiter_fcfs_policy import ArbiterFCFSPolicy
from src.vehicle.vehicle import Vehicle

class ArbiterPriorityPolicy(ArbiterFCFSPolicy):

    def can_swap(self, v_j: Vehicle, v_i: Vehicle) -> bool:
        if v_j.priority > v_i.priority:
            return True
        else:
            return False