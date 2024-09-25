import RPi.GPIO as GPIO

# Setze den Modus für die GPIO-Pin-Nummerierung
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Liste aller GPIO-Pins, die ausgelesen werden sollen
# Pin 9 Abluft (PrimaKlima)
# Pin 10 CO2 Flasche
gpio_pins = [9, 10]

# Setze jeden GPIO-Pin auf INPUT
for pin in gpio_pins:
  GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in gpio_pins:
    GPIO.setup(pin, GPIO.IN)
    initial_status = GPIO.input(pin)
    print(f"Initial status of GPIO {pin}: {'HIGH' if initial_status == GPIO.HIGH else 'LOW'}")

# Funktion zum Auslesen des GPIO-Status
def read_gpio_status():
    gpio_status = {}
    for pin in gpio_pins:
        status = GPIO.input(pin)  # Liest den Status des Pins (HIGH oder LOW)
        gpio_status[pin] = 'OFF [HIGH]' if status == GPIO.HIGH else 'ON'
    return gpio_status

gpio_status = read_gpio_status()
print("GPIO Status:")
for pin, status in gpio_status.items():
  print(f"GPIO Pin {pin}: {status}")
