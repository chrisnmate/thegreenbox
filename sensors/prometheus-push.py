from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Sensordaten (Beispieldaten)
co2_value = 640
temperature = 22.5
humidity = 62.4
vpd = 0.71

# Prometheus Registry und Metriken erstellen
registry = CollectorRegistry()

co2_gauge = Gauge('sensor_co2', 'CO2-Wert', registry=registry)
temp_gauge = Gauge('sensor_temperature', 'Temperatur in Celsius', registry=registry)
hum_gauge = Gauge('sensor_humidity', 'Luftfeuchtigkeit in Prozent', registry=registry)
vpd_gauge = Gauge('sensor_vpd', 'VPD-Wert', registry=registry)

# Werte aktualisieren
co2_gauge.set(co2_value)
temp_gauge.set(temperature)
hum_gauge.set(humidity)
vpd_gauge.set(vpd)

# Daten an das Push Gateway senden
push_to_gateway('localhost:9091', job='sensor_job', registry=registry)
