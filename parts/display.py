import time
from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont

serial = i2c(port=1, address=0x3C)

device = sh1106(serial)

font = ImageFont.truetype('FreeSans.ttf', 18)

try:
   while True:
      with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((15, 20), "Hello World!", font=font, fill="white")

except KeyboardInterrupt:
  print("Programm wurde beendet!")