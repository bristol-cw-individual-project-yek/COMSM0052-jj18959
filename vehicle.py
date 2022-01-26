from numpy import Infinity
import traci

class Vehicle:

    def __init__(self, vehicleId):
        self.vehicleId = vehicleId
        self.currentRoute = ""
        self.currentRouteIndex = -1
        self.currentPosition = (Infinity, Infinity)
    

    def add_to_route(self, routeId):
        traci.vehicle.add(self.vehicleId, routeId)
        self.currentRoute = routeId

        # TODO: Change this
        traci.vehicle.setSpeed(self.vehicleId, 1)

        # Disregard all checks regarding safe speed, maximum acceleration/deceleration, right of way at intersections and red lights
        traci.vehicle.setSpeedMode(self.vehicleId, 32)
        traci.vehicle.setImperfection(self.vehicleId, 0)
        traci.vehicle.setAccel(self.vehicleId, 99999)
        traci.vehicle.setDecel(self.vehicleId, 99999)
    

    def update(self):
        self.currentRouteIndex = traci.vehicle.getRouteIndex(self.vehicleId)
        self.currentPosition = traci.vehicle.getPosition(self.vehicleId)
        message:str = "Position of " + self.vehicleId + ": " + str(self.currentPosition)
        print(message)