import traceback
from vehicle.vehicle import Vehicle
from vehicle.policy.custom_policy import CustomPolicy
from vehicle.policy.policy import Policy
from vehicle.policy.first_come_first_serve_policy import FirstComeFirstServePolicy
import random
import traci
from network.network import Network

class VehicleShepherd:

    def __init__(self, network:Network):
        self.vehicles:dict = {}
        self.vehicleTypes:dict = {}
        self.network:Network = network
    

    def add_vehicle_types(self, vehicleTypes:dict):
        self.vehicleTypes = vehicleTypes
        for vehicleType in vehicleTypes:
            vehType = vehicleTypes[vehicleType]
            traci.vehicletype.copy("DEFAULT_VEHTYPE", vehicleType)
            try:
                traci.vehicletype.setHeight(vehicleType, vehType["height"])
            except KeyError as e:
                pass
            try:
                traci.vehicletype.setWidth(vehicleType, vehType["width"])
            except KeyError as e:
                pass
            try:
                traci.vehicletype.setLength(vehicleType, vehType["length"])
            except KeyError as e:
                pass
            try:
                colourHex = vehType["colour"]
                r = (colourHex >> 16) & 0xff
                g = (colourHex >> 8) & 0xff
                b = colourHex & 0xff
                a = 0xff
                traci.vehicletype.setColor(vehicleType, (r, g, b, a))
            except KeyError as e:
                pass
        print("Vehicle types: " + str(traci.vehicletype.getIDList()))
    

    # TODO: Write test for this
    def add_vehicles(self, vehicleGroups:dict, routeIds: list):
        for group in vehicleGroups:
            vehGroup = vehicleGroups[group]
            for i in range(vehGroup["num"]):
                vId = group + "-" + str(i)
                vehicle:Vehicle = Vehicle(vId)
                policyType = vehGroup["policy-type"]
                if policyType == "custom":
                    path = vehGroup["policy-path"]
                    policy = CustomPolicy(path)
                elif policyType == "first-come-first-serve" or policyType == "fcfs":
                    policy = FirstComeFirstServePolicy()
                else:
                    policy = Policy()
                vehicle.set_conflict_resolution_policy(policy)
                routeId = routeIds[random.randint(0, len(routeIds) - 1)]
                if "vehicle-type" in vehGroup:
                    try:
                        vehType = vehGroup["vehicle-type"]
                        vehicle.set_vehicle_type(vehType)
                    except KeyError:
                        print(traceback.format_exc())
                    except traci.exceptions.TraCIException:
                        print(traceback.format_exc())
                    try:
                        vehicle.set_speed(self.vehicleTypes[vehType]["speed"])
                    except KeyError:
                        print(traceback.format_exc())
                
                vehicle.add_to_route(routeId, self.network)
                self.vehicles[vId] = vehicle
                routeIds.remove(routeId)
    

    def update_vehicles(self):
        vIds_to_be_removed = []

        # Update all active vehicles
        for vId in self.vehicles:
            try:
                vehicle:Vehicle = self.vehicles[vId]
                vehicle.update(self.vehicles, self.network)
            except traci.exceptions.TraCIException as e:
                print(e)
                vIds_to_be_removed.append(vId)
        # Stop tracking any vehicles that no longer exist
        for vId in vIds_to_be_removed:
            self.vehicles.pop(vId)