import sys
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

sys.path.insert(0, "backend")

from ml.deployment_preprocessing import prepare_for_model


candidate_data_files = [
    "./data/telecom_churn_100k.csv",
    "./backend/ml/data/dataset.csv",
    os.path.join(os.path.dirname(__file__), "backend", "ml", "data", "dataset.csv"),
]

DATA_FILE = None
for path in candidate_data_files:
    if os.path.exists(path):
        DATA_FILE = path
        break

if not DATA_FILE:
    raise FileNotFoundError(f"Could not find dataset in any of: {candidate_data_files}")

MODEL_FILE = os.path.join(os.path.dirname(__file__), "backend", "models", "logistic_regression_100k.joblib")


print(f"Loading dataset from {DATA_FILE}...")

df = pd.read_csv(DATA_FILE)

print("Dataset:", df.shape)


# ============================================================
# TARGET
# Dataset uses:
# 0 = No Churn
# 1 = Churn
# ============================================================

y = pd.to_numeric(
    df["Churn"],
    errors="coerce",
).astype("int")


if not set(y.unique()).issubset({0, 1}):
    raise ValueError(
        f"Unexpected Churn values: {sorted(y.unique())}"
    )


print()
print("Churn distribution:")
print(y.value_counts().sort_index())


# ============================================================
# FEATURES
# ============================================================

X = prepare_for_model(df)

print()
print("Model input:", X.shape)
print("Features:", len(X.columns))


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print()
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ============================================================
# LOGISTIC REGRESSION
# ============================================================

model = LogisticRegression(
    max_iter=2000,
    random_state=42,
)

print()
print("Training Logistic Regression...")

model.fit(
    X_train,
    y_train,
)


# ============================================================
# PREDICTION
# ============================================================

predictions = model.predict(X_test)

probabilities = model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions,
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0,
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0,
)

roc_auc = roc_auc_score(
    y_test,
    probabilities,
)

cm = confusion_matrix(
    y_test,
    predictions,
)


# ============================================================
# RESULTS
# ============================================================

print()
print("========================================")
print("       LOGISTIC REGRESSION RESULTS")
print("========================================")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")

print()
print("Confusion Matrix:")
print(cm)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_FILE),
    exist_ok=True,
)

joblib.dump(
    model,
    MODEL_FILE,
)

print()
print("========================================")
print("MODEL SAVED")
print("========================================")

print(MODEL_FILE)