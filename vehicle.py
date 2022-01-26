import traci


class Vehicle:

    def __init__(self, vehicleId):
        self.vehicleId = vehicleId
    
    
    def addToRoute(self, routeId):
        traci.vehicle.add(self.vehicleId, routeId)
        pass