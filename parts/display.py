from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont
import subprocess

# I2C-Scan durchführen
print("Scanne I²C-Bus...")
scan = subprocess.check_output(["i2cdetect", "-y", "1"]).decode()
address = None
for line in scan.splitlines():
    if "3c" in line.lower():
        address = 0x3C
    elif "3d" in line.lower():
        address = 0x3D

if address is None:
    print("Kein OLED-Display gefunden! Bitte Verkabelung prüfen.")
    exit(1)

print(f"OLED gefunden auf Adresse: {hex(address)}")

# OLED initialisieren
serial = i2c(port=1, address=address)
device = ssd1306(serial)

# Schriftart laden
font = ImageFont.load_default()

# Testanzeige
with canvas(device) as draw:
    draw.text((10, 10), "Hello OLED!", font=font, fill="white")
    draw.text((10, 30), f"Addr: {hex(address)}", font=font, fill="white")

