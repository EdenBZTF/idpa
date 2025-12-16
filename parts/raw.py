
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time, math
from smbus2 import SMBus

ADDR = 0x2C  # QMC5883P-Standardadresse (laut aktuellen Guides/Datenblättern)

def s16(v):  # 16-bit signed
    return v - 65536 if v > 32767 else v

def init_qmc5883p(bus):
    """
    Robuste Initialisierung:
    - Soft-Reset (verschiedene Registervarianten testen)
    - Set/Reset aktivieren
    - Control-Register konfigurieren (OSR/Range/ODR/Mode)
    """
    # 1) Soft-Reset: manche Derivate verwenden 0x0A oder 0x0B als Reset-Kommando
    for reg, val in [(0x0A, 0x01), (0x0B, 0x01)]:
        try:
            bus.write_byte_data(ADDR, reg, val)
            time.sleep(0.01)
        except OSError:
            pass

    # 2) Set/Reset aktivieren (falls vorhanden)
    try:
        # 0x0B: Set/Reset Mode (bei vielen Boards 0x01 = enable)
        bus.write_byte_data(ADDR, 0x0B, 0x01)
    except OSError:
        pass

    # 3) Control-Register 0x09 setzen:
    # Bits: OSR(7:6), Range(5:4), ODR(3:2), Mode(1:0)
    # Empfehlung: OSR=512(10), Range=2G(00), ODR=200Hz(11), Mode=Continuous(11)
    ctrl = (2 << 6) | (0 << 4) | (3 << 2) | 3
    bus.write_byte_data(ADDR, 0x09, ctrl)
    time.sleep(0.02)

def read_once(bus, swap_xy=False):
    """
    Liest einen Messsatz:
    - wartet auf DRDY (Status 0x06, Bit0)
    - prüft Overflow (Bit1)
    - liest 6 Bytes: X_L, X_H, Y_L, Y_H, Z_L, Z_H
    - Achsen optional tauschen, je nach Boardausrichtung
    """
    # 1) Status poll, bis DRDY=1
    for _ in range(50):  # ~50*5ms = 250ms Timeout
        try:
            status = bus.read_byte_data(ADDR, 0x06)
        except OSError:
            status = 0
        drdy = bool(status & 0x01)      # Data Ready
        overflow = bool(status & 0x02)  # Overflow
        if overflow:
            # Bei Overflow: Soft-Reset / CTRL neu setzen hilft oft kurz
            bus.write_byte_data(ADDR, 0x09, (2 << 6) | (0 << 4) | (2 << 2) | 3)  # ODR 100Hz
            time.sleep(0.01)
        if drdy:
            break
        time.sleep(0.005)

    # 2) Daten lesen
    data = bus.read_i2c_block_data(ADDR, 0x00, 6)
    x = s16(data[0] | (data[1] << 8))
    y = s16(data[2] | (data[3] << 8))
    z = s16(data[4] | (data[5] << 8))

    # 3) Optional Achsen tauschen (manche Boards sind "verdreht")
    if swap_xy:
        x, y = y, x

    # 4) Heading berechnen (ggf. Vorzeichen abhängig von Einbaulage anpassen)
    heading = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
    return x, y, z, heading

def main():
    with SMBus(1) as bus:
        # einfacher "Ping": wenn das fehlschlägt, Verkabelung/Adresse prüfen
        try:
            bus.read_byte(ADDR)
        except OSError:
            print("❌ Keine Antwort von 0x2C – prüfe I²C/Verkabelung/Versorgung.")
            return

        init_qmc5883p(bus)

        print("QMC5883P @0x2C – Rohwerte, Strg+C zum Beenden")
        try:
            while True:
                x, y, z, heading = read_once(bus, swap_xy=False)
                print(f"Raw X={x:6d} Y={y:6d} Z={z:6d}  Heading={heading:6.1f}°")
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Beendet.")

if __name__ == "__main__":
    main()
