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

    def __init__(self, network:Network, seed:int):
        self.vehicles:dict = {}
        self.vehicleTypes:dict = {}
        self.vehicleGroups:dict = {}
        self.network:Network = network
        self.seed = seed
        self.rng:random.Random = random.Random(self.seed)
    

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
    def add_vehicles(self, vehicleGroups:dict):
        for group in vehicleGroups:
            vehGroup = vehicleGroups[group]
            self.vehicleGroups[group] = {}
            for i in range(vehGroup["num"]):
                vId = group + "-" + str(i)
                vehicle:Vehicle = Vehicle(vId)

                self.set_policy(vehicle, vehGroup)
                routeId = self.network.get_random_route_id()
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
    

    def has_active_vehicles(self):
        result = False
        for vId in self.vehicles:
            result = result or self.vehicles[vId].isActive
        return result


    def update_vehicles(self):
        vehicle_data = {}

        vehicles_to_be_updated = []
        # Update all active vehicles
        for vId in self.vehicles:
            vehicle:Vehicle = self.vehicles[vId]
            if vehicle.isActive:
                vehicles_to_be_updated.append(vehicle)
        
        while len(vehicles_to_be_updated) > 0:
            # Randomize order in which vehicles are updated - they won't necessarily be updated in order in real life!
            index = self.rng.randint(0, len(vehicles_to_be_updated) - 1)
            try:
                vehicle:Vehicle = vehicles_to_be_updated[index]
                vehicle.update(self.vehicles)
            except traci.exceptions.TraCIException as e:
                vehicle.isActive = False
            vehicles_to_be_updated.remove(vehicle)

        # Log data
        for group in self.vehicleGroups:
            vIds_to_be_removed = []
            vehGroup = self.vehicleGroups[group]
            group_data = {}
            for vId in vehGroup:
                vehicle:Vehicle = self.vehicles[vId]
                if vehicle.isActive:
                    group_data[vehicle.vehicleId] = vehicle.get_data_as_dict()
                else:
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
            policy = CustomPolicy(vehicle, path)
        elif policyType == "first-come-first-serve" or policyType == "fcfs":
            policy = FirstComeFirstServePolicy(vehicle)
        elif policyType == "priority":
            policy = PriorityPolicy(vehicle)
        else:
            policy = Policy(vehicle)
        vehicle.set_conflict_resolution_policy(policy)