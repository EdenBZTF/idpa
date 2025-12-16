from .mock import MockGPS

def get_current_location():
    data = MockGPS().read()
    return (data["latitude"], data["longitude"])
