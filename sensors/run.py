import board
import busio
import adafruit_dht
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import time
import os
import math

# VPD Cannabis
# < 0.4: Danger Zone
# 0.4 to 0.8: Low Transition (Early Vegetative Phase / Propagation)
# 0.8 to 1.2: Late Vegetative / Early Flower (Healthy Transpiration)
# 1.2 to 1.6: Mid/ Late Flower (High Transpiration)
# > 1.6: Danger Zone

# Initialisiere die I2C-Verbindung
i2c = busio.I2C(board.SCL, board.SDA)

# Initialisiere das OLED-Display (128x64)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Initialisiere den DHT-Sensor
dht_sensor = adafruit_dht.DHT22(board.D4)  # Ersetze D4 durch den richtigen Pin

# Funktion, um den Sättigungsdampfdruck zu berechnen
def saturation_vapor_pressure(temp_c):
    return 0.6108 * math.exp(17.27 * temp_c / (temp_c + 237.3))

# Funktion, um den VPD zu berechnen
def calculate_vpd(room_temp, humidity):
    # Blatt-Temperatur ist 2 Grad kälter als Raumtemperatur
    leaf_temp = room_temp - 2.0

    # Sättigungsdampfdruck für Blatt- und Raumtemperatur
    es_leaf = saturation_vapor_pressure(leaf_temp)  # Sättigungsdampfdruck bei Blatt-Temp
    es_room = saturation_vapor_pressure(room_temp)  # Sättigungsdampfdruck bei Raum-Temp

    # Tatsächlicher Dampfdruck in der Luft (abhängig von Raum-Temp und Luftfeuchtigkeit)
    ea = humidity * es_room / 100.0  # Relative Feuchtigkeit in % wird auf 0-1 normiert

    # VPD (Differenz zwischen Sättigungsdampfdruck am Blatt und tatsächlichem Dampfdruck)
    vpd = es_leaf - ea
    return vpd

# Funktion, um Temperatur und Luftfeuchtigkeit zu lesen
def read_sensor():
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        return temperature, humidity
    except Exception as e:
        print("Fehler beim Lesen des Sensors:", e)
        return None, None

# Lade eine größere Schriftart
font_path = "RobotoCondensed-Regular.ttf"  # Beispiel für eine andere Schriftart
if not os.path.exists(font_path):
    print(f"Schriftartdatei '{font_path}' nicht gefunden.")
    # Hier den vollständigen Pfad zur Schriftart angeben, falls nötig
    font_path = "/home/thegreenbox/display/RobotoCondensed-Bold.ttf"  # Ersetze dies durch den richtigen Pfad

try:
    font = ImageFont.truetype(font_path, 13)  # Schriftgröße anpassen
except OSError:
    print(f"Kann die Schriftart '{font_path}' nicht laden. Stelle sicher, dass es sich um eine TrueType-Datei handelt.")
    font = ImageFont.load_default()  # Standard-Schriftart verwenden, falls Fehler auftritt

# Hauptschleife
while True:
    # Sensorwerte lesen
    temperature, humidity = read_sensor()
    vpd = calculate_vpd(temperature, humidity)
    vpd_rounded = round(vpd, 2)

    # Display löschen
    oled.fill(0)

    # Neues Bild erstellen
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Balken zeichnen (15 Pixel hoch)
    bar_height = 13
    draw.rectangle([0, 0, oled.width, bar_height], fill=255)

    # Texte für Temperatur und Luftfeuchtigkeit
    if temperature is not None and humidity is not None:
        draw.text((10, bar_height + 0), f'Temp: {temperature:.1f}C', font=font, fill=255)
        draw.text((10, bar_height + 15), f'Hum: {humidity:.1f}%', font=font, fill=255)
        draw.text((10, bar_height + 30), f'VPD: {vpd_rounded}', font=font, fill=255)
    else:
        draw.text((10, bar_height + 5), 'Temp: --.-C', font=font, fill=255)
        draw.text((10, bar_height + 25), 'Hum: --.-%', font=font, fill=255)
        draw.text((10, bar_height + 45), 'Sensor: Fehler', font=font, fill=255)

    # Bild auf das Display laden
    oled.image(image)
    oled.show()

    # Wartezeit
    time.sleep(2)
