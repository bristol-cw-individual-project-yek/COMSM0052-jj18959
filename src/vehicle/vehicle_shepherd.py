import traceback
from src.vehicle.vehicle import Vehicle
from src.vehicle.policy.custom_policy import CustomPolicy
from src.vehicle.policy.policy import Policy
from src.vehicle.policy.first_come_first_serve_policy import FirstComeFirstServePolicy
from src.vehicle.policy.priority_policy import PriorityPolicy
import random
import traci
from src.network.network import Network

class VehicleShepherd:

    def __init__(self, network:Network):
        self.vehicles:dict = {}
        self.vehicleTypes:dict = {}
        self.vehicleGroups:dict = {}
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
            self.vehicleGroups[group] = {}
            missed_vehicles = 0
            for i in range(vehGroup["num"]):
                
                if len(routeIds) > 0:
                    vId = group + "-" + str(i)
                    vehicle:Vehicle = Vehicle(vId)

                    self.set_policy(vehicle, vehGroup)
                    routeId = routeIds[random.randint(0, len(routeIds) - 1)]
                    vehicle.add_to_route(routeId, self.network)

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
                    try:
                        vehicle.set_priority(vehGroup["priority"])
                    except KeyError:
                        print(traceback.format_exc())
                    
                    if "svo" in vehGroup:
                        vehicle.svo_angle = vehGroup["svo"]
                    elif "social-value-orientation" in vehGroup:
                        vehicle.svo_angle = vehGroup["social-value-orientation"]
                    elif "social_value_orientation" in vehGroup:
                        vehicle.svo_angle = vehGroup["social_value_orientation"]
                    
                    self.vehicles[vId] = vehicle
                    self.vehicleGroups[group][vId] = vehicle
                    routeIds.remove(routeId)
                else:
                    missed_vehicles += 1
        if missed_vehicles > 0:
            # TODO: Do something with missed vehicles
            print(f"Vehicles not created: {missed_vehicles}")
    

    def update_vehicles(self):
        vehicle_data = {}

        # Update all active vehicles
        for group in self.vehicleGroups:
            vIds_to_be_removed = []
            vehGroup = self.vehicleGroups[group]
            group_data = {}
            for vId in vehGroup:
                try:
                    vehicle:Vehicle = self.vehicles[vId]
                    vehicle.isActive = True
                    vehicle.update(self.vehicles)
                    group_data[vehicle.vehicleId] = vehicle.get_data_as_dict()
                except traci.exceptions.TraCIException as e:
                    vehicle.isActive = False
                    vIds_to_be_removed.append(vId)
            # Stop tracking any vehicles that no longer exist
            for vId in vIds_to_be_removed:
                self.vehicleGroups[group].pop(vId)
            vehicle_data[group] = group_data

        data = {
            "vehicle_groups":   vehicle_data
        }
        
        return data
    

    def get_vehicle_metadata(self):
        data = {}
        for vehId in self.vehicles:
            vehicle:Vehicle = self.vehicles[vehId]
            data[vehId] = vehicle.get_data_as_dict(include_metadata=True, include_info=False)
        return data


    def set_policy(self, vehicle:Vehicle, vehGroup:dict):
        policyType = vehGroup["policy-type"]
        if policyType == "custom":
            path = vehGroup["policy-path"]
            policy = CustomPolicy(path)
        elif policyType == "first-come-first-serve" or policyType == "fcfs":
            policy = FirstComeFirstServePolicy()
        elif policyType == "priority":
            policy = PriorityPolicy()
        else:
            policy = Policy()
        vehicle.set_conflict_resolution_policy(policy)