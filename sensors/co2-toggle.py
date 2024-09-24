import RPi.GPIO as GPIO
import time

# GPIO-Modus (Broadcom-Nummerierung verwenden)
GPIO.setmode(GPIO.BCM)

# Pin definieren, an dem das Relay angeschlossen ist
relay_pin = 10  # GPIO 17 (Pin 11 auf dem Board)

# GPIO-Pin als Ausgang definieren
GPIO.setup(relay_pin, GPIO.OUT)

try:
    while True:
        # Relay aktivieren (z.B. Lampe einschalten)
        GPIO.output(relay_pin, GPIO.LOW)  # Je nach Relay LOW oder HIGH setzen
        print("Relay AN")
        time.sleep(30)  # Warte 5 Sekunden

        # Relay deaktivieren (z.B. Lampe ausschalten)
        GPIO.output(relay_pin, GPIO.HIGH)
        print("Relay AUS")
        time.sleep(30)  # Warte 5 Sekunden

except KeyboardInterrupt:
    print("Beende das Programm")

finally:
    # Aufräumen
    GPIO.cleanup()
