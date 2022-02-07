from vehicle.vehicle import Vehicle
import random
import traci

class VehicleShepherd:

    def __init__(self):
        self.vehicles = {}
    

    # TODO: Write test for this
    def add_vehicles(self, vehicleGroups:dict, routeIds: list):
        for group in vehicleGroups:
            for i in range(vehicleGroups[group]["num"]):
                vId = group + "-" + str(i)
                vehicle:Vehicle = Vehicle(vId)

                policyType = vehicleGroups[group]["policy-type"]
                if policyType == "default":
                    pass

                routeId = routeIds[random.randint(0, len(routeIds) - 1)]
                vehicle.add_to_route(routeId)
                self.vehicles[vId] = vehicle
                routeIds.remove(routeId)
    

    def update_vehicles(self):
        vIds_to_be_removed = []

        # Update all active vehicles
        for vId in self.vehicles:
            try:
                self.vehicles[vId].update(self.vehicles)
            except traci.exceptions.TraCIException as e:
                print(e)
                vIds_to_be_removed.append(vId)
        # Stop tracking any vehicles that no longer exist
        for vId in vIds_to_be_removed:
            self.vehicles.pop(vId)