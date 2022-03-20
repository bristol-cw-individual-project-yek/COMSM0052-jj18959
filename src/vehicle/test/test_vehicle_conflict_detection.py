import unittest
from src.vehicle.vehicle_conflict_detection import ConflictDetection
import src.vehicle.vehicle as vehicle

class TestVehicleConflictDetection(unittest.TestCase):

    def test_get_manhattan_distance(self):
        alg = ConflictDetection()
        self.assertEqual(alg.get_manhattan_distance((0,0), (0,0)), 0)
        self.assertEqual(alg.get_manhattan_distance((0,1), (1,0)), 2)
        self.assertEqual(alg.get_manhattan_distance((0,-1), (-1,0)), alg.get_manhattan_distance((0,1), (1,0)))
        self.assertEqual(alg.get_manhattan_distance((-50, 0), (50, 0)), 100)
    

    def test_detect_other_vehicles_same_lane(self):
        vehicle1 = vehicle.Vehicle("1")
        vehicle2 = vehicle.Vehicle("2")
        vehicle3 = vehicle.Vehicle("3")
        vehicle4 = vehicle.Vehicle("4")
        vehicles = {
            "1" : vehicle1,
            "2" : vehicle2,
            "3" : vehicle3,
            "4" : vehicle4
        }

        # Set up vehicles 1 and 3 to be in the same lane
        vehicle1.currentRoute = ["lane1", "lane2", "lane3"]
        vehicle2.currentRoute = ["lane4", "lane2", "lane6"]
        vehicle3.currentRoute = ["lane2", "lane1", "lane9"]
        vehicle4.currentRoute = ["lane1", "lane2", "lane3"]

        vehicle1.currentRouteIndex = 1
        vehicle2.currentRouteIndex = 0
        vehicle3.currentRouteIndex = 0
        vehicle4.currentRouteIndex = 2

        cd = ConflictDetection()
        results = cd.detect_other_vehicles(vehicle1, vehicles, filters=["same_lane"])

        self.assertEqual(len(results["same_lane"]), 1)
        self.assertEqual(results["same_lane"][0].vehicleId, "3")
    
    
    # TODO: Write test for checking conflicts on same junction


if __name__ == "__main__":
    unittest.main()