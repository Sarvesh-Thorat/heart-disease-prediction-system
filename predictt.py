import joblib
import numpy as np

# Load trained model and scaler
model = joblib.load("model/heart_model.pkl")
scaler = joblib.load("model/scaler.pkl")



def predict_heart_disease(patient_data):

    # Convert input to NumPy array
    patient_data = np.array(patient_data).reshape(1, -1)

    # Scale input data
    patient_data = scaler.transform(patient_data)

    # Prediction
    prediction = model.predict(patient_data)[0]

    # Probability
    probability = model.predict_proba(patient_data)[0][1] * 100

    # Risk Level
    if probability < 30:
        risk_level = "Low"
    elif probability < 70:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Result
    result = {
        "Prediction": "Heart Disease" if prediction == 1 else "No Heart Disease",
        "Probability": round(probability, 2),
        "Risk Level": risk_level
    }

    return result


# -------------------------------
# Test the Prediction Module
# -------------------------------

sample_patient = [
    52,     # age
    1,      # sex
    0,      # cp
    125,    # trestbps
    212,    # chol
    0,      # fbs
    1,      # restecg
    168,    # thalach
    0,      # exang
    1.0,    # oldpeak
    2,      # slope
    0,      # ca
    2       # thal
]

result = predict_heart_disease(sample_patient)

print("Prediction :", result["Prediction"])
print("Probability:", result["Probability"], "%")
print("Risk Level :", result["Risk Level"])