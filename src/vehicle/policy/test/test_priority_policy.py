import unittest
from src.vehicle.policy.priority_policy import PriorityPolicy
from src.vehicle.vehicle_state import VehicleState
from src.vehicle.vehicle import Vehicle
from sumolib.net.node import Node
import os
import sys


class TestPriorityPolicy(unittest.TestCase):

    def test_priority(self):
        vehicles = []
        positions = [(0, 10), (9, 10), (12, 10)]
        priorities = [2, 2, 1]
        junction = Node("junction", "junction", (10, 10), [])
        for i in range(3):
            vehicle = Vehicle(str(i))
            vehicle.isActive = True
            vehicle.set_conflict_resolution_policy(PriorityPolicy())
            vehicle.nextJunction = junction
            vehicle.currentPosition = positions[i]
            vehicle.priority = priorities[i]
            vehicle.currentState = VehicleState.DRIVING
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
        expected_results = [VehicleState.WAITING, VehicleState.WAITING, VehicleState.CROSSING]
        
        self.assertEqual(vehicle.conflictResolutionPolicy.decide_state(vehicles[0], conflicts[0]), expected_results[0])
        self.assertEqual(vehicle.conflictResolutionPolicy.decide_state(vehicles[1], conflicts[1]), expected_results[1])
        self.assertEqual(vehicle.conflictResolutionPolicy.decide_state(vehicles[2], conflicts[2]), expected_results[2])
        

if __name__ == "__main__":
    unittest.main()