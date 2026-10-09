from pathlib import Path

import joblib
import pandas as pd

from flask import Flask, request, jsonify


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_FILE = BASE_DIR / "models" / "house_price_model.joblib"


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD MODEL ONCE
# ============================================================

if not MODEL_FILE.exists():

    raise FileNotFoundError(
        f"Model not found: {MODEL_FILE}. "
        "Run train.py first."
    )


model = joblib.load(MODEL_FILE)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "message": "House Price Prediction API",
        "status": "running"
    })


# ============================================================
# PREDICT
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "JSON data is required"
        }), 400


    # --------------------------------------------------------
    # Get house size
    # --------------------------------------------------------

    if "size" not in data:

        return jsonify({
            "error": "Missing 'size'"
        }), 400


    try:

        size = float(data["size"])

    except (ValueError, TypeError):

        return jsonify({
            "error": "'size' must be a number"
        }), 400


    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    house = pd.DataFrame({
        "Size": [size]
    })


    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    prediction = model.predict(house)

    predicted_price = float(prediction[0])


    # --------------------------------------------------------
    # Return JSON
    # --------------------------------------------------------

    return jsonify({

        "size_sqft": size,

        "predicted_price_kes":
            round(predicted_price, 2)

    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=7000,
        debug=True
    )