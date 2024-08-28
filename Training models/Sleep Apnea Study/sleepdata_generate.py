import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of rows
num_rows = 200000

# Generate data
total_sleep_duration = np.random.randint(300, 481, num_rows)  # 300 to 480 minutes
rem_sleep_duration = np.random.randint(90, 181, num_rows)     # 90 to 180 minutes
deep_sleep_duration = np.random.randint(60, 121, num_rows)    # 60 to 120 minutes
light_sleep_duration = total_sleep_duration - rem_sleep_duration - deep_sleep_duration

# Ensure light sleep duration is non-negative
light_sleep_duration = np.clip(light_sleep_duration, 120, 300)

room_temperature = np.random.uniform(18, 24, num_rows)        # 18 to 24 °C
age = np.random.randint(18, 81, num_rows)                     # 18 to 80 years
gender = np.random.choice(['Male', 'Female'], num_rows)       # Random gender
height = np.random.uniform(1.5, 2.0, num_rows)                # 1.5 to 2.0 meters
weight = np.random.uniform(50, 120, num_rows)                  # 50 to 120 kg
bmi = weight / (height ** 2)                                   # BMI calculation

# Randomly assign anomaly types
anomaly_types = np.random.choice(
    ['PLMD', 'RLS', 'RBD', 'OSA'], num_rows, p=[0.25, 0.25, 0.25, 0.25]
)

# Create DataFrame
data = pd.DataFrame({
    'Total Sleep Duration (minutes)': total_sleep_duration,
    'REM Sleep Duration (minutes)': rem_sleep_duration,
    'Deep Sleep Duration (minutes)': deep_sleep_duration,
    'Light Sleep Duration (minutes)': light_sleep_duration,
    'Room Temperature (°C)': room_temperature,
    'Age (years)': age,
    'Gender': gender,
    'Height (meters)': height,
    'Weight (kg)': weight,
    'BMI': bmi,
    'Anomaly Type': anomaly_types
})

# Save to CSV
data.to_csv('simulated_sleep_data.csv', index=False)

print("Dataset generated successfully!")
