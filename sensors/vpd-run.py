import board
import busio
import adafruit_dht
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import time
import os
import math
import mh_z19
import RPi.GPIO as GPIO
import logging
from datetime import datetime
import requests

PUSHGATEWAY_URL = 'http://localhost:9091/metrics/job/environment'
FONT_PATH="/home/thegreenbox/thegreenbox/git/thegreenbox/sensors/fonts/"
FONT_NAME="RobotoCondensed-ExtraBold.ttf"
font_path=FONT_PATH+FONT_NAME

# Logging-Konfiguration
logging.basicConfig(
    filename='sensor_logfile.log',  # Name des Logfiles
    level=logging.INFO,  # Log-Level (INFO oder DEBUG, je nach Wunsch)
    format='%(asctime)s - %(message)s',  # Format der Logausgabe
    datefmt='%Y-%m-%d %H:%M:%S'  # Datums- und Zeitformat
)

GPIO.setmode(GPIO.BCM)

# Pin definieren, an dem das Relay angeschlossen ist
# TODO: Change to correct pin name
relay_pin = 10
relay_pin_abluft = 9

GPIO.setup(relay_pin, GPIO.OUT)
GPIO.setup(relay_pin_abluft, GPIO.OUT)


# VPD-Bereiche definieren
def vpd_range_message(vpd):
    if vpd < 0.4:
        return "!! Danger Zone !!"
    elif 0.4 <= vpd < 0.8:
        return "Low VPD"
    elif 0.8 <= vpd < 1.2:
        return "Healthy VPD :)  :)"
    elif 1.2 <= vpd < 1.6:
        return "High VPD"
    else:
        return "!! Danger Zone !!"

# Funktion, um den Sättigungsdampfdruck zu berechnen
def saturation_vapor_pressure(temp_c):
    return 0.6108 * math.exp(17.27 * temp_c / (temp_c + 237.3))

# Funktion, um den VPD zu berechnen
def calculate_vpd(room_temp, humidity):
    leaf_temp = room_temp - 2.0  # Blatt-Temperatur
    es_leaf = saturation_vapor_pressure(leaf_temp)  # Sättigungsdampfdruck
    es_room = saturation_vapor_pressure(room_temp)  # Sättigungsdampfdruck
    ea = humidity * es_room / 100.0  # Tatsächlicher Dampfdruck in der Luft
    vpd = es_leaf - ea  # VPD (Differenz zwischen Sättigungsdampfdruck und tatsächlichem Dampfdruck)
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

i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
dht_sensor = adafruit_dht.DHT22(board.D4)  # Ersetze D4 durch den richtigen Pin

# Lade eine Schriftart
if not os.path.exists(font_path):
    font_path = FONT_PATH + FONT_NAME
try:
    font = ImageFont.truetype(font_path, 12)  # Schriftgröße anpassen
except OSError:
    print(f"Kann die Schriftart '{font_path}' nicht laden. Verwende Standardschriftart.")
    font = ImageFont.load_default()  # Standard-Schriftart verwenden, falls Fehler auftritt

# Hauptschleife
while True:
    # Sensorwerte lesen
    temperature, humidity = read_sensor()

    if temperature is not None and humidity is not None:
        vpd = calculate_vpd(temperature, humidity)
        vpd_rounded = round(vpd, 2)
        vpd_message = vpd_range_message(vpd_rounded)  # VPD-Zustand ermitteln
    else:
        vpd_message = "Sensor Error"
        vpd_rounded = "--"

    # Display löschen
    oled.fill(0)

    # Neues Bild erstellen
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Balken oben zeichnen (15 Pixel hoch)
    bar_height = 18
    draw.rectangle([0, 0, oled.width, bar_height], fill=0)

    co2 = mh_z19.read()
    if co2['co2'] < 1000:
      log_message = f"CO2900DOWN: 'co2': {co2['co2']} : Temp: {temperature:.1f}C : Hum: {humidity:.1f}% : VPD: {vpd_rounded}"
      logging.info(log_message)
      print(f"'co2': {co2['co2']} : Temp: {temperature:.1f}C : Hum: {humidity:.1f}% : VPD: {vpd_rounded}")
      GPIO.output(relay_pin, GPIO.HIGH)
      GPIO.output(relay_pin_abluft, GPIO.LOW)
    else:
      log_message = f"CO2900UP: 'co2': {co2['co2']} : Temp: {temperature:.1f}C : Hum: {humidity:.1f}% : VPD: {vpd_rounded}"
      logging.info(log_message)
      print(f"'co2': {co2['co2']} : Temp: {temperature:.1f}C : Hum: {humidity:.1f}% : VPD: {vpd_rounded}")
      GPIO.output(relay_pin, GPIO.HIGH)
      GPIO.output(relay_pin_abluft, GPIO.LOW)

    data = f'''
    # TYPE temperature gauge
    greenbox_temperature {temperature}
    # TYPE humidity gauge
    greenbox_humidity {humidity}
    # TYPE VPD gauge
    greenbox_vpd {vpd_rounded}
    # TYPE CO2 gauge
    greebox_co2 {co2['co2']}
    '''

    # Sende die Daten an den Pushgateway
    try:
      response = requests.post(PUSHGATEWAY_URL, data=data)
      print(f'Response Code: {response.status_code}')
      print('Response Content:', response.text)
    except Exception as e:
      print('Fehler beim Senden der Daten:', str(e))

    # VPD-Range-Message im oberen Balken
    draw.text((5, 1), f'{co2}', font=font, fill=255)  # Text in den oberen 15 Pixeln

    # Texte für Temperatur, Luftfeuchtigkeit und VPD-Wert
    if temperature is not None and humidity is not None:
        draw.text((10, bar_height + 2), f'Temp: {temperature:.1f}C', font=font, fill=255)
        draw.text((10, bar_height + 17), f'Hum: {humidity:.1f}%', font=font, fill=255)
        draw.text((10, bar_height + 32), f'VPD: {vpd_rounded}', font=font, fill=255)
    else:
        draw.text((10, bar_height + 5), 'Temp: --.-C', font=font, fill=255)
        draw.text((10, bar_height + 25), 'Hum: --.-%', font=font, fill=255)
        draw.text((10, bar_height + 45), 'Sensor: Fehler', font=font, fill=255)

    # Bild auf das Display laden
    oled.image(image)
    oled.show()

    # Wartezeit
    time.sleep(5)
