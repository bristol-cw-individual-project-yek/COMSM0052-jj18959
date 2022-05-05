#import src.vehicle.vehicle as veh
import sumolib
import shapely.geometry as geometry

def is_in_junction(vehicle, junction:sumolib.net.node.Node):
    junction_shape = geometry.Polygon(junction.getShape())
    vehicle_location = geometry.Point(vehicle.currentPosition)
    return junction_shape.contains(vehicle_location)