import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
DATA_PATH = BASE_DIR / "heart_disease.csv"

# Load trained model and scaler
model = joblib.load(MODEL_DIR / "heart_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
raw_feature_columns = joblib.load(MODEL_DIR / "raw_feature_columns.pkl")
encoded_feature_columns = joblib.load(MODEL_DIR / "encoded_feature_columns.pkl")

training_df = pd.read_csv(DATA_PATH)
feature_df = training_df.drop(columns=["target"])
categorical_cols = feature_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()


def _prepare_patient_features(patient_data):
    if isinstance(patient_data, dict):
        patient_df = pd.DataFrame([patient_data])
    else:
        patient_df = pd.DataFrame([patient_data], columns=raw_feature_columns)

    patient_df = patient_df.reindex(columns=raw_feature_columns)

    for col in raw_feature_columns:
        if col not in categorical_cols:
            patient_df[col] = pd.to_numeric(patient_df[col], errors="coerce")
        else:
            patient_df[col] = patient_df[col].astype(str)

    encoded_patient = pd.get_dummies(patient_df, columns=categorical_cols, drop_first=True)
    encoded_patient = encoded_patient.reindex(columns=encoded_feature_columns, fill_value=0)
    return encoded_patient


def predict_heart_disease(patient_data):
    prepared_data = _prepare_patient_features(patient_data)
    prepared_data = scaler.transform(prepared_data)

    prediction = model.predict(prepared_data)[0]
    probability = model.predict_proba(prepared_data)[0][1] * 100

    if probability < 30:
        risk_level = "Low"
    elif probability < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "Prediction": "Heart Disease" if prediction == 1 else "No Heart Disease",
        "Probability": round(probability, 2),
        "Risk Level": risk_level,
    }


# -------------------------------
# Test the Prediction Module
# -------------------------------

sample_patient = [
    52,      # age
    "M",     # sex
    "TA",    # chest_pain_type
    125,     # resting_bp
    212,     # cholesterol
    "N",     # fasting_blood_sugar
    "LVH",   # resting_ecg
    168,     # max_hr
    "N",     # exercise_angina
    1.0,     # oldpeak
    "Flat",  # st_slope
    0,       # ca
    "Reversible"  # thal
]

result = predict_heart_disease(sample_patient)

print("Prediction :", result["Prediction"])
print("Probability:", result["Probability"], "%")
print("Risk Level :", result["Risk Level"])