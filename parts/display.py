#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.core.error import DeviceNotFoundError

from .Gps import get_current_location

from .calculate import calculate_distance, calculate_bearing

def draw_OLED(distance, bearing):

    serial = i2c(port=1, address=0x3C)  # SH1106 ist oft auch 0x3C
    try:
        device = sh1106(serial)
    except DeviceNotFoundError:
        print("OLED (SH1106) auf 0x3C nicht gefunden – prüfe Adresse/Verkabelung.")

    try:
        font = ImageFont.truetype("FreeSans.ttf", 16)
    except Exception:
        from PIL import ImageFont as IF
        font = IF.load_default()

    while True:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((6, 6),  "Ziel-Distanz:", font=font, fill="white")
            draw.text((6, 24), f"{distance:.1f} m", font=font, fill="white")
            draw.text((6, 42), f"Peilung: {bearing:.1f}°", font=font, fill="white")

        time.sleep(0.5)


   
