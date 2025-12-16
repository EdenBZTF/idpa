
# parts/qmc5883p_raw.py
# -*- coding: utf-8 -*-
import time
from smbus2 import SMBus

QMC_ADDR = 0x2C  # dein Sensor meldet 0x2C

def _s16(v: int) -> int:
    return v - 65536 if v > 32767 else v

class QMC5883P:
    """
    Minimaler RAW-Treiber für QMC5883P:
    - Initialisiert den Sensor (Soft-Reset, Set/Reset, Control 0x09)
    - Liest Rohdaten X/Y/Z aus den Datenregistern (0x00..0x05)
    - Pollt Status (DRDY/Overflow)
    """

    def __init__(self, bus_id: int = 1, addr: int = QMC_ADDR):
        self.bus_id = bus_id
        self.addr = addr
        self.bus = SMBus(bus_id)
        self._init_sensor()

    def _init_sensor(self):
        # Soft-Reset versuchen (manche Derivate nutzen 0x0A oder 0x0B)
        for reg, val in [(0x0A, 0x01), (0x0B, 0x01)]:
            try:
                self.bus.write_byte_data(self.addr, reg, val)
                time.sleep(0.01)
            except OSError:
                pass

        # Set/Reset aktivieren (falls vorhanden)
        try:
            self.bus.write_byte_data(self.addr, 0x0B, 0x01)
        except OSError:
            pass

        # Control-Register 0x09 setzen:
        # OSR(7:6)=512(10), Range(5:4)=2G(00), ODR(3:2)=200Hz(11), Mode(1:0)=Continuous(11)
        ctrl = (2 << 6) | (0 << 4) | (3 << 2) | 3
        self.bus.write_byte_data(self.addr, 0x09, ctrl)
        time.sleep(0.02)

    def _wait_drdy(self, timeout_ms: int = 250):
        """Wartet bis DRDY=1 im Statusregister 0x06, begrenzt durch timeout."""
        t0 = time.time()
        while (time.time() - t0) * 1000 < timeout_ms:
            try:
                status = self.bus.read_byte_data(self.addr, 0x06)
            except OSError:
                status = 0
            if status & 0x02:  # Overflow
                # leichte Anpassung reduziert Overflow manchmal
                ctrl = (2 << 6) | (0 << 4) | (2 << 2) | 3  # ODR=100Hz
                self.bus.write_byte_data(self.addr, 0x09, ctrl)
                time.sleep(0.01)
            if status & 0x01:  # DRDY
                return True
            time.sleep(0.005)
        return False

    def read_raw(self):
        """Liest einen Datensatz (x, y, z) als signed 16-bit Rohwerte."""
        self._wait_drdy()
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 6)
        x = _s16(data[0] | (data[1] << 8))
        y = _s16(data[2] | (data[3] << 8))
        z = _s16(data[4] | (data[5] << 8))
        return x, y, z

    def close(self):
        try:
            self.bus.close()
        except Exception:
