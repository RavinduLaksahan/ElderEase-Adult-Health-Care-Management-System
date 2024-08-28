import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic test dataset
num_samples = 100  # Number of samples

synthetic_test_data = pd.DataFrame({
    'Heart Rate': np.random.randint(60, 100, size=num_samples),  # Sample heart rates between 60 and 100
    'Body Temperature': np.round(np.random.uniform(36.0, 38.0, size=num_samples), 1),  # Sample body temperatures between 36.0 and 38.0
    'Oxygen Saturation': np.random.randint(85, 100, size=num_samples),  # Sample SpO2 levels between 85 and 100
    'Age': np.random.randint(18, 80, size=num_samples),  # Sample ages between 18 and 80
    'Gender': np.random.choice(['Male', 'Female'], size=num_samples),  # Randomly choose Male or Female
    'Weight (kg)': np.random.randint(50, 120, size=num_samples),  # Sample weights between 50 and 120 kg
    'Height (m)': np.round(np.random.uniform(1.5, 2.0, size=num_samples), 2),  # Sample heights between 1.5m and 2.0m
    'Derived_BMI': np.round(np.random.uniform(18.5, 35.0, size=num_samples), 1),  # Sample BMIs between 18.5 and 35.0
})
# Assign Risk Category based on a simple heuristic
risk_categories = []
for i in range(num_samples):
    if synthetic_test_data['Heart Rate'].iloc[i] > 90 or synthetic_test_data['Oxygen Saturation'].iloc[i] < 90:
        risk_categories.append('High Risk')
    else:
        risk_categories.append('Low Risk')

synthetic_test_data['Risk Category'] = risk_categories

# Save to CSV
synthetic_test_data.to_csv('synthetic_test_data.csv', index=False)

print("Synthetic test data created and saved to 'synthetic_test_data.csv'.")
