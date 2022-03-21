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
    

    def get_vehicle_nearest_to_junction(self, junction, edge, vehicle_list:list):
        vehicles_on_edge = self.get_vehicles_on_edge(edge, vehicle_list)
        if len(vehicles_on_edge) > 0:
            other_vehicle = None
            for v in vehicles_on_edge:
                if not other_vehicle or v.get_distance_to_junction(junction) < other_vehicle.get_distance_to_junction(junction):
                    other_vehicle = v
            return other_vehicle
        else:
            return None


    # Detect other surrounding vehicles, including:
    # - Vehicles in the same lane
    # - Vehicles approaching the same junction
    def detect_other_vehicles(self, vehicle, vehicles:dict, filters:list=None) -> dict:
        visible_vehicles = list(filter(lambda v : v.isActive, list(vehicles.values())))
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
        
        # Only checks vehicles closest to junction, excluding the lane of the current vehicle
        if not filters or "same_junction" in filters:
            next_junction = vehicle.nextJunction
            incoming_edges = next_junction.getIncoming()
            vehicles_approaching_same_junction = []
            currentRoute = vehicle.currentRoute[vehicle.currentRouteIndex]
            for edge in incoming_edges:
                edge_id = edge.getID()
                if edge_id != currentRoute:
                    other_vehicle = self.get_vehicle_nearest_to_junction(next_junction, edge, visible_vehicles)
                    if other_vehicle:
                        vehicles_approaching_same_junction.append(other_vehicle)
            result["same_junction"] = vehicles_approaching_same_junction
        
        return result
