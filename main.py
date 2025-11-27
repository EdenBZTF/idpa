from parts import Location 
from parts import Calculate
import requests

AMENITY_URL = "http://127.0.0.1:5000/get_amenity"   

def get_current_amenity():
    try:
        r = requests.get(AMENITY_URL, timeout=2)
        if r.status_code == 200:
            return r.json().get("amenity")
    except Exception as e:
        print("Error fetching amenity:", e)
    return None

def main():
    current = get_current_amenity()
    print("Current amenity:", current)

    coords = Location.get_nearest_amenity(current)
    print("Coordinates:", coords)

    dist = Calculate.calculate_distance(coords)
    print("Distance:", dist)

if __name__ == '__main__':
    main()