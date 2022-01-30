from numpy import Infinity
from vehicle_conflict_detection import ConflictDetectionAlgorithm
import traci

class Vehicle:

    def __init__(self, vehicleId):
        self.vehicleId = vehicleId
        self.currentRoute = []
        self.currentRouteIndex = -1
        self.currentPosition = (Infinity, Infinity)
        self.conflictDetectionAlgorithm = ConflictDetectionAlgorithm()
    

    def add_to_route(self, routeId):
        traci.vehicle.add(self.vehicleId, routeId)
        self.currentRoute = list(traci.route.getEdges(routeId))
        print(self.currentRoute)
        print(str(traci.junction.getIDList()))
        print(str(traci.vehicle.getLaneID(self.vehicleId)))

        # Set a constant speed
        # TODO: Change this
        traci.vehicle.setSpeed(self.vehicleId, 1)

        # Disregard all checks regarding safe speed, maximum acceleration/deceleration, right of way at intersections and red lights
        traci.vehicle.setSpeedMode(self.vehicleId, 32)
        traci.vehicle.setImperfection(self.vehicleId, 0)
        traci.vehicle.setAccel(self.vehicleId, 99999)
        traci.vehicle.setDecel(self.vehicleId, 99999)


    def update(self, vehicles:dict):
        self.currentRouteIndex = traci.vehicle.getRouteIndex(self.vehicleId)
        self.currentPosition = traci.vehicle.getPosition(self.vehicleId)
        #message:str = "Position of " + self.vehicleId + ": " + str(self.currentPosition)
        #print(message)
        print("Vehicles that conflict with " + self.vehicleId + ": " + str(self.conflictDetectionAlgorithm.detect_conflicts(self, vehicles)))