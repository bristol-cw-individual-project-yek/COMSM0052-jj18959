class ConflictDetectionAlgorithm:
    MANHATTAN_DISTANCE_LIMIT = 10

    def detect_conflicts(self, vehicle, vehicles:dict):
        visible_vehicles = list(vehicles.keys())    # TODO: change this
        result = []

        for vId in visible_vehicles:
            if vId != vehicle.vehicleId:
                other_vehicle = vehicles[vId]
                x_distance = abs(other_vehicle.currentPosition[0] - vehicle.currentPosition[0])
                y_distance = abs(other_vehicle.currentPosition[1] - vehicle.currentPosition[1])
                manhattan_distance = x_distance + y_distance
                if manhattan_distance <= self.MANHATTAN_DISTANCE_LIMIT:
                    result.append(other_vehicle)
        
        return result
