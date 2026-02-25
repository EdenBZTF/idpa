import math
import time
import requests

from parts import Location, calculate, Gps, stepper, compass, display

# ---------------- CONFIG ----------------

AMENITY_URL = "http://127.0.0.1:5000/get_amenity"

UPDATE_INTERVAL = 0.5
DEADZONE_DEGREES = 5
COMPASS_SAMPLES = 12
MOTOR_SETTLE_TIME = 0.25

# ----------------------------------------

COMPASS_OFFSET = 0.0
needle_angle = 0.0            # REAL needle position (tracked)
filtered_heading = None       # compass filter state


# ---------- HELPERS ----------

def circular_mean(deg_list):
    sin_sum = sum(math.sin(math.radians(d)) for d in deg_list)
    cos_sum = sum(math.cos(math.radians(d)) for d in deg_list)
    return (math.degrees(math.atan2(sin_sum, cos_sum)) + 360) % 360


def shortest_rotation(target, current):
    """Return minimal rotation from current to target (-180 to +180)."""
    return (target - current + 540) % 360 - 180


def lowpass_circular(new, old, alpha=0.25):
    """Low-pass filter for angles in degrees."""
    if old is None:
        return new
    delta = shortest_rotation(new, old)
    return (old + alpha * delta) % 360


def read_compass():
    readings = []
    for _ in range(COMPASS_SAMPLES):
        readings.append(compass.get_heading() % 360)
        time.sleep(0.05)
    return circular_mean(readings)


def get_current_amenity():
    try:
        r = requests.get(AMENITY_URL, timeout=2)
        if r.status_code == 200:
            return r.json().get("amenity")
    except Exception as e:
        print("Amenity fetch error:", e)
    return None


# ---------- MAIN ----------

def main():
    global COMPASS_OFFSET, needle_angle, filtered_heading

    print("BarFinder gestartet")
    print("Kalibriere Magnetometer – Gerät zeigt nach Norden")

    # ---------- CALIBRATION ----------
    samples = []
    for _ in range(12):
        samples.append(compass.get_heading() % 360)
        time.sleep(0.1)

    measured = circular_mean(samples)
    COMPASS_OFFSET = (-measured) % 360

    needle_angle = 0.0   # needle points forward at startup

    print(f"Gemessener Heading: {measured:.1f}°")
    print(f"Compass Offset: {COMPASS_OFFSET:.1f}°")

    try:
        while True:
            amenity = get_current_amenity()
            print(f"\nAktuelles Ziel: {amenity}")

            if not amenity:
                time.sleep(UPDATE_INTERVAL)
                continue

            target_coords = Location.get_nearest_amenity(amenity)
            if not target_coords:
                print("Keine Zielkoordinaten")
                time.sleep(UPDATE_INTERVAL)
                continue

            current_location = Gps.get_current_location()
            if not current_location:
                print("Keine GPS-Position")
                time.sleep(UPDATE_INTERVAL)
                continue

            distance = calculate.calculate_distance(target_coords)
            bearing = calculate.calculate_bearing(target_coords)

            # ---------- COMPASS ----------
            raw_heading = read_compass()
            heading = (raw_heading + COMPASS_OFFSET) % 360
            filtered_heading = lowpass_circular(heading, filtered_heading)

            # ---------- NEEDLE CONTROL ----------
            desired_needle = (bearing - filtered_heading) % 360
            delta = shortest_rotation(desired_needle, needle_angle)

            print(f"Distanz: {distance:.1f} m")
            print(f"Heading: {filtered_heading:.1f}°")
            print(f"Bearing: {bearing:.1f}°")
            print(f"Nadel Soll: {desired_needle:.1f}°")
            print(f"Nadel Ist: {needle_angle:.1f}°")
            print(f"Drehung: {delta:.1f}°")

            if abs(delta) > DEADZONE_DEGREES:
                stepper.rotate_degrees(-delta, 300)
                # Update needle to absolute position after move
                needle_angle = desired_needle
                time.sleep(MOTOR_SETTLE_TIME)
            else:
                print("Innerhalb Deadzone")

            display.draw_OLED(distance, amenity)
            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\nBeendet durch Benutzer")


if __name__ == "__main__":
    main()
