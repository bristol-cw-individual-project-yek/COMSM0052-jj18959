import unittest
import main

class TestMain(unittest.TestCase):

    def test_run_simulation(self):
        vehicleIdsToRoutes = {}
        for i in range(10):
            vehicleIdsToRoutes["testVehicle"] = "r" + str(i)
            main.run_simulation(vehicleIdsToRoutes)