from numpy import Infinity
import traci

class Vehicle:


    def __init__(self, vehicleId):
        self.vehicleId = vehicleId
    

    def add_to_route(self, routeId):
        traci.vehicle.add(self.vehicleId, routeId)
        traci.vehicle.setImperfection(self.vehicleId, 0)
        traci.vehicle.setAccel(self.vehicleId, 99999)
        traci.vehicle.setDecel(self.vehicleId, 99999)