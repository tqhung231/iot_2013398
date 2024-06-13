import os

import joblib
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score


class WateringPredictionModel:
    def __init__(self, model_path, scaler_path):
        # Load the trained model
        self.model = tf.keras.models.load_model(model_path)

        # Load the scaler
        self.scaler = joblib.load(scaler_path)

    def preprocess_and_predict(self, input_data):
        """
        Preprocess the input data and make a prediction using the trained model.
        :param input_data: A dictionary with keys "Soil Moisture", "Temperature", and "Soil Humidity".
        :return: A prediction where 1 indicates "ON" and 0 indicates "OFF".
        """
        # Convert input data to a DataFrame
        input_df = pd.DataFrame([input_data])

        # Standardize the feature columns using the loaded scaler
        input_scaled = self.scaler.transform(input_df)

        # Make a prediction using the trained model
        prediction = self.model.predict(input_scaled)

        # Convert prediction to a binary value (1 or 0)
        binary_prediction = 1 if prediction[0] >= 0.5 else 0

        return binary_prediction

    def evaluate_model(self, X, y):
        """
        Evaluate the model on a given dataset.
        :param X: Features of the dataset.
        :param y: True labels of the dataset.
        :return: Accuracy of the model on the dataset.
        """
        # Standardize the feature columns
        X_scaled = self.scaler.transform(X)

        # Make predictions on the entire dataset
        predictions = self.model.predict(X_scaled)

        # Convert predictions to binary values (1 or 0)
        binary_predictions = [1 if pred >= 0.5 else 0 for pred in predictions]

        # Calculate accuracy
        accuracy = accuracy_score(y, binary_predictions)

        return accuracy


# Example usage
if __name__ == "__main__":
    # Define the directory where the model and scaler are saved
    dir = os.path.dirname(__file__)
    model_path = os.path.join(dir, "watering_prediction_model.h5")
    scaler_path = os.path.join(dir, "scaler.pkl")

    # Load the dataset
    file_path = os.path.join(dir, "tarp.csv")
    df = pd.read_csv(file_path)

    # Preprocess the data
    X = df[["Soil Moisture", "Temperature", "Soil Humidity"]]
    y = df["Status"].apply(lambda x: 1 if x == "ON" else 0)  # Convert status to binary

    # Initialize the prediction model
    model = WateringPredictionModel(model_path, scaler_path)

    # Calculate accuracy on the entire dataset
    accuracy = model.evaluate_model(X, y)

    # Print the accuracy
    print(f"Test Accuracy: {accuracy}")

    # Predict for a single input
    input_data = {"Soil Moisture": 30, "Temperature": 22, "Soil Humidity": 55}
    prediction = model.preprocess_and_predict(input_data)
    status = "ON" if prediction == 1 else "OFF"
    print(f"Prediction: {status}")
