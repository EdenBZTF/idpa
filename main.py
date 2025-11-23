from parts.Location import get_nearest_amenity
from parts.calculate import calculate_distance

import csv
import os

def get_current_amenity():
    with open('webserver/amenities.csv', mode='r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            name, selected, *_ = row
            if selected == '1':
                return name
    return None

c = get_current_amenity()
cords = get_nearest_amenity(get_current_amenity())
print(cords)
print(calculate_distance(cords))