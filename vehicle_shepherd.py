from vehicle import Vehicle
import traci

class VehicleShepherd:

    def __init__(self):
        self.vehicles = {}
    
    def add_vehicles(self, vehicleIds_to_routes:dict):
        for vId in vehicleIds_to_routes:
            vehicle:Vehicle = Vehicle(vId)
            vehicle.add_to_route(vehicleIds_to_routes[vId])
            self.vehicles[vId] = vehicle
    
    def update_vehicles(self):
        vIds_to_be_removed = []

        # Update all active vehicles
        for vId in self.vehicles:
            try:
                self.vehicles[vId].update()
            except traci.exceptions.TraCIException as e:
                print(e)
                vIds_to_be_removed.append(vId)
        # Stop tracking any vehicles that no longer exist
        for vId in vIds_to_be_removed:
            self.vehicles.pop(vId)