import requests

def get_current_location():
    url = "http://127.0.0.1:5000/get_location"
    default_location = (47.556649952305165, 8.891523313646145)

    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            if latitude is not None and longitude is not None:
                return (float(latitude), float(longitude))
    except requests.RequestException as e:
        print(f"Could not fetch location from server: {e}")

    # fallback to default if request fails
    return default_location

