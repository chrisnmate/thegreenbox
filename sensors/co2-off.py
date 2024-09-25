import RPi.GPIO as GPIO
import time

# GPIO-Modus (Broadcom-Nummerierung verwenden)
GPIO.setmode(GPIO.BCM)

# Pin definieren, an dem das Relay angeschlossen ist
relay_pin = 10  # GPIO 17 (Pin 11 auf dem Board)

# GPIO-Pin als Ausgang definieren
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, GPIO.HIGH)
print("Relay AN [abluft]")
