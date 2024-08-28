import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import requests  # Import the requests library
from math import log

# Blynk authentication token
BLYNK_AUTH = 'uEjWstrat9Hr-ljlQ314yJ09YUSNS_c5'  # Replace with your Auth Token
BLYNK_URL = f'https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH}&v0='

# Initialize I2C bus and ADS1015 ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

# Constants for NTC Thermistor calculation
R0 = 10000  # Resistance at 25 degrees C (10k ohms)
B = 3950    # Beta coefficient
T0 = 298.15 # Temperature in Kelvin at 25 degrees C (25 + 273.15)

def get_temperature():
    # Read voltage from the voltage divider
    Vout = chan.voltage
    # Calculate the resistance of the thermistor
    Rt = R0 * (3.3 / Vout - 1)
    # Calculate the temperature in Kelvin
    temperature_K = 1 / (1/T0 + log(Rt / R0) / B)
    # Convert Kelvin to Celsius
    temperature_C = temperature_K - 273.15
    return temperature_C

while True:
    # Get temperature data
    temperature = get_temperature()
    print(f"Temperature: {temperature:.2f} C")
    
    # Send temperature to Blynk using HTTP request
    response = requests.get(BLYNK_URL + str(temperature))
    
    if response.status_code == 200:
        print(f"Value sent successfully: {temperature:.2f} to v0")
    else:
        print(f"Failed to send value. Status code: {response.status_code}")

    time.sleep(5)  # Read data every 5 seconds
