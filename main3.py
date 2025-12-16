from parts import Location, calculate, Gps, stepper, compass, display
import requests
import time

# ---------------- CONFIG ----------------

AMENITY_URL = "http://127.0.0.1:5000/get_amenity"

COMPASS_OFFSET = 2          # Kalibrierung (358° → 0°)
UPDATE_INTERVAL = 3         # Sekunden
DEADZONE_DEGREES = 2        # Unterhalb davon nicht drehen

# ----------------------------------------

# Merkt sich die aktuelle physische Position der Nadel
current_needle_angle = 0


def get_current_amenity():
    try:
        r = requests.get(AMENITY_URL, timeout=2)
        if r.status_code == 200:
            return r.json().get("amenity")
    except Exception as e:
        print("Error fetching amenity:", e)
    return None


def shortest_rotation(target, current):
    """
    Berechnet die kürzeste Drehung von current → target
    Rückgabe: Wert zwischen -180° und +180°
    """
    return (target - current + 540) % 360 - 180


def main():
    global current_needle_angle

    print("BarFinder gestartet 🚀")

    try:
        while True:
            # --- 1️⃣ Ziel ---
            amenity = "bar"
            print("\nAktuelles Ziel:", amenity)

            target_coords = Location.get_nearest_amenity(amenity)
            if not target_coords:
                print("Keine Zielkoordinaten gefunden")
                time.sleep(UPDATE_INTERVAL)
                continue

            print("Zielkoordinaten:", target_coords)
            print("meine Koordinaten:", Gps.get_current_location())

            # --- 2️⃣ Eigene Position ---
            location_now = Gps.get_current_location()
            if not location_now:
                print("Keine GPS-Position")
                time.sleep(UPDATE_INTERVAL)
                continue

            # --- 3️⃣ Distanz & Bearing ---
            distance = calculate.calculate_distance(target_coords)
            bearing_to_target = calculate.calculate_bearing(target_coords)

            current_heading = 0
            
            for _ in range(50):
                current_heading += compass.get_heading()
                time.sleep(0.2)
            current_heading /= 50
            print(f"Aktueller Kompasswert (gemittelt): {current_heading:.1f}°")
            
            # --- 4️⃣ Kompass ---
            heading = (current_heading + COMPASS_OFFSET) % 360

            # Wo SOLL die Nadel stehen?
            target_needle_angle = (bearing_to_target - heading) % 360

            # --- 5️⃣ Drehung berechnen ---
            delta = shortest_rotation(target_needle_angle, current_needle_angle)

            print(f"Distanz: {distance:.1f} m")
            print(f"Kompass Heading: {heading:.1f}°")
            print(f"Zielwinkel: {target_needle_angle:.1f}°")
            print(f"Drehung nötig: {delta:.1f}°")

            # --- 6️⃣ Drehen (nur wenn nötig) ---
            if abs(delta) > DEADZONE_DEGREES:
                print(f"Drehe Nadel um {delta:.1f}°. Current: {current_needle_angle:.1f}° → Target: {target_needle_angle:.1f}°")
                stepper.rotate_degrees(delta, 1000)
                current_needle_angle = (current_needle_angle + delta) % 360
            else:
                print("Innerhalb Deadzone – keine Drehung")

            # --- 7️⃣ Display ---
            display.draw_OLED(distance, target_needle_angle)

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("\nBeendet durch Benutzer")

    except Exception as e:
        print("Fehler:", e)


if __name__ == "__main__":
    main()