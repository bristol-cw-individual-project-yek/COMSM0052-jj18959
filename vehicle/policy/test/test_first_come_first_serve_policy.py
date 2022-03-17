import unittest
from vehicle.policy.first_come_first_serve_policy import FirstComeFirstServePolicy
from vehicle.vehicle_state import VehicleState
from vehicle.vehicle import Vehicle
from sumolib.net.node import Node

class TestFirstComeFirstServePolicy(unittest.TestCase):

    def test_fcfs(self):
        vehicles = []
        positions = [(0, 10), (9, 10), (12, 10)]
        junction = Node("junction", "junction", (10, 10), [])
        for i in range(3):
            vehicle = Vehicle(str(i))
            vehicle.set_conflict_resolution_policy(FirstComeFirstServePolicy())
            vehicle.nextJunction = junction
            vehicle.currentPosition = positions[i]
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
        expected_results = [VehicleState.WAITING, VehicleState.CROSSING, VehicleState.WAITING]
        for i in range(len(vehicles)):
            self.assertEqual(vehicle.conflictResolutionPolicy.decide_state(vehicle, conflicts[i]), expected_results[i])
        

if __name__ == "__main__":
    unittest.main()