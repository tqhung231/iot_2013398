import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score


class FertilizerPredictionModel:
    def __init__(
        self,
        model_path,
        scaler_path,
        soil_type_encoder_path,
        crop_type_encoder_path,
        fertilizer_encoder_path,
    ):
        # Load the trained model
        self.model = tf.keras.models.load_model(model_path)

        # Load the scaler and encoders
        self.scaler = joblib.load(scaler_path)
        self.soil_type_encoder = joblib.load(soil_type_encoder_path)
        self.crop_type_encoder = joblib.load(crop_type_encoder_path)
        self.fertilizer_encoder = joblib.load(fertilizer_encoder_path)

    def preprocess_and_predict(self, input_data):
        """
        Preprocess the input data and make a prediction using the trained model.
        :param input_data: A dictionary with keys "Soil Type", "Crop Type", "Nitrogen", "Phosphorous", "Potassium",
            "Temperature", "Humidity", "Moisture".
        :return: A prediction for the fertilizer name.
        """
        # Encode the categorical features
        input_data["Soil Type"] = self.soil_type_encoder.transform(
            [input_data["Soil Type"]]
        )[0]
        input_data["Crop Type"] = self.crop_type_encoder.transform(
            [input_data["Crop Type"]]
        )[0]

        # Convert input data to a DataFrame
        input_df = pd.DataFrame([input_data])

        # Standardize the feature columns using the loaded scaler
        input_scaled = self.scaler.transform(input_df)

        # Make a prediction using the trained model
        prediction = self.model.predict(input_scaled)

        # Convert prediction to the original label
        predicted_class = np.argmax(prediction, axis=1)[0]
        fertilizer_name = self.fertilizer_encoder.inverse_transform([predicted_class])[
            0
        ]

        return fertilizer_name

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

        # Convert predictions to class labels
        predicted_classes = np.argmax(predictions, axis=1)

        # Calculate accuracy
        accuracy = accuracy_score(y, predicted_classes)

        return accuracy


# Example usage
if __name__ == "__main__":
    # Define the directory where the model and scaler are saved
    dir = os.path.dirname(__file__)
    model_path = os.path.join(dir, "fertilizer_prediction_model.h5")
    scaler_path = os.path.join(dir, "scaler.pkl")
    soil_type_encoder_path = os.path.join(dir, "soil_type_encoder.pkl")
    crop_type_encoder_path = os.path.join(dir, "crop_type_encoder.pkl")
    fertilizer_encoder_path = os.path.join(dir, "fertilizer_encoder.pkl")

    # Initialize the prediction model
    model = FertilizerPredictionModel(
        model_path,
        scaler_path,
        soil_type_encoder_path,
        crop_type_encoder_path,
        fertilizer_encoder_path,
    )

    # Predict for a single input
    input_data = {
        "Temparature": 26,
        "Humidity": 52,
        "Moisture": 38,
        "Soil Type": "Sandy",
        "Crop Type": "Maize",
        "Nitrogen": 37,
        "Potassium": 0,
        "Phosphorous": 0,
    }
    prediction = model.preprocess_and_predict(input_data)
    print(f"Prediction: {prediction}")
