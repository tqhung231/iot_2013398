import os

import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

dir = os.path.dirname(__file__)
# Load the dataset
file_path = os.path.join(dir, "tarp.csv")
df = pd.read_csv(file_path)

# Preprocess the data
X = df[["Soil Moisture", "Temperature", "Soil Humidity"]]
y = df["Status"].apply(lambda x: 1 if x == "ON" else 0)  # Convert status to binary

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standardize the feature columns
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Build the TensorFlow model
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64, activation="relu", input_shape=(3,)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

# Compile the model with AdamW optimizer
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

# Set up early stopping
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=20, restore_best_weights=True
)


# Train the model
history = model.fit(
    X_train,
    y_train,
    epochs=1000000,
    validation_split=0.2,
    batch_size=1000,
    callbacks=[early_stopping],
)

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)

print(f"Test Accuracy: {test_acc}")

# Save the model
model.save(os.path.join(dir, "watering_prediction_model.h5"))

# Save encoders and scaler
import joblib

joblib.dump(scaler, os.path.join(dir, "scaler.pkl"))

# Plot and save the training history for loss
plt.figure(figsize=(10, 6))
plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.title("Training and Validation Loss Over Epochs")
plt.savefig("training_loss_history.png")
plt.show()

# Plot and save the training history for accuracy
plt.figure(figsize=(10, 6))
plt.plot(history.history["accuracy"], label="Training Accuracy")
plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.title("Training and Validation Accuracy Over Epochs")
plt.savefig("training_accuracy_history.png")
plt.show()
