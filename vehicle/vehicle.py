from numpy import Infinity
from vehicle.vehicle_conflict_detection import ConflictDetectionAlgorithm
from vehicle.vehicle_state import VehicleState
from vehicle.vehicle_policy import VehiclePolicy
import vehicle.grid as grid
import traci

class Vehicle:

    def __init__(self, vehicleId):
        self.currentState = VehicleState.DRIVING
        self.vehicleId = vehicleId
        self.currentRoute = []
        self.currentRouteIndex = -1
        self.currentPosition = (Infinity, Infinity)
        self.currentGridPosition = (Infinity, Infinity)
        self.conflictDetectionAlgorithm = ConflictDetectionAlgorithm()
        self.conflictResolutionPolicy = VehiclePolicy()
    

    def set_conflict_resolution_policy(self, policy:VehiclePolicy):
        self.conflictResolutionPolicy = policy
    

    def add_to_route(self, routeId):
        traci.vehicle.add(self.vehicleId, routeId)
        self.currentRoute = list(traci.route.getEdges(routeId))
        #print(self.currentRoute)
        #print(str(traci.junction.getIDList()))
        #print(str(traci.vehicle.getLaneID(self.vehicleId)))

        # Set a constant speed
        # TODO: Change this
        traci.vehicle.setSpeed(self.vehicleId, 1)

        # Disregard all checks regarding safe speed, maximum acceleration/deceleration, right of way at intersections and red lights
        traci.vehicle.setSpeedMode(self.vehicleId, 32)
        traci.vehicle.setImperfection(self.vehicleId, 0)
        traci.vehicle.setAccel(self.vehicleId, 99999)
        traci.vehicle.setDecel(self.vehicleId, 99999)


    def update(self, vehicles:dict):
        conflicting_vehicles = self.conflictDetectionAlgorithm.detect_conflicts(self, vehicles)
        self.currentState = self.conflictResolutionPolicy.decide_state(self, conflicting_vehicles)
        self.currentRouteIndex = traci.vehicle.getRouteIndex(self.vehicleId)
        self.currentPosition = traci.vehicle.getPosition(self.vehicleId)
        self.currentGridPosition = grid.position_to_grid_square(self.currentPosition)
        message:str = "Position of " + self.vehicleId + ": " + str(self.currentPosition) + "\n"
        message += "Grid position of " + self.vehicleId + ": " + str(self.currentGridPosition)
        #print(message)
        #print("Vehicles that conflict with " + self.vehicleId + ": " + str(conflicting_vehicles))
        self.actBasedOnState()
    

    def actBasedOnState(self):
        if self.currentState == VehicleState.DRIVING:
            traci.vehicle.setSpeed(self.vehicleId, 1)
        elif self.currentState == VehicleState.WAITING:
            traci.vehicle.setSpeed(self.vehicleId, 0)