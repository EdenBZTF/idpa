
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time, math
from smbus2 import SMBus

ADDR = 0x2C  # QMC5883P

def s16(v): return v - 65536 if v > 32767 else v

def init(bus, odr=3, range_sel=0, osr=2, mode=3):
    # Soft-Reset versuchen
    for reg, val in [(0x0A, 0x01), (0x0B, 0x01)]:
        try:
            bus.write_byte_data(ADDR, reg, val)
            time.sleep(0.01)
        except OSError:
            pass
    # Set/Reset aktivieren (falls vorhanden)
    try:
        bus.write_byte_data(ADDR, 0x0B, 0x01)
    except OSError:
        pass
    # Control 0x09: OSR(7:6), Range(5:4), ODR(3:2), Mode(1:0)
    ctrl = (osr << 6) | (range_sel << 4) | (odr << 2) | mode
    bus.write_byte_data(ADDR, 0x09, ctrl)
    time.sleep(0.02)

def read_raw(bus):
    # Status 0x06: DRDY=Bit0, OFLOW=Bit1
    for _ in range(50):
        try:
            status = bus.read_byte_data(ADDR, 0x06)
        except OSError:
            status = 0
        if status & 0x02:  # Overflow
            # leichte Anpassung der ODR reduziert Overflow in der Praxis
            bus.write_byte_data(ADDR, 0x09, (2 << 6) | (0 << 4) | (2 << 2) | 3)  # OSR=512, Range=2G, ODR=100Hz
            time.sleep(0.01)
        if status & 0x01:  # DRDY
            break
        time.sleep(0.005)

    data = bus.read_i2c_block_data(ADDR, 0x00, 6)
    x = s16(data[0] | (data[1] << 8))
    y = s16(data[2] | (data[3] << 8))
    z = s16(data[4] | (data[5] << 8))
    return x, y, z

def main():
    with SMBus(1) as bus:
        # Ping
        try:
            bus.read_byte(ADDR)
        except OSError:
            print("Keine Antwort von 0x2C – I²C/Verkabelung prüfen.")
            return

        # Init: ODR=200Hz, Range=2G, OSR=512, Continuous
        init(bus, odr=3, range_sel=0, osr=2, mode=3)

        # EMA-Filterparameter
        alpha = 0.2  # 0<alpha<=1; kleiner = stärker glätten
        fx = fy = fz = None

        # Offset (Hard-Iron) – erst einmal grob aus 1s Messung schätzen
        samples = []
        t0 = time.time()
        while time.time() - t0 < 1.0:
            samples.append(read_raw(bus))
            time.sleep(0.01)
        ox = sum(s[0] for s in samples)/len(samples)
        oy = sum(s[1] for s in samples)/len(samples)
        oz = sum(s[2] for s in samples)/len(samples)
        print(f"Grobe Offsets: ox={ox:.1f} oy={oy:.1f} oz={oz:.1f}")

        print("QMC5883P @0x2C – gefilterte Rohwerte + Heading, Strg+C zum Beenden")
        try:
            while True:
                x, y, z = read_raw(bus)
                # Offset abziehen
                x -= ox; y -= oy; z -= oz

                # EMA-Filter
                if fx is None:
                    fx, fy, fz = x, y, z
                else:
                    fx = alpha * x + (1 - alpha) * fx
                    fy = alpha * y + (1 - alpha) * fy
                    fz = alpha * z + (1 - alpha) * fz

                # Heading (Achsen ggf. tauschen/Negieren je nach Einbau)
                heading = (math.degrees(math.atan2(fy, fx)) + 360.0) % 360.0

                print(f"X={fx:8.1f} Y={fy:8.1f} Z={fz:8.1f}  Heading={heading:6.1f}°")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Beendet.")

if __name__ == "__main__":
    main()