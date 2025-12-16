from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont

# I2C-Interface initialisieren
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Testanzeige
with canvas(device) as draw:
   
