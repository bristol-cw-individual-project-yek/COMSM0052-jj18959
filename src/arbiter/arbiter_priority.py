from src.arbiter.arbiter_fcfs_policy import ArbiterFCFSPolicy
from src.vehicle.vehicle import Vehicle

class ArbiterPriorityPolicy(ArbiterFCFSPolicy):

    def can_swap(self, v_i: Vehicle, v_j: Vehicle) -> bool:
        if v_i.priority > v_j.priority:
            return True
        else:
            return False