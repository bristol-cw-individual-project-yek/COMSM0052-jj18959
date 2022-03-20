from numpy import Infinity
from src.vehicle.vehicle_conflict_detection import ConflictDetection
from src.vehicle.vehicle_state import VehicleState
from src.vehicle.policy.policy import Policy
from src.vehicle.policy.custom_policy import CustomPolicy
import src.vehicle.grid as grid
import traci
import math

class Vehicle:

    def __init__(self, vehicleId, vehicleType="DEFAULT_VEHTYPE"):
        self.currentState:VehicleState = VehicleState.DRIVING
        self.vehicleId = vehicleId
        self.currentRoute = []
        self.currentRouteIndex = -1
        self.currentPosition = (Infinity, Infinity)
        self.currentGridPosition = (Infinity, Infinity)
        self.conflictDetectionAlgorithm = ConflictDetection()
        self.conflictResolutionPolicy = Policy()
        self.nextJunction = None
        self.visibilityAngle = 60   # in degrees
        self.vehicleType = vehicleType
        self.speed = 1
        self.priority = -1
        self.timeSpentWaiting = 0
    

    def set_vehicle_type(self, vehicle_type):
        self.vehicleType = vehicle_type
        traci.vehicle.setType(self.vehicleId, self.vehicleType)
    

    def set_speed(self, speed):
        self.speed = speed
        print("Speed of ", self.vehicleId, ": ", self.speed)
    

    def set_conflict_resolution_policy(self, policy:Policy):
        self.conflictResolutionPolicy = policy
    

    def set_priority(self, priority:int):
        self.priority = priority
        print("Priority of ", self.vehicleId, ": ", self.priority)
    

    def add_to_route(self, routeId, network):
        traci.vehicle.add(self.vehicleId, routeId, typeID=self.vehicleType)
        self.currentRoute = list(traci.route.getEdges(routeId))
        self.nextJunction = self.get_next_junction(network)
        #print(self.currentRoute)
        #print(str(traci.junction.getIDList()))
        #print(str(traci.vehicle.getLaneID(self.vehicleId)))

        # Set a constant speed
        # TODO: Change this
        traci.vehicle.setSpeed(self.vehicleId, self.speed)

        # Disregard all checks regarding safe speed, maximum acceleration/deceleration, right of way at intersections and red lights
        traci.vehicle.setSpeedMode(self.vehicleId, 32)
        traci.vehicle.setImperfection(self.vehicleId, 0)
        traci.vehicle.setAccel(self.vehicleId, 99999)
        traci.vehicle.setDecel(self.vehicleId, 99999)


    def update(self, vehicles:dict, network):
        self.currentRouteIndex = traci.vehicle.getRouteIndex(self.vehicleId)
        if self.currentRouteIndex < 0:
            self.currentRouteIndex = 0
        self.nextJunction = self.get_next_junction(network)
        self.currentPosition = traci.vehicle.getPosition(self.vehicleId)
        self.currentGridPosition = grid.position_to_grid_square(self.currentPosition)
        conflicting_vehicles = self.conflictDetectionAlgorithm.detect_other_vehicles(self, vehicles)
        self.currentState = self.conflictResolutionPolicy.decide_state(self, conflicting_vehicles)
        message:str = "Position of " + self.vehicleId + ": " + str(self.currentPosition) + "\n"
        message += "Grid position of " + self.vehicleId + ": " + str(self.currentGridPosition)
        #print(message)
        #print("Vehicles that conflict with " + self.vehicleId + ": " + str(conflicting_vehicles))
        self.actBasedOnState()
        if self.currentState == VehicleState.WAITING:
            self.timeSpentWaiting += 1
    

    def actBasedOnState(self):
        if self.currentState == VehicleState.DRIVING or self.currentState == VehicleState.CROSSING:
            traci.vehicle.setSpeed(self.vehicleId, self.speed)
        elif self.currentState == VehicleState.WAITING:
            traci.vehicle.setSpeed(self.vehicleId, 0)
        else:
            traci.vehicle.setSpeed(self.vehicleId, self.speed)
    

    def get_next_junction(self, network):
        current_edge = self.currentRoute[self.currentRouteIndex]
        next_junction = network.net.getEdge(current_edge).getToNode()
        return next_junction
    

    def get_distance_to_junction(self, junction=None):
        if junction:
            junction_pos = junction.getCoord()
        else:
            junction_pos = self.get_next_junction_pos()
        return Vehicle.get_distance(self.currentPosition, junction_pos)
    

    def get_distance_to_vehicle(self, vehicle):
        other_vehicle_pos = vehicle.currentPosition
        return Vehicle.get_distance(self.currentPosition, other_vehicle_pos)
    

    def get_next_junction_pos(self):
        return self.nextJunction.getCoord()
    

    def get_distance(vector1:tuple, vector2:tuple):
        distance_x = abs(vector1[0] - vector2[0])
        distance_y = abs(vector1[1] - vector2[1])
        return (distance_x ** 2 + distance_y ** 2) ** 0.5
    

    def get_current_edge(self):
        return self.currentRoute[self.currentRouteIndex]


    def get_direction_to_vehicle(self, other_vehicle):
        diff_x = other_vehicle.currentPosition[0] - self.currentPosition[0]
        diff_y = other_vehicle.currentPosition[1] - self.currentPosition[1]
        return math.degrees(math.atan2(diff_y, diff_x)) + 90
    

    def get_data_as_dict(self, include_metadata=False, include_info=True):
        if self.currentState:
            stateStr = self.currentState.name
        else:
            stateStr = "n/a"
        result = {
            "id"            : self.vehicleId
        }
        if include_metadata:
            result["type"]      = self.vehicleType
            result["policy"]    = type(self.conflictResolutionPolicy).__name__  # TODO: Figure out how to handle custom policies
            if (result["policy"] == "CustomPolicy"):
                policy:CustomPolicy = self.conflictResolutionPolicy
                result["policy_path"] = policy.module_path
        if include_info:
            result.update({
                "state"                 : stateStr,
                "position"              : self.currentPosition,
                "route"                 : self.currentRoute,
                "lane"                  : self.currentRoute[self.currentRouteIndex],
                "next_junction"         : self.nextJunction.getID(),
                "current_speed"         : self.speed,
                "priority"              : self.priority,
                "time_spent_waiting"    : self.timeSpentWaiting
            })
        return result