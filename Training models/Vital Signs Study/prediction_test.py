import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

# Load the saved model
model = tf.keras.models.load_model('human_vital_signs_model.h5')  # or use .keras if applicable

# Load the synthetic test dataset
test_data = pd.read_csv('synthetic_test_data.csv')

# Prepare features for prediction
# Convert categorical 'Gender' to numerical
test_data['Gender'] = test_data['Gender'].map({'Male': 0, 'Female': 1})

# Select only the features needed for prediction
X_test = test_data[['Heart Rate', 'Body Temperature', 'Oxygen Saturation', 'Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Derived_BMI']].values

# Make predictions
predictions_prob = model.predict(X_test)
predictions_classes = np.argmax(predictions_prob, axis=1)

# Map numerical predictions back to Risk Category labels
risk_labels = {0: 'Low Risk', 1: 'High Risk'}
predicted_risk = [risk_labels[pred] for pred in predictions_classes]

# Add predictions to the test data DataFrame
test_data['Predicted Risk Category'] = predicted_risk

# Compare predicted vs actual risk categories
print(test_data[['Risk Category', 'Predicted Risk Category']])

# Calculate accuracy
accuracy = np.mean(predicted_risk == test_data['Risk Category'])
print(f'Prediction Accuracy: {accuracy * 100:.2f}%')

# Generate and print classification report
print("\nClassification Report:")
print(classification_report(test_data['Risk Category'], predicted_risk))

# Generate and print confusion matrix
conf_matrix = confusion_matrix(test_data['Risk Category'], predicted_risk)
print("\nConfusion Matrix:")
print(conf_matrix)
