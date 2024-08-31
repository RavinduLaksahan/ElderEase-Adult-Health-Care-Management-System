import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report

# Load the dataset
data = pd.read_csv('human_vital_signs_dataset.csv')

# Preprocess the data
data.dropna(inplace=True)  # Remove missing values

# Encode categorical variables (Gender and Risk Category)
label_encoder_gender = LabelEncoder()
data['Gender'] = label_encoder_gender.fit_transform(data['Gender'])

label_encoder_risk = LabelEncoder()
data['Risk Category'] = label_encoder_risk.fit_transform(data['Risk Category'])  # High Risk: 0, Low Risk: 1

# Split the dataset into features and target
X = data[['Heart Rate', 'Body Temperature', 'Oxygen Saturation', 'Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Derived_BMI']].values
y = data['Risk Category'].values

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(2, activation='softmax')  # 2 output classes (High Risk and Low Risk)
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print("Test Accuracy:", test_accuracy)

# Make predictions on test data
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)

# Confusion Matrix and Classification Report
cm = confusion_matrix(y_test, y_pred_classes)
print("Confusion Matrix:\n", cm)
print("\nClassification Report:\n", classification_report(y_test, y_pred_classes))

# Plot accuracy graph
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(loc='upper left')
plt.show()

# Save the model
model.save('human_vital_signs_model.h5')
