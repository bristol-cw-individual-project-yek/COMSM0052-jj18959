from network.network import Network

class ConflictDetection:
    MANHATTAN_DISTANCE_LIMIT = 2

    def get_manhattan_distance(self, pos1:tuple, pos2:tuple):
        x_distance = abs(pos1[0] - pos2[0])
        y_distance = abs(pos1[1] - pos2[1])
        manhattan_distance = x_distance + y_distance
        return manhattan_distance
    

    def get_next_junction(self, vehicle, network:Network):
        current_edge = vehicle.currentRoute[vehicle.currentRouteIndex]
        next_junction = network.net.getEdge(current_edge).getToNode()
        return next_junction
    

    def get_vehicles_on_edge(self, edge, vehicle_list:list):
        valid_vehicles = []
        edge_id = edge.getID()
        for vehicle in vehicle_list:
            if vehicle.currentRoute[vehicle.currentRouteIndex] == edge_id:
                valid_vehicles.append(vehicle)
        return valid_vehicles


    def detect_conflicts(self, vehicle, vehicles:dict, network:Network):
        visible_vehicles = list(vehicles.values())    # TODO: change this
        result = []

        next_junction = self.get_next_junction(vehicle, network)
        incoming_edges = next_junction.getIncoming()
        incoming_vehicles = []
        for edge in incoming_edges:
            incoming_vehicles.extend(self.get_vehicles_on_edge(edge, visible_vehicles))

        for other_vehicle in incoming_vehicles:
            if other_vehicle.vehicleId != vehicle.vehicleId:
                manhattan_distance = self.get_manhattan_distance(other_vehicle.currentGridPosition, vehicle.currentGridPosition)
                if manhattan_distance <= self.MANHATTAN_DISTANCE_LIMIT:
                    result.append(other_vehicle)
        
        return result
