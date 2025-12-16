
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from smbus2 import SMBus

def try_hmc5883l(bus, addr):
    """
    HMC5883L: Adresse typ. 0x1E.
    ID-Register: 0x0A, 0x0B, 0x0C -> üblicherweise 'H','4','3'
    Datenregister: 0x03..0x08 (MSB/LSB X,Z,Y)
    """
    try:
        ida = bus.read_byte_data(addr, 0x0A)
        idb = bus.read_byte_data(addr, 0x0B)
        idc = bus.read_byte_data(addr, 0x0C)
        print(f"[HMC5883L? @ {hex(addr)}] ID: {chr(ida)} {chr(idb)} {chr(idc)}")
    except Exception as e:
        print(f"[HMC5883L? @ {hex(addr)}] ID-Read Fehler: {e}")
        return False

    # rudimentäre Plausibilitätsprüfung
    if ida == ord('H') and idb == ord('4') and idc == ord('3'):
        # Config: 8 Samples, 15Hz, Normal
        bus.write_byte_data(addr, 0x00, 0x70)
        # Gain: 1.3 Ga
        bus.write_byte_data(addr, 0x01, 0x20)
        # Mode: Continuous
        bus.write_byte_data(addr, 0x02, 0x00)
        time.sleep(0.01)
        # einmal Messwerte lesen
        data = bus.read_i2c_block_data(addr, 0x03, 6)  # X,Z,Y Reihenfolge
        x = (data[0] << 8) | data[1]
        z = (data[2] << 8) | data[3]
        y = (data[4] << 8) | data[5]
        # Zweierkomplement wandeln
        def to_signed(n): return n - 65536 if n > 32767 else n
        x, y, z = map(to_signed, (x, y, z))
        print(f"[HMC5883L] Raw X={x} Y={y} Z={z}")
        return True
    else:
        print("[HMC5883L] ID nicht passend – vermutlich kein HMC5883L.")
        return False

def try_qmc5883l(bus, addr):
    """
    QMC5883L: Adresse typ. 0x0D.
    Register:
      Control: 0x09 (OSR|Range|ODR|Mode)
      Data: 0x00..0x05 -> X LSB/MSB, Y LSB/MSB, Z LSB/MSB
    """
    try:
        # Init: OSR=512(10), Range=2G(01), ODR=50Hz(10), Mode=Continuous(01)
        # Bits: OSR(7:6), RNG(5:4), ODR(3:2), MODE(1:0)
        ctrl = (2 << 6) | (1 << 4) | (2 << 2) | 1
        bus.write_byte_data(addr, 0x09, ctrl)
        time.sleep(0.02)
        data = bus.read_i2c_block_data(addr, 0x00, 6)
        # LSB/MSB
        x = data[0] | (data[1] << 8)
        y = data[2] | (data[3] << 8)
        z = data[4] | (data[5] << 8)
        # QMC5883L liefert 16-bit signed
        def to_signed16(v): return v - 65536 if v > 32767 else v
        x, y, z = map(to_signed16, (x, y, z))
        print(f"[QMC5883L] Raw X={x} Y={y} Z={z}")
        return True
    except Exception as e:
        print(f"[QMC5883L? @ {hex(addr)}] Fehler: {e}")
        return False

def dump_registers(bus, addr, start=0x00, length=0x40):
    try:
        vals = bus.read_i2c_block_data(addr, start, length)
        print(f"[Dump @ {hex(addr)} {hex(start)}..{hex(start+length-1)}]")
        print(" ".join(f"{v:02X}" for v in vals))
    except Exception as e:
        print(f"[Dump @ {hex(addr)}] Fehler: {e}")

def main():
    with SMBus(1) as bus:
        # bekannte Adressen prüfen
        candidates = [0x1E, 0x0D, 0x2C]  # 0x2C aus deinem Scan
        found = False

        for addr in candidates:
            print(f"\n=== Prüfe Adresse {hex(addr)} ===")
            try:
                # einfacher Ping: lese ein Byte irgendwo – kann fehlschlagen
                bus.read_byte(addr)
                print(f"I²C-Gerät antwortet auf {hex(addr)}.")
            except Exception:
                print(f"Keine direkte Antwort auf {hex(addr)} (nicht zwingend ein Problem).")

            # Treiber-Versuche
            if addr == 0x1E:
                found = try_hmc5883l(bus, addr) or found
            elif addr == 0x0D:
                found = try_qmc5883l(bus, addr) or found
            elif addr == 0x2C:
                print("Adresse 0x2C ist für HMC/QMC untypisch – wir dumpen Register zur Identifikation.")
                dump_registers(bus, addr, start=0x00, length=32)

        if not found:
            print("\n⚠️ Kein eindeutig unterstützter Magnetometer erkannt.")
            print("→ Viele GY            print("→ Viele GY-273 sind QMC5883L (meist 0x0D).")
            print("→ Dein Modul auf 0x2C könnte ein anderer Chip sein. Sende mir bitte Fotos/Board-Label.")

if __name__ == "__main__":
    main()
