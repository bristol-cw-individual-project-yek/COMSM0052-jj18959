import unittest
from vehicle.vehicle import Vehicle

class TestVehicle(unittest.TestCase):

    def test_get_distance_to_vehicle(self):
        vehicle1 = Vehicle("1")
        vehicle2 = Vehicle("2")
        vehicle1.currentPosition = (0, 0)
        vehicle2.currentPosition = (3, 4)
        self.assertEqual(vehicle1.get_distance_to_vehicle(vehicle2), vehicle2.get_distance_to_vehicle(vehicle1))
        self.assertEqual(vehicle1.get_distance_to_vehicle(vehicle2), 5)

    
    def test_get_distance_to_junction(self):
        vehicle1 = Vehicle("1")
        

if __name__ == "__main__":
    unittest.main()