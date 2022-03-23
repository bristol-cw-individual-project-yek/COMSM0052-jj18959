import unittest
from src.vehicle.vehicle import Vehicle
import math


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
    

    def test_get_vehicle_reward_no_waiting(self):
        vehicle = Vehicle("a")
        vehicle.timeSpentWaiting = 0
        self.assertEqual(vehicle.get_reward(), 1)
    

    def test_get_vehicle_reward_waiting(self):
        vehicle = Vehicle("a")
        vehicle.timeSpentWaiting = 1
        self.assertEqual(vehicle.get_reward(), 0.5)
        vehicle.timeSpentWaiting = 2
        self.assertAlmostEqual(vehicle.get_reward(), 0.333, 3)
        vehicle.timeSpentWaiting = 10
        self.assertAlmostEqual(vehicle.get_reward(), 0.091, 3)
    

    def test_get_vehicle_reward_error(self):
        vehicle = Vehicle("a")
        vehicle.timeSpentWaiting = -1
        try:
            reward = vehicle.get_reward()
            self.fail("Vehicle.get_reward() failed to throw ZeroDivisionError where expected")
        except ZeroDivisionError:
            pass
    

    def test_get_social_value_orientation_utility_one_to_one_egotistic_no_wait(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = 0
        vehicle2.svo_angle = 0
        vehicle1.timeSpentWaiting = 0
        vehicle2.timeSpentWaiting = 0
        self.assertEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 1)
        self.assertEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 1)


    def test_get_social_value_orientation_utility_one_to_one_egotistic_wait(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = 0
        vehicle2.svo_angle = 0
        vehicle1.timeSpentWaiting = 10
        vehicle2.timeSpentWaiting = 0
        self.assertAlmostEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 0.091, 3)
        self.assertEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 1)


    def test_get_social_value_orientation_utility_one_to_one_prosocial_no_wait(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = math.pi/4
        vehicle2.svo_angle = math.pi/4
        vehicle1.timeSpentWaiting = 0
        vehicle2.timeSpentWaiting = 0
        self.assertAlmostEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 1.414, 3)
        self.assertAlmostEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 1.414, 3)
    

    def test_get_social_value_orientation_utility_one_to_one_prosocial_wait(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = math.pi/4
        vehicle2.svo_angle = math.pi/4
        vehicle1.timeSpentWaiting = 10
        vehicle2.timeSpentWaiting = 0
        self.assertAlmostEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 0.771, 3)
        self.assertAlmostEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 0.771, 3)
    

    def test_get_social_value_orientation_utility_one_to_one_mixed_no_wait(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = 0          # Egotistic
        vehicle2.svo_angle = math.pi/4  # Prosocial
        vehicle1.timeSpentWaiting = 0
        vehicle2.timeSpentWaiting = 0
        self.assertEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 1)
        self.assertAlmostEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 1.414, 3)
    

    def test_get_social_value_orientation_utility_one_to_one_mixed_wait_1(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = 0          # Egotistic
        vehicle2.svo_angle = math.pi/4  # Prosocial
        vehicle1.timeSpentWaiting = 10
        vehicle2.timeSpentWaiting = 0
        self.assertAlmostEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 0.091, 3)
        self.assertAlmostEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 0.771, 3)
    

    def test_get_social_value_orientation_utility_one_to_one_mixed_wait_2(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.svo_angle = 0          # Egotistic
        vehicle2.svo_angle = math.pi/4  # Prosocial
        vehicle1.timeSpentWaiting = 0
        vehicle2.timeSpentWaiting = 10
        self.assertEqual(vehicle1.get_social_value_orientation_utility_one_to_one(vehicle2), 1)
        self.assertAlmostEqual(vehicle2.get_social_value_orientation_utility_one_to_one(vehicle1), 0.771, 3)
        

if __name__ == "__main__":
    unittest.main()