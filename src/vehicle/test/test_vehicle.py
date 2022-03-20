import unittest
from src.vehicle.vehicle import Vehicle
import os
import sys


class TestVehicle(unittest.TestCase):

    def test_get_distance_to_vehicle_1(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.currentPosition = (0, 0)
        vehicle2.currentPosition = (3, 4)
        self.assertEqual(vehicle1.get_distance_to_vehicle(vehicle2), vehicle2.get_distance_to_vehicle(vehicle1))
        self.assertEqual(vehicle1.get_distance_to_vehicle(vehicle2), 5)
    

    def test_get_distance_to_vehicle_2(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.currentPosition = (-1, 5)
        vehicle2.currentPosition = (6, -2)
        self.assertEqual(vehicle1.get_distance_to_vehicle(vehicle2), vehicle2.get_distance_to_vehicle(vehicle1))
        self.assertAlmostEqual(vehicle1.get_distance_to_vehicle(vehicle2), 9.9, 1)

    
    def test_get_direction_to_vehicle_1(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.currentPosition = (0, 0)
        vehicle2.currentPosition = (3, 4)
        self.assertAlmostEqual(vehicle1.get_direction_to_vehicle(vehicle2), 143.1, 1)
        self.assertAlmostEqual(vehicle2.get_direction_to_vehicle(vehicle1), -36.9, 1)
    

    def test_get_direction_to_vehicle_2(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.currentPosition = (0, 0)
        vehicle2.currentPosition = (1, 1)
        self.assertAlmostEqual(vehicle1.get_direction_to_vehicle(vehicle2), 135, 1)
        self.assertAlmostEqual(vehicle2.get_direction_to_vehicle(vehicle1), -45, 1)
    

    def test_get_direction_to_vehicle_3(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.currentPosition = (-5, 2)
        vehicle2.currentPosition = (6, 3)
        self.assertAlmostEqual(vehicle1.get_direction_to_vehicle(vehicle2), 95.2, 1)
        self.assertAlmostEqual(vehicle2.get_direction_to_vehicle(vehicle1), -84.8, 1)
        

if __name__ == "__main__":
    unittest.main()