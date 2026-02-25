
# parts/compass.py
# -*- coding: utf-8 -*-
import math
from parts.qmc5883p_raw import QMC5883P

# Optional: grobe Offsets (Hard-Iron) – erstmal 0.0.
# Die kannst du später mit einer kleinen Kalibrierfahrt ermitteln.
X_OFFSET = 0.0
Y_OFFSET = 0.0
Z_OFFSET = 0.0

# Optional: Achsen tauschen/negieren je nach Einbau
SWAP_XY = False
NEGATE_X = False
NEGATE_Y = False

# Singleton-Instanz (einmaliger Zugriff auf den Bus)
_sensor = None

def _sensor_instance() -> QMC5883P:
    global _sensor
    if _sensor is None:
        _sensor = QMC5883P(bus_id=1, addr=0x2C)
    return _sensor

def get_raw_magnet():
    """
    Liefert reale Rohwerte (x, y, z) vom QMC5883P.
    Wendet optional Achsen-Tausch, Vorzeichenwechsel und Offsets an.
    """
    x, y, z = _sensor_instance().read_raw()

    # Achsen optional anpassen
    if SWAP_XY:
        x, y = y, x
    if NEGATE_X:
        x = -x
    if NEGATE_Y:
        y = -y

    # Offsets abziehen (Hard-Iron)
    x -= X_OFFSET
    y -= Y_OFFSET
    z -= Z_OFFSET

    return x, y, z

def get_heading():
    """
    Heading in Grad (0..360) aus den korrigierten Rohwerten berechnen.
    Hinweis: je nach Einbaulage evtl. atan2(-y, x) o. Achsen tauschen.
    """
    x, y, _ = get_raw_magnet()
    angle_rad = math.atan2(x, y)
    angle_deg = math.degrees(angle_rad)
    return (angle_deg + 360) % 360
    
