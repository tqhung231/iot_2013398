from flask import Flask, request, jsonify
from flask_cors import CORS
from test import FertilizerPredictionModel

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Load your model here
model = FertilizerPredictionModel(
    model_path="fertilizer_prediction_model.h5",
    scaler_path="scaler.pkl",
    soil_type_encoder_path="soil_type_encoder.pkl",
    crop_type_encoder_path="crop_type_encoder.pkl",
    fertilizer_encoder_path="fertilizer_encoder.pkl",
)


@app.route("/api/predict-fertilizer", methods=["POST"])
def predict_fertilizer():
    data = request.json
    input_data = {
        "Temparature": data["temparature"],
        "Humidity": data["humidity"],
        "Moisture": data["moisture"],
        "Soil Type": data["soilType"],
        "Crop Type": data["cropType"],
        "Nitrogen": data["nitrogen"],
        "Potassium": data["potassium"],
        "Phosphorous": data["phosphorous"],
    }
    prediction = model.preprocess_and_predict(input_data)
    return jsonify({"fertilizer": prediction})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
