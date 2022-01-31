class ConflictDetectionAlgorithm:
    MANHATTAN_DISTANCE_LIMIT = 10

    def get_manhattan_distance(self, pos1:tuple, pos2:tuple):
        x_distance = abs(pos1[0] - pos2[0])
        y_distance = abs(pos1[1] - pos2[1])
        manhattan_distance = x_distance + y_distance
        return manhattan_distance

    def detect_conflicts(self, vehicle, vehicles:dict):
        visible_vehicles = list(vehicles.keys())    # TODO: change this
        result = []

        for vId in visible_vehicles:
            if vId != vehicle.vehicleId:
                other_vehicle = vehicles[vId]
                manhattan_distance = self.get_manhattan_distance(other_vehicle.currentPosition, vehicle.currentPosition)
                if manhattan_distance <= self.MANHATTAN_DISTANCE_LIMIT:
                    result.append(other_vehicle)
        
        return result
