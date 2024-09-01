import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

# 1. Load the model
model = load_model('human_vital_signs_model.h5')

# 2. Print the model summary
model.summary()

# Prepare label encoders as they were used during training
label_encoder_gender = LabelEncoder()
label_encoder_gender.fit(['Male', 'Female'])  # Ensure this matches your training labels

# 3. Prepare the single data point for prediction
# Convert Gender from 'Female' to numeric value
gender_encoded = label_encoder_gender.transform(['Male'])[0]
data = np.array([[73, 36, 98.50826478, 40, gender_encoded, 75, 1.8, 18]])

# 4. Make a prediction
prediction = model.predict(data)

# Convert the prediction to a readable format, if necessary
# Assuming the model outputs probabilities and you need the class with the highest probability
predicted_class = np.argmax(prediction, axis=1)

# Print the predicted risk category
print("Predicted Risk Category:", "High Risk" if predicted_class == 1 else "Low Risk")

# If you have a test dataset and want to evaluate:
# test_loss, test_accuracy = model.evaluate(X_test, y_test)
# print(f"Test Accuracy: {test_accuracy * 100:.2f}%")
