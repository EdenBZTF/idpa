import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# I2C initialisieren
i2c = busio.I2C(board.SCL, board.SDA)

# OLED initialisieren (128x64)
oled = SSD1306_I2C(128, 64, i2c)

# Display löschen
oled.fill(0)
oled.show()

# Bild erstellen
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Text schreiben
draw.text((0, 0), "Hello OLED!", fill=255)

# Bild anzeigen
oled.image(image)
oled.show()
``
