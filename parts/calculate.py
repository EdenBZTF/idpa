from geopy.distance import geodesic
from parts.Gps import get_current_location

def calculate_distance(cords):
    my_location = get_current_location()
    return geodesic(my_location, cords).meters