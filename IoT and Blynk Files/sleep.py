import time
import board
import busio
import adafruit_mpu6050
import blynklib
import numpy as np
import requests
import tensorflow as tf

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
HR_DATA_PIN = 1  # Virtual pin for retrieving heart rate from Blynk

# Calibration data
calibration_data = []
is_sleeping = False
sleep_start_time = None
last_movement_time = None
sleep_duration_hours = 0
heart_rate_readings = []  # Array to store heart rate readings

model = tf.keras.models.load_model('sleep_disorder_model.h5')

# Function to retrieve user data from Blynk and calculate BMI
def get_user_data_and_calculate_bmi():
    # Retrieve data from Blynk using HTTP GET requests
    age_response = requests.get(f'https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&v5')
    gender_response = requests.get(f'https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&v4')
    weight_response = requests.get(f'https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&v7')
    height_response = requests.get(f'https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&v6')

    # Check if all requests were successful
    if age_response.status_code == 200 and gender_response.status_code == 200 and weight_response.status_code == 200 and height_response.status_code == 200:
        age = int(age_response.json())
        gender = 'Male' if int(gender_response.json()) == 0 else 'Female'
        weight = float(weight_response.json())
        height = float(height_response.json())

        # Calculate BMI
        bmi = weight / (height ** 2)

        # Determine BMI category
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 24.9:
            bmi_category = "Normal"
        elif 24.9 <= bmi < 29.9:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

        # Store the data in variables
        global user_age, user_gender, user_weight, user_height, user_bmi, user_bmi_category
        user_age = age
        user_gender = gender
        user_weight = weight
        user_height = height
        user_bmi = bmi
        user_bmi_category = bmi_category

    else:
        print("Failed to retrieve one or more values from Blynk")
        return None

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

# Function to retrieve heart rate from Blynk
def get_heart_rate():
    response = requests.get(f'https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&v{HR_DATA_PIN}')
    if response.status_code == 200:
        heart_rate = response.json()  # Assuming the response is a list with the heart rate
        return heart_rate
    else:
        print(f"Failed to retrieve heart rate. Status code: {response.status_code}")
        return None

# Calibrate the sensor and get baseline readings
accel_baseline, gyro_baseline = calibrate_sensor()

while True:
    # Get user data and calculate BMI
    get_user_data_and_calculate_bmi()

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
            average_hr = np.mean(heart_rate_readings) if heart_rate_readings else 0
            print(f"Sleep Duration: {sleep_duration_hours:.2f} hours")
            print(f"Average Heart Rate during sleep: {average_hr:.2f} BPM")
            is_sleeping = False
            sleep_start_time = None
            heart_rate_readings.clear()  # Clear readings after waking up

            # Prepare data for model prediction
            # Convert categorical variables to appropriate numerical values
            gender_numeric = 0 if user_gender == 'Male' else 1
            bmi_category_numeric = {"Underweight": 0, "Normal": 1, "Overweight": 2, "Obese": 3}
            input_data = np.array([[gender_numeric, user_age, sleep_duration_hours, bmi_category_numeric[user_bmi_category], average_hr]])

            # Make prediction
            prediction = model.predict(input_data)

            # Determine the sleep disorder based on model predictions
            if prediction[0][0] > 0.5:  # Sleep Apnea
                sleep_disorder = 'Sleep Apnea'
            elif prediction[0][1] > 0.5:  # Insomnia
                sleep_disorder = 'Insomnia'
            else:  # Healthy
                sleep_disorder = 'Healthy'
            
            # Send the sleep disorder prediction to Blynk via virtual pin V9
            requests.get(f'https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH}&v9={sleep_disorder}')
            print(f"Sleep disorder prediction sent: {sleep_disorder} to v9")

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
            # If still sleeping, keep sending the sleeping status and collect heart rate
            heart_rate = get_heart_rate()
            if heart_rate is not None:
                heart_rate_readings.append(heart_rate)  # Store heart rate reading
            response = requests.get(f"{BLYNK_URL}&v{SLEEP_DATA_PIN}=Person is Sleeping")
            if response.status_code == 200:
                print("Person is Sleeping status sent successfully")
            else:
                print(f"Failed to send status: {response.status_code}")

    # Run Blynk's event loop
    blynk.run()
    
    # Small delay to prevent overwhelming the sensor
    time.sleep(0.5)  # Check every half second
