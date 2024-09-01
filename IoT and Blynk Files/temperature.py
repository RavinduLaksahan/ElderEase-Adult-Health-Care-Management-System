import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import requests
import tensorflow as tf
import numpy as np
from math import log

# Blynk authentication token
BLYNK_AUTH = 'uEjWstrat9Hr-ljlQ314yJ09YUSNS_c5'
BLYNK_URL_BASE = f'https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&'

# Initialize I2C bus and ADS1015 ADC
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

# Constants for NTC Thermistor calculation
R0 = 10000  # Resistance at 25 degrees C (10k ohms)
B = 3950    # Beta coefficient
T0 = 298.15 # Temperature in Kelvin at 25 degrees C (25 + 273.15)

# Load the pre-trained model
model = tf.keras.models.load_model('human_vital_signs_model.h5')

def get_temperature():
    Vout = chan.voltage
    Rt = R0 * (3.3 / Vout - 1)
    temperature_K = 1 / (1/T0 + log(Rt / R0) / B)
    temperature_C = temperature_K - 273.15
    return temperature_C

def get_blynk_value(pin):
    url = f"{BLYNK_URL_BASE}{pin}"
    response = requests.get(url)
    if response.status_code == 200:
        return float(response.text)
    else:
        print(f"Failed to retrieve value from {pin}. Status code: {response.status_code}")
        return None

while True:
    # Get temperature data from the sensor
    temperature = get_temperature()
    print(f"Body Temperature: {temperature:.2f} C")

    # Send temperature to Blynk
    requests.get(f'https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH}&v0={temperature}')

    # Retrieve data from Blynk
    heart_rate = get_blynk_value('v1')
    oxygen_saturation = get_blynk_value('v2')
    age = get_blynk_value('v5')
    gender = get_blynk_value('v4')  # 0 for Male, 1 for Female
    weight = get_blynk_value('v7')
    height = get_blynk_value('v6')

    if None not in (heart_rate, oxygen_saturation, age, gender, weight, height):
        derived_bmi = weight / (height ** 2)
        print(f"Derived BMI: {derived_bmi:.2f}")

        # Prepare the data for the model (reshape as the model expects a batch of inputs)
        input_data = np.array([[heart_rate, temperature, oxygen_saturation, age, gender, weight, height, derived_bmi]])
        
        # Make prediction
        prediction = model.predict(input_data)
        risk_category = 'High Risk' if prediction[0][0] > 0.5 else 'Low Risk'

        # Send the Risk Category to Blynk
        requests.get(f'https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH}&v8={risk_category}')
        print(f"Risk Category sent successfully: {risk_category} to v8")

    time.sleep(5)  # Pause for 5 seconds before the next reading
