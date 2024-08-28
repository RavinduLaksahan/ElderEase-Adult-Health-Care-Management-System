import max30102
import hrcalc
import time
import requests
import numpy as np

# Blynk authentication token
BLYNK_AUTH = 'uEjWstrat9Hr-ljlQ314yJ09YUSNS_c5'  # Replace with your Auth Token
BLYNK_URL = f'https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH}'

# Initialize the MAX30102 sensor
m = max30102.MAX30102()

hr2 = 0
sp2 = 0

# Parameters for exponential moving average
alpha = 0.2  # Smoothing factor, 0 < alpha <= 1 (smaller alpha means smoother)
hr_ema = None
sp_ema = None

# Parameters for adaptive window size
min_window_size = 3
max_window_size = 8

# Initial warm-up period and reading collection
warm_up_period = 10  # seconds
warm_up_end_time = time.time() + warm_up_period
hr_readings = []
sp_readings = []

def adaptive_window_size(data, min_size, max_size, threshold=10):
    variance = np.var(data)
    if variance > threshold:
        return min(max_size, max_size)
    return min(max(min_size, min_size + int(variance)))

def is_valid_reading(value, min_val, max_val):
    return min_val <= value <= max_val

while True:
    # Read data from the sensor
    red, ir = m.read_sequential()
    
    # Calculate heart rate and SpO2
    hr, hrb, sp, spb = hrcalc.calc_hr_and_spo2(ir, red)
    
    if time.time() < warm_up_end_time:
        # During the warm-up period, collect initial readings
        if hrb and hr != -999 and is_valid_reading(hr, 50, 180):
            hr_readings.append(hr)
        if spb and sp != -999 and is_valid_reading(sp, 80, 100):
            sp_readings.append(sp)
    else:
        # After warm-up, use the average of initial readings for stability
        if hr_readings:
            hr2 = int(np.mean(hr_readings))
        if sp_readings:
            sp2 = int(np.mean(sp_readings))
        
        if hrb and hr != -999 and is_valid_reading(hr, 50, 180):
            hr2 = int(hr)
            if hr_ema is None:
                hr_ema = hr2
            else:
                hr_ema = alpha * hr2 + (1 - alpha) * hr_ema
            
            print("Heart Rate (EMA): ", int(hr_ema))
            
            # Send heart rate to Blynk
            response_hr = requests.get(f"{BLYNK_URL}&v1={int(hr_ema)}")
            if response_hr.status_code == 200:
                print(f"Heart Rate sent successfully: {int(hr_ema)} BPM")
            else:
                print(f"Failed to send Heart Rate. Status code: {response_hr.status_code}")
        
        if spb and sp != -999 and is_valid_reading(sp, 80, 100):
            sp2 = int(sp)
            if sp_ema is None:
                sp_ema = sp2
            else:
                sp_ema = alpha * sp2 + (1 - alpha) * sp_ema
            
            print("SPO2 (EMA)       : ", int(sp_ema))
            
            # Send SpO2 to Blynk
            response_spo2 = requests.get(f"{BLYNK_URL}&v2={int(sp_ema)}")
            if response_spo2.status_code == 200:
                print(f"SpO2 sent successfully: {int(sp_ema)}%")
            else:
                print(f"Failed to send SpO2. Status code: {response_spo2.status_code}")
    
    # Adjust delay for more stable readings
    time.sleep(0.5)
