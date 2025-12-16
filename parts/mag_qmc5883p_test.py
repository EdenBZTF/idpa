
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, math
import board, busio
import adafruit_qmc5883p

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_qmc5883p.QMC5883P(i2c, address=0x2C)

# sinnvolle Startwerte
sensor.mode = adafruit_qmc5883p.MODE_CONTINUOUS
sensor.data_rate = adafruit_qmc5883p.ODR_200HZ
sensor.range = adafruit_qmc5883p.RANGE_2G           # feinster Bereich
sensor.oversample_ratio = adafruit_qmc5883p.OSR_8
sensor.downsample_ratio = adafruit_qmc5883p.DSR_1

print("QMC5883P @0x2C – Messwerte in µT, Strg+C zum Beenden")
while True:
    mx, my, mz = sensor.magnetic    # µT
    heading = (math.degrees(math.atan2(my, mx)) + 360.0) % 360.0
    print(f"X={mx:7.2f} µT  Y={my:7.2f} µT  Z={mz:7.2f} µT  Heading={heading:6.1f}°")
    time.sleep(3)
