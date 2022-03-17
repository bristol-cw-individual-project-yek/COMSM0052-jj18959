import unittest
import os
import sys

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

from vehicle.vehicle_conflict_detection import ConflictDetection

class TestVehicleConflictDetection(unittest.TestCase):

    def test_get_manhattan_distance(self):
        alg = ConflictDetection()
        self.assertEqual(alg.get_manhattan_distance((0,0), (0,0)), 0)
        self.assertEqual(alg.get_manhattan_distance((0,1), (1,0)), 2)
        self.assertEqual(alg.get_manhattan_distance((0,-1), (-1,0)), alg.get_manhattan_distance((0,1), (1,0)))
        self.assertEqual(alg.get_manhattan_distance((-50, 0), (50, 0)), 100)

if __name__ == "__main__":
    unittest.main()