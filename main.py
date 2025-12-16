from parts import Location, calculate, Gps, Stepper, Compass
import requests
import time

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
    try:
        while True:
            print('pre 1')
            current = 'bar'
            print("Current amenity:", current)
            print('pre 2')
            coords = Location.get_nearest_amenity(current)
            print("Coordinates:", coords)
            if coords:
                print('pre 3')
                dist = calculate.calculate_distance(coords)
                print("Distance:", dist)
                bearing = calculate.calculate_bearing(coords)
                print(bearing)
            time.sleep(3)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()