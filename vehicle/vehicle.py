from numpy import Infinity
from vehicle.vehicle_conflict_detection import ConflictDetection
from vehicle.vehicle_state import VehicleState
from vehicle.policy.policy import Policy
import vehicle.grid as grid
import traci
from network.network import Network

class Vehicle:

    def __init__(self, vehicleId):
        self.currentState = VehicleState.DRIVING
        self.vehicleId = vehicleId
        self.currentRoute = []
        self.currentRouteIndex = -1
        self.currentPosition = (Infinity, Infinity)
        self.currentGridPosition = (Infinity, Infinity)
        self.conflictDetectionAlgorithm = ConflictDetection()
        self.conflictResolutionPolicy = Policy()
        self.nextJunction = None
    

    def set_conflict_resolution_policy(self, policy:Policy):
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


    def update(self, vehicles:dict, network:Network):
        self.currentRouteIndex = traci.vehicle.getRouteIndex(self.vehicleId)
        if self.currentRouteIndex < 0:
            self.currentRouteIndex = 0
        self.nextJunction = self.get_next_junction(network)
        self.currentPosition = traci.vehicle.getPosition(self.vehicleId)
        self.currentGridPosition = grid.position_to_grid_square(self.currentPosition)
        conflicting_vehicles = self.conflictDetectionAlgorithm.detect_conflicts(self, vehicles)
        self.currentState = self.conflictResolutionPolicy.decide_state(self, conflicting_vehicles)
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
    

    def get_next_junction(self, network:Network):
        current_edge = self.currentRoute[self.currentRouteIndex]
        next_junction = network.net.getEdge(current_edge).getToNode()
        return next_junction
    

    def get_distance_to_junction(self):
        junction_pos = self.nextJunction.getCoord()
        return Vehicle.get_distance(self.currentPosition, junction_pos)
    

    def get_distance_to_vehicle(self, vehicle):
        other_vehicle_pos = vehicle.currentPosition
        return Vehicle.get_distance(self.currentPosition, other_vehicle_pos)
    

    def get_distance(vector1:tuple, vector2:tuple):
        distance_x = abs(vector1[0] - vector2[0])
        distance_y = abs(vector1[1] - vector2[1])
        return (distance_x ** 2 + distance_y ** 2) ** 0.5