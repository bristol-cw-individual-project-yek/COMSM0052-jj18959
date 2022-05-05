import unittest
from src.arbiter.arbiter import Arbiter
from src.vehicle.policy.policy import VehiclePolicy
from src.vehicle.vehicle_state import VehicleState
from src.vehicle.vehicle import Vehicle
import sumolib
from src.arbiter.arbiter import ArbiterManager
from src.arbiter.arbiter_fcfs_policy import ArbiterFCFSPolicy


class TestArbiterFCFSPolicy(unittest.TestCase):

    def test_fcfs_1(self):
        vehicles = []
        positions = [(9, 10), (0, 10), (12, 10)]
        junction = sumolib.net.node.Node("junction", "junction", (10, 10), [])
        arbiter_manager = ArbiterManager()
        arbiter_policy = ArbiterFCFSPolicy("junction")
        arbiter = Arbiter(arbiter_policy)
        arbiter_manager.assign_arbiter_to_junction("junction", arbiter)
        for i in range(3):
            vehicle = Vehicle(str(i))
            vehicle.isActive = True
            vehicle.set_conflict_resolution_policy(VehiclePolicy(vehicle))
            vehicle.nextJunction = junction
            vehicle.currentPosition = positions[i]
            vehicle.currentRoute = [""]
            vehicles.append(vehicle)
        conflicts = [
            {
                "visible"       : [vehicles[1], vehicles[2]],
                "same_junction" : [vehicles[1], vehicles[2]],
                "same_lane"     : [vehicles[1]]
            },
            {
                "visible"       : [vehicles[0], vehicles[2]],
                "same_junction" : [vehicles[0], vehicles[2]],
                "same_lane"     : [vehicles[0]]
            },
            {
                "visible"       : [vehicles[0], vehicles[1]],
                "same_junction" : [vehicles[0], vehicles[1]],
                "same_lane"     : []
            },
        ]
        expected_results = [VehicleState.CROSSING,
                            VehicleState.WAITING,
                            VehicleState.WAITING]
        for i in range(len(vehicles)):
            state = vehicles[i].conflictResolutionPolicy._decide_state(conflicts[i])
            self.assertEqual(state, expected_results[i])
        

if __name__ == "__main__":
    unittest.main()