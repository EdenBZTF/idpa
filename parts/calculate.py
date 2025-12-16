import math
from geopy.distance import geodesic
from .Gps import get_current_location

def calculate_distance(cords):
    my_location = get_current_location() #bztf
    return round(geodesic(my_location, cords).meters, 1)

def calculate_bearing(target_coords):
    lat1, lon1 = get_current_location()
    lat2, lon2 = target_coords

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dLon = lon2 - lon1

    x = math.sin(dLon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(dLon)

    bearing_rad = math.atan2(x, y) 
    bearing_deg = math.degrees(bearing_rad)

    bearing_deg = (bearing_deg + 360) % 360

    return bearing_deg
