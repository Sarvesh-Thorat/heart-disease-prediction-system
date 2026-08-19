import joblib
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "heart_disease.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)


X = df.drop(columns=["target"])
y = df["target"]

print(X.columns)
print("Number of features:", len(X.columns))
print(df.shape)

raw_feature_columns = X.columns.tolist()
joblib.dump(raw_feature_columns, MODEL_DIR / "raw_feature_columns.pkl")

categorical_cols = X.select_dtypes(include=["object", "category", "string"]).columns.tolist()
if categorical_cols:
    X = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

encoded_feature_columns = X.columns.tolist()
joblib.dump(encoded_feature_columns, MODEL_DIR / "encoded_feature_columns.pkl")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
print("Scaler saved successfully.")

lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)

lr_prediction = lr_model.predict(X_test)
lr_accuracy = accuracy_score(y_test, lr_prediction)

print("Logistic Regression Accuracy:", lr_accuracy)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

rf_prediction = rf_model.predict(X_test)
rf_accuracy = accuracy_score(y_test, rf_prediction)

print("Random Forest Accuracy:", rf_accuracy)

if rf_accuracy > lr_accuracy:
    best_model = rf_model
    print("Best Model: Random Forest")
else:
    best_model = lr_model
    print("Best Model: Logistic Regression")

joblib.dump(best_model, MODEL_DIR / "heart_model.pkl")
print("Model Saved Successfully!")


from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score
)


y_pred = best_model.predict(X_test)

print("\nModel Evaluation")

print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("F1 Score :", f1_score(y_test, y_pred))

print("\nClassification Report")
print(classification_report(y_test, y_pred))

cm = confusion_matrix(y_test, y_pred)

print("\nConfusion Matrix")
print(cm)

