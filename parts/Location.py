import requests
from .Gps import get_current_location
from geopy.distance import geodesic

def get_nearest_amenity(amenity):
    my_location = get_current_location()

    query = f"""
    [out:json];
    node["amenity"="{amenity}"](around:1000,{my_location[0]},{my_location[1]});
    out skel;
    """

    url = "https://overpass.osm.ch/api/interpreter"
    # url = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.get(url, params={'data': query}, timeout=10)
        data = response.json()
    except Exception as e:
        print("Error fetching data from Overpass API:", e)
        data = {"elements": []}
    nearest = None
    min_dist = float("inf")

    for element in data["elements"]:
        bench_location = (element["lat"], element["lon"])
        dist = geodesic(my_location, bench_location).meters
        if dist < min_dist:
            min_dist = dist
            nearest = bench_location

    return nearest
