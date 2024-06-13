import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

dir = os.path.dirname(__file__)
# Load the dataset
file_path = os.path.join(dir, "fertilizer.csv")
df = pd.read_csv(file_path)

# Preprocess the data
# Convert categorical columns to numerical
soil_type_encoder = LabelEncoder()
df["Soil Type"] = soil_type_encoder.fit_transform(df["Soil Type"])

crop_type_encoder = LabelEncoder()
df["Crop Type"] = crop_type_encoder.fit_transform(df["Crop Type"])

fertilizer_encoder = LabelEncoder()
df["Fertilizer Name"] = fertilizer_encoder.fit_transform(df["Fertilizer Name"])

# Separate features and target
X = df.drop(columns=["Fertilizer Name"])
y = df["Fertilizer Name"]

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standardize the feature columns
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Build the TensorFlow model
model = tf.keras.models.Sequential(
    [
        tf.keras.layers.Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(
            len(np.unique(y)), activation="softmax"
        ),  # Output layer for classification
    ]
)

# Compile the model
model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

# Early stopping callback
early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=10, restore_best_weights=True
)

# Train the model
history = model.fit(
    X_train,
    y_train,
    epochs=1000000,
    validation_split=0.2,
    batch_size=100,
    callbacks=[early_stopping],
)

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)

print(f"Test Accuracy: {test_acc}")

# Save the model
model.save(os.path.join(dir, "fertilizer_prediction_model.h5"))

# Save encoders and scaler
import joblib

joblib.dump(soil_type_encoder, os.path.join(dir, "soil_type_encoder.pkl"))
joblib.dump(crop_type_encoder, os.path.join(dir, "crop_type_encoder.pkl"))
joblib.dump(fertilizer_encoder, os.path.join(dir, "fertilizer_encoder.pkl"))
joblib.dump(scaler, os.path.join(dir, "scaler.pkl"))

# Plot and save the training history
plt.figure(figsize=(10, 6))
plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.legend()
plt.title("Training and Validation Loss Over Epochs")
plt.savefig(os.path.join(dir, "training_history.png"))
plt.show()
