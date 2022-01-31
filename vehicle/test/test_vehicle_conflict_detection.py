import unittest
from vehicle.vehicle_conflict_detection import ConflictDetectionAlgorithm

class TestVehicleConflictDetection(unittest.TestCase):

    def test_get_manhattan_distance(self):
        alg = ConflictDetectionAlgorithm()
        self.assertEqual(alg.get_manhattan_distance((0,0), (0,0)), 0)
        self.assertEqual(alg.get_manhattan_distance((0,1), (1,0)), 2)
        self.assertEqual(alg.get_manhattan_distance((0,-1), (-1,0)), alg.get_manhattan_distance((0,1), (1,0)))
        self.assertEqual(alg.get_manhattan_distance((-50, 0), (50, 0)), 100)

if __name__ == "__main__":
    unittest.main()