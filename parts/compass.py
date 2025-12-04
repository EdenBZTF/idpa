from parts.mock import MockCompass
import math

def get_raw_magnet():
    return MockCompass().get_magnet()

def get_heading():
    x, y, z = get_raw_magnet()

    angle_rad = math.atan2(y, x)
    angle_deg = math.degrees(angle_rad)

    return (angle_deg + 360) % 360
