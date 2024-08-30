import time
import board
import busio
import adafruit_mpu6050
import blynklib
import numpy as np
import requests

# Blynk authentication token
BLYNK_AUTH = 'uEjWstrat9Hr-ljlQ314yJ09YUSNS_c5' 
BLYNK_URL = f'https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH}'

# Initialize Blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

# Initialize I2C bus and MPU6050
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_mpu6050.MPU6050(i2c)

# Constants
CALIBRATION_PERIOD = 10  # Calibration period in seconds
LOW_MOVEMENT_TIME = 10  # Time in seconds for low movement to indicate sleep
SLEEP_DATA_PIN = 3  # Virtual pin for sending sleep data to Blynk

# Calibration data
calibration_data = []
is_sleeping = False
sleep_start_time = None

# Function to calibrate sensor
def calibrate_sensor():
    print("Calibrating sensor...")
    for _ in range(CALIBRATION_PERIOD * 10):  # Collect data over the calibration period
        accel = sensor.acceleration
        calibration_data.append(accel)
        time.sleep(0.1)  # Collect data every 0.1 seconds
    return np.mean(calibration_data, axis=0)

# Function to detect movement
def is_moving(current_accel, baseline, threshold):
    return any(abs(current - baseline_val) > threshold for current, baseline_val in zip(current_accel, baseline))

# Calibrate the sensor and get baseline readings
baseline = calibrate_sensor()

while True:
    # Read acceleration data
    current_accel = sensor.acceleration

    # Calculate the dynamic threshold based on the current baseline
    threshold = np.mean(baseline) + 0.1  # Adjust as needed

    # Check for movement
    if is_moving(current_accel, baseline, threshold):
        print("Movement detected")
        is_sleeping = False
        sleep_start_time = None

        # Send "Person is Awake" message to Blynk via HTTP request
        response = requests.get(f"{BLYNK_URL}&v{SLEEP_DATA_PIN}=Person is Awake")
        if response.status_code == 200:
            print("Person is Awake status sent successfully")
        else:
            print(f"Failed to send status: {response.status_code}")

    else:
        print("Low movement detected")
        if not is_sleeping:
            # Check if low movement duration is sufficient to determine sleep
            if sleep_start_time is None:
                sleep_start_time = time.time()  # Mark the start of low movement
            elif time.time() - sleep_start_time >= LOW_MOVEMENT_TIME:
                is_sleeping = True
                print("Person is sleeping")

                # Send "Person is Sleeping" message to Blynk via HTTP request
                response = requests.get(f"{BLYNK_URL}&v{SLEEP_DATA_PIN}=Person is Sleeping")
                if response.status_code == 200:
                    print("Person is Sleeping status sent successfully")
                else:
                    print(f"Failed to send status: {response.status_code}")

        else:
            # If still sleeping, keep sending the sleeping status
            response = requests.get(f"{BLYNK_URL}&v{SLEEP_DATA_PIN}=Person is Sleeping")
            if response.status_code == 200:
                print("Person is Sleeping status sent successfully")
            else:
                print(f"Failed to send status: {response.status_code}")

    # Run Blynk's event loop
    blynk.run()
    
    # Small delay to prevent overwhelming the sensor
    time.sleep(0.5)  # Check every half second
