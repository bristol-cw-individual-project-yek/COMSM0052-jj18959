from cgi import test
import os, sys
import dotenv
import traci
import sumolib
from vehicle import Vehicle

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    print(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

ENV = dotenv.dotenv_values(".env")


def run_simulation(vehicleIds_to_routes:dict):
    if ("--no-gui" in sys.argv):
        sumoBinary = sumolib.checkBinary("sumo")
    else:
        sumoBinary = sumolib.checkBinary("sumo-gui")
    sumoCmd = [sumoBinary, "-c", ENV["configPath"], "--collision.check-junctions", "--collision.action", "warn"]

    traci.start(sumoCmd)

    vehicles = {}
    for vId in vehicleIds_to_routes:
        vehicle:Vehicle = Vehicle(vId)
        vehicle.add_to_route(vehicleIds_to_routes[vId])
        vehicles[vId] = vehicle
    
    step = 0
    while step < 100 and len(vehicles) > 0:
        traci.simulationStep()
        vIds_to_be_removed = []

        # Print speed and positions of all vehicles
        for vId in vehicles:
            try:
                message:str = "Speed of " + vId + ": " + str(traci.vehicle.getSpeed(vId))
                message += "\nPosition of " + vId + ": " + str(traci.vehicle.getPosition(vId))
                print(message)
            except traci.exceptions.TraCIException as e:
                print(e)
                vIds_to_be_removed.append(vId)
        # Stop tracking any vehicles that no longer exist
        for vId in vIds_to_be_removed:
            vehicles.pop(vId)
        # Print collisions that are currently happening
        print(traci.simulation.getCollisions())
        
        step += 1
    
    traci.close()


if __name__ == "__main__":
    vehicleIds_to_routes = {
        "aaa"   :   "route_0",
        "bbb"   :   "route_1"
    }
    run_simulation(vehicleIds_to_routes)
