import sumolib.net as net
from typing import Union

class ConflictDetection:
    MANHATTAN_DISTANCE_LIMIT = 2

    def get_manhattan_distance(self, pos1:tuple, pos2:tuple):
        x_distance = abs(pos1[0] - pos2[0])
        y_distance = abs(pos1[1] - pos2[1])
        manhattan_distance = x_distance + y_distance
        return manhattan_distance
    

    def get_vehicles_on_edge(self, edge:Union[net.edge.Edge, str], vehicle_list:list):
        valid_vehicles = []
        if type(edge) is net.edge.Edge:
            edge_id:str = edge.getID()
        elif type(edge) is str:
            edge_id:str = edge
        else:
            edge_id = None
        for vehicle in vehicle_list:
            if vehicle.currentRoute[vehicle.currentRouteIndex] == edge_id:
                valid_vehicles.append(vehicle)
        return valid_vehicles


    # Detect other surrounding vehicles, including:
    # - Vehicles in the same lane
    # - Vehicles approaching the same junction
    def detect_other_vehicles(self, vehicle, vehicles:dict, filters:list=None) -> dict:
        visible_vehicles = list(vehicles.values())    # TODO: change this
        result = {}
        if not filters or "visible" in filters:
            result["visible"] = visible_vehicles
            try:
                result["visible"].remove(vehicle)
                pass
            except:
                pass
        if not filters or "same_lane" in filters:
            result["same_lane"] = self.get_vehicles_on_edge(vehicle.get_current_edge(), visible_vehicles)
            try:
                result["same_lane"].remove(vehicle)
                pass
            except:
                pass
        
        if not filters or "same_junction" in filters:
            next_junction = vehicle.nextJunction
            incoming_edges = next_junction.getIncoming()
            vehicles_approaching_same_junction = []
            for edge in incoming_edges:
                vehicles_approaching_same_junction.extend(self.get_vehicles_on_edge(edge, visible_vehicles))
            result["same_junction"] = vehicles_approaching_same_junction
        
        return result
