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


def run_simulation(vehicles:list):
    if ("--no-gui" in sys.argv):
        sumoBinary = sumolib.checkBinary("sumo")
    else:
        sumoBinary = sumolib.checkBinary("sumo-gui")
    sumoCmd = [sumoBinary, "-c", ENV["configPath"]]

    traci.start(sumoCmd)
    for v in vehicles:
        vehicle:Vehicle = v
        vehicle.add_to_route("route_0")
    step = 0
    while step < 30:
        traci.simulationStep()
        try:
            print(traci.vehicle.getSpeed("aaa"))
        except traci.exceptions.TraCIException as e:
            print(e)
            break
        step += 1
    traci.close()


if __name__ == "__main__":
    test_vehicle = Vehicle("aaa")
    vehicles = [test_vehicle]
    run_simulation(vehicles)
