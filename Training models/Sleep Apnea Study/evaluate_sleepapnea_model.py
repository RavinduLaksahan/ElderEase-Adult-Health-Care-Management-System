import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

# 1. Load the model
model = load_model('sleep_disorder_model.h5')

# 2. Preprocess the input data
# Example data: Gender: Female, Age: 40, Sleep Duration: 6.5, BMI Category: Normal, Heart Rate: 80

# Encode 'Gender': Assuming 'Male' = 0, 'Female' = 1
gender_encoder = LabelEncoder()
gender_encoder.fit(['Male', 'Female'])
gender = gender_encoder.transform(['Male'])[0]

# Encode 'BMI Category': Assuming 'Normal' = 0, 'Normal Weight' = 1, 'Overweight' = 2
bmi_category_encoder = LabelEncoder()
bmi_category_encoder.fit(['Normal', 'Normal Weight', 'Overweight'])
bmi_category = bmi_category_encoder.transform(['Normal Weight'])[0]

# Create the input array
data = np.array([[gender, 50, 6.5, bmi_category, 65]])

# 3. Make a prediction
prediction = model.predict(data)

# Convert the prediction to a readable format, assuming model outputs probabilities
predicted_class = np.argmax(prediction, axis=1)

# 4. Print the predicted sleep disorder category
# Assuming the sleep disorder categories are encoded as: 'Healthy' = 0, 'Sleep Apnea' = 1, 'Insomnia' = 2
sleep_disorder_classes = ['Healthy', 'Sleep Apnea', 'Insomnia']
print("Predicted Sleep Disorder:", sleep_disorder_classes[predicted_class[0]])
