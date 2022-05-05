from numpy import Infinity
from src.vehicle.vehicle_conflict_detection import ConflictDetection
from src.vehicle.vehicle_state import VehicleState
from src.vehicle.policy.policy import VehiclePolicy
from src.vehicle.policy.custom_policy import CustomPolicy
import src.vehicle.grid as grid
import traci
import math
import sumolib

class Vehicle:

    def __init__(self, vehicleId, vehicleType="DEFAULT_VEHTYPE"):
        self.currentState:VehicleState = VehicleState.DRIVING
        self.vehicleId = vehicleId
        self.currentRoute = []
        self.currentRouteIndex = 0
        self.currentPosition = (Infinity, Infinity)
        self.currentGridPosition = (Infinity, Infinity)
        self.conflictDetectionAlgorithm = ConflictDetection()
        self.conflictResolutionPolicy = VehiclePolicy(self)
        self.nextJunction:sumolib.net.node.Node = None
        self.visibilityAngle = 60   # in degrees
        self.vehicleType = vehicleType
        self.speed = 1
        self.priority = -1
        self.totalTimeSpentWaiting:int = 0
        self.currentTimeSpentWaiting:int = 0
        self.svo_angle:float = 0    # Vehicles are considered egoistic by default
        self.isActive = True
        self.pastWaitTimesAtJunctions:list = []
        self.network = None
    

    def get_reward(self, reserved_time:float=None) -> float:
        """
        Get the reward of this agent, based on the total time spent waiting across the entire simulation.

        By default, the reward = -t, where t is the total time spent waiting throughout the simulation.

        If the "reserved_time" parameter is passed in, t = reserved_time - current time + total time spent waiting instead.
        """
        if (reserved_time):
            waiting_time = (reserved_time - traci.simulation.getTime()) + self.totalTimeSpentWaiting
        else:
            waiting_time = self.totalTimeSpentWaiting
        return -waiting_time


    def get_svo_utility_one_to_one(self, other_vehicle, reserved_time:float=None, other_reserved_time:float=None) -> float:
        reward:float = self.get_reward(reserved_time)
        other_reward:float = other_vehicle.get_reward(other_reserved_time)
        utility:float = (reward * math.cos(self.svo_angle)) + (other_reward * math.sin(self.svo_angle))
        return utility
    

    def get_svo_utility_group_average(self, other_vehicles:list, weights:list=None) -> float:
        if weights:
            assert(len(other_vehicles) == len(weights))
        reward:float = self.get_reward()
        other_rewards:float = 0
        for i in range(len(other_vehicles)):
            veh = other_vehicles[i]
            r = veh.get_reward()
            if weights:
                r *= weights[i]
            other_rewards += r
        if weights:
            other_rewards /= sum(weights)
        else:
            other_rewards /= len(other_vehicles)
        utility:float = (reward * math.cos(self.svo_angle)) + (other_rewards * math.sin(self.svo_angle))
        return utility
    

    def get_svo_utility_group_sum(self, other_vehicles:list, weights:list=None) -> float:
        if weights:
            assert(len(other_vehicles) == len(weights))
        reward:float = self.get_reward()
        other_rewards:float = 0
        for i in range(len(other_vehicles)):
            veh = other_vehicles[i]
            r = veh.get_reward()
            if weights:
                r *= weights[i]
            other_rewards += r
        utility:float = (reward * math.cos(self.svo_angle)) + (other_rewards * math.sin(self.svo_angle))
        return utility
    

    def set_vehicle_type(self, vehicle_type):
        self.vehicleType = vehicle_type
        traci.vehicle.setType(self.vehicleId, self.vehicleType)
    

    def set_speed(self, speed):
        self.speed = speed
        print("Speed of ", self.vehicleId, ": ", self.speed)
    

    def set_conflict_resolution_policy(self, policy:VehiclePolicy):
        self.conflictResolutionPolicy = policy
    

    def set_priority(self, priority:int):
        self.priority = priority
    

    def add_to_route(self, routeId, network):
        traci.vehicle.add(self.vehicleId, routeId, typeID=self.vehicleType)
        self.currentRoute = list(traci.route.getEdges(routeId))
        self.network = network
        self.nextJunction = self.get_next_junction()
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


    def update(self, vehicles:dict):
        self.currentRouteIndex = traci.vehicle.getRouteIndex(self.vehicleId)
        if self.currentRouteIndex < 0:
            self.currentRouteIndex = 0
        next_junction = self.get_next_junction()
        if next_junction.getID() != self.nextJunction.getID():
            self.pastWaitTimesAtJunctions.append(self.currentTimeSpentWaiting)
            self.currentTimeSpentWaiting = 0
        self.nextJunction = next_junction
        self.currentPosition = traci.vehicle.getPosition(self.vehicleId)
        self.currentGridPosition = grid.position_to_grid_square(self.currentPosition)
        conflicting_vehicles = self.conflictDetectionAlgorithm.detect_other_vehicles(self, vehicles)
        self.currentState = self.conflictResolutionPolicy._decide_state(conflicting_vehicles)
        message:str = "Position of " + self.vehicleId + ": " + str(self.currentPosition) + "\n"
        message += "Grid position of " + self.vehicleId + ": " + str(self.currentGridPosition)
        #print(message)
        #print("Vehicles that conflict with " + self.vehicleId + ": " + str(conflicting_vehicles))
        self.actBasedOnState()
        if self.currentState == VehicleState.WAITING:
            self.totalTimeSpentWaiting += 1
            if self.get_distance_to_junction() <= self.conflictResolutionPolicy.MIN_WAITING_DISTANCE_FROM_JUNCTION:
                self.currentTimeSpentWaiting += 1
    

    def actBasedOnState(self):
        if self.currentState == VehicleState.DRIVING or self.currentState == VehicleState.CROSSING:
            traci.vehicle.setSpeed(self.vehicleId, self.speed)
        elif self.currentState == VehicleState.WAITING:
            traci.vehicle.setSpeed(self.vehicleId, 0)
        else:
            traci.vehicle.setSpeed(self.vehicleId, self.speed)
    

    def get_next_junction(self) -> sumolib.net.node.Node:
        current_edge = self.currentRoute[self.currentRouteIndex]
        next_junction:sumolib.net.node.Node = self.network.net.getEdge(current_edge).getToNode()
        return next_junction
    

    def get_next_crossing_internal_length(self) -> float:
        current_edge = self.currentRoute[self.currentRouteIndex]
        try:
            next_edge = self.currentRoute[self.currentRouteIndex + 1]
            return self.network.getConnectionLength(current_edge, next_edge)
        except IndexError:
            return 1
    

    def get_time_to_cross_next_junction(self) -> float:
        distance_to_next_lane = self.get_next_crossing_internal_length()
        speed = self.speed
        return distance_to_next_lane / speed
    

    def get_time_to_next_lane_at_full_speed(self):
        """
        Returns the estimated time it would take for this vehicle to reach the next lane at full speed.
        """
        distance_to_next_lane = self.get_distance_to_junction() + (self.get_next_crossing_internal_length() / 2)
        speed = self.speed
        return distance_to_next_lane / speed
    

    def get_distance_to_junction(self, junction=None) -> float:
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
    

    def get_distance(vector1:tuple, vector2:tuple) -> float:
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
                "time_spent_waiting"    : self.totalTimeSpentWaiting
            })
        return result