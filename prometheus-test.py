import requests
import time

# Pushgateway URL
PUSHGATEWAY_URL = 'http://localhost:9091/metrics/job/environment'

# Statische Daten für Temperatur und Luftfeuchtigkeit
temperature = 22.5  # Temperatur in Grad Celsius
humidity = 60.0     # Luftfeuchtigkeit in Prozent

# Erstelle die Daten im Prometheus-Format
data = f'''
# TYPE temperature gauge
temperature {temperature}
# TYPE humidity gauge
humidity {humidity}
'''

# Sende die Daten an den Pushgateway
response = requests.post(PUSHGATEWAY_URL, data=data)

# Überprüfe die Antwort
if response.status_code == 202:
    print('Daten erfolgreich an den Pushgateway gesendet!')
else:
    print(f'Fehler beim Senden der Daten: {response.status_code}')
