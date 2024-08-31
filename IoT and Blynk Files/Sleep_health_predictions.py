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
SUSTAINED_MOVEMENT_TIME = 4  # Time in seconds for sustained movement to indicate waking up
SLEEP_DATA_PIN = 3  # Virtual pin for sending sleep data to Blynk

# Calibration data
calibration_data = []
is_sleeping = False
sleep_start_time = None
last_movement_time = None
sleep_duration_hours = 0

# Function to calibrate sensor
def calibrate_sensor():
    print("Calibrating sensor...")
    for _ in range(CALIBRATION_PERIOD * 10):  # Collect data over the calibration period
        accel = sensor.acceleration
        gyro = sensor.gyro
        calibration_data.append((accel, gyro))
        time.sleep(0.1)  # Collect data every 0.1 seconds
    accel_baseline = np.mean([data[0] for data in calibration_data], axis=0)
    gyro_baseline = np.mean([data[1] for data in calibration_data], axis=0)
    return accel_baseline, gyro_baseline

# Function to detect movement (now using both accelerometer and gyroscope data)
def is_moving(current_accel, current_gyro, accel_baseline, gyro_baseline, accel_threshold, gyro_threshold):
    accel_movement = any(abs(current - baseline) > accel_threshold for current, baseline in zip(current_accel, accel_baseline))
    gyro_movement = any(abs(current - baseline) > gyro_threshold for current, baseline in zip(current_gyro, gyro_baseline))
    return accel_movement or gyro_movement

# Calibrate the sensor and get baseline readings
accel_baseline, gyro_baseline = calibrate_sensor()

while True:
    # Read acceleration and gyroscope data
    current_accel = sensor.acceleration
    current_gyro = sensor.gyro

    # Calculate the dynamic thresholds based on the current baseline
    accel_threshold = np.mean(accel_baseline) + 0.1 
    gyro_threshold = np.mean(gyro_baseline) + 0.1 

    # Check for movement
    if is_moving(current_accel, current_gyro, accel_baseline, gyro_baseline, accel_threshold, gyro_threshold):
        print("Movement detected")
        last_movement_time = time.time()
        if is_sleeping:
            # Calculate sleep duration before waking up
            sleep_duration_hours = (time.time() - sleep_start_time) / 3600  # Convert to hours
            print(f"Sleep Duration: {sleep_duration_hours:.2f} hours")
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
