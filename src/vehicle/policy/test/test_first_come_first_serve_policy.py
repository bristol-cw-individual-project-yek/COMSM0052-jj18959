import unittest
from src.vehicle.policy.first_come_first_serve_policy import FirstComeFirstServePolicy
from src.vehicle.vehicle_state import VehicleState
from src.vehicle.vehicle import Vehicle
from sumolib.net.node import Node
import os
import sys


class TestFirstComeFirstServePolicy(unittest.TestCase):

    def test_fcfs_1(self):
        vehicles = []
        positions = [(0, 10), (9, 10), (12, 10)]
        junction = Node("junction", "junction", (10, 10), [])
        for i in range(3):
            vehicle = Vehicle(str(i))
            vehicle.isActive = True
            vehicle.set_conflict_resolution_policy(FirstComeFirstServePolicy(vehicle))
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
        expected_results = [VehicleState.WAITING,
                            VehicleState.CROSSING,
                            VehicleState.WAITING]
        for i in range(len(vehicles)):
            state = vehicles[i].conflictResolutionPolicy.decide_state(vehicle, conflicts[i])
            self.assertEqual(state, expected_results[i])
        

if __name__ == "__main__":
    unittest.main()