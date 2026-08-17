from __future__ import annotations

import os
from io import StringIO
from typing import Dict, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
	accuracy_score,
	classification_report,
	confusion_matrix,
	f1_score,
	precision_score,
	recall_score,
	roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from preprocessing import (
	build_preprocessing_pipeline,
	encode_target,
	identify_feature_types,
	load_and_clean_data,
	split_features_target,
)


RANDOM_STATE = 42
TEST_SIZE = 0.2
TARGET_COLUMN = "Churn"
DATA_PATH = "dataset.csv"
OUTPUT_DIR = "artifacts"


def ensure_output_dir(output_dir: str) -> None:
	os.makedirs(output_dir, exist_ok=True)


def perform_eda(df: pd.DataFrame, target_col: str, output_dir: str) -> None:
	print("\n=== DATASET INFO ===")
	buffer = StringIO()
	df.info(buf=buffer)
	print(buffer.getvalue())

	print("\n=== CHURN DISTRIBUTION ===")
	print(df[target_col].value_counts(dropna=False))
	print(df[target_col].value_counts(normalize=True, dropna=False))

	plt.figure(figsize=(7, 5))
	sns.countplot(data=df, x=target_col)
	plt.title("Churn Distribution")
	plt.tight_layout()
	plt.savefig(os.path.join(output_dir, "eda_churn_distribution.png"), dpi=200)
	plt.close()

	if "Contract_Type_Month-to-month" in df.columns:
		contract_cols = [col for col in df.columns if col.startswith("Contract_Type_")]
		contract_data = df[contract_cols + [target_col]].copy()
		contract_data['Contract_Type'] = contract_data[contract_cols].idxmax(axis=1).str.replace("Contract_Type_", "")
		plt.figure(figsize=(9, 5))
		sns.countplot(data=contract_data, x="Contract_Type", hue=target_col)
		plt.title("Contract Type vs Churn")
		plt.xticks(rotation=15)
		plt.tight_layout()
		plt.savefig(os.path.join(output_dir, "eda_contract_vs_churn.png"), dpi=200)
		plt.close()

	if "Average_Monthly_Bill" in df.columns:
		plt.figure(figsize=(8, 5))
		sns.histplot(data=df, x="Average_Monthly_Bill", bins=30, kde=True)
		plt.title("Average Monthly Bill Distribution")
		plt.tight_layout()
		plt.savefig(os.path.join(output_dir, "eda_monthly_charges_distribution.png"), dpi=200)
		plt.close()

	if "Tenure_Months" in df.columns:
		plt.figure(figsize=(8, 5))
		sns.histplot(data=df, x="Tenure_Months", bins=30, kde=True)
		plt.title("Tenure Distribution")
		plt.tight_layout()
		plt.savefig(os.path.join(output_dir, "eda_tenure_distribution.png"), dpi=200)
		plt.close()

	numeric_df = df.select_dtypes(include=["number"]).copy()
	if not numeric_df.empty:
		plt.figure(figsize=(10, 8))
		sns.heatmap(numeric_df.corr(), cmap="coolwarm", center=0)
		plt.title("Numerical Correlation Heatmap")
		plt.tight_layout()
		plt.savefig(os.path.join(output_dir, "eda_correlation_heatmap.png"), dpi=200)
		plt.close()


def build_model() -> LogisticRegression:
	return LogisticRegression(max_iter=2000, random_state=RANDOM_STATE, C=10.0, solver="liblinear", penalty="l1")




def get_scores_for_roc(model: Pipeline, X_test: pd.DataFrame) -> np.ndarray:
	if hasattr(model, "predict_proba"):
		return model.predict_proba(X_test)[:, 1]
	if hasattr(model, "decision_function"):
		raw_scores = model.decision_function(X_test)
		min_val, max_val = raw_scores.min(), raw_scores.max()
		if max_val == min_val:
			return np.zeros_like(raw_scores, dtype=float)
		return (raw_scores - min_val) / (max_val - min_val)
	return model.predict(X_test)


def evaluate_model(
	name: str,
	pipeline: Pipeline,
	X_train: pd.DataFrame,
	X_test: pd.DataFrame,
	y_train: pd.Series,
	y_test: pd.Series,
) -> Tuple[dict, np.ndarray, str, Pipeline]:
	pipeline.fit(X_train, y_train)

	y_pred = pipeline.predict(X_test)
	y_score = get_scores_for_roc(pipeline, X_test)

	metrics = {
		"Model": name,
		"Accuracy": accuracy_score(y_test, y_pred),
		"Precision": precision_score(y_test, y_pred, zero_division=0),
		"Recall": recall_score(y_test, y_pred, zero_division=0),
		"F1": f1_score(y_test, y_pred, zero_division=0),
		"ROC_AUC": roc_auc_score(y_test, y_score),
	}

	cm = confusion_matrix(y_test, y_pred)
	report = classification_report(y_test, y_pred, zero_division=0)

	return metrics, cm, report, pipeline


def plot_confusion_matrix(cm: np.ndarray, model_name: str, output_dir: str) -> None:
	plt.figure(figsize=(6, 5))
	sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
	plt.title(f"Confusion Matrix - {model_name}")
	plt.xlabel("Predicted")
	plt.ylabel("Actual")
	plt.tight_layout()
	filename = f"cm_{model_name.lower().replace(' ', '_')}.png"
	plt.savefig(os.path.join(output_dir, filename), dpi=200)
	plt.close()


def save_artifacts(pipeline: Pipeline, output_dir: str) -> Tuple[str, str]:
	preprocessor = pipeline.named_steps["preprocessor"]
	classifier = pipeline.named_steps["classifier"]

	model_path = os.path.join(output_dir, "best_churn_model.pkl")
	preprocessor_path = os.path.join(output_dir, "preprocessing_pipeline.pkl")

	joblib.dump(classifier, model_path)
	joblib.dump(preprocessor, preprocessor_path)

	return model_path, preprocessor_path


def reload_and_predict_sample(
	model_path: str, preprocessor_path: str, X_test: pd.DataFrame
) -> None:
	loaded_model = joblib.load(model_path)
	loaded_preprocessor = joblib.load(preprocessor_path)

	sample_customer = X_test.iloc[[0]].copy()
	transformed_sample = loaded_preprocessor.transform(sample_customer)

	sample_pred = loaded_model.predict(transformed_sample)[0]
	sample_prob = None
	if hasattr(loaded_model, "predict_proba"):
		sample_prob = loaded_model.predict_proba(transformed_sample)[0][1]

	print("\n=== SAMPLE CUSTOMER PREDICTION (RELOADED ARTIFACTS) ===")
	print(sample_customer)
	print(f"Predicted churn class: {sample_pred}")
	if sample_prob is not None:
		print(f"Predicted churn probability: {sample_prob:.4f}")


def main() -> None:
	ensure_output_dir(OUTPUT_DIR)

	df = load_and_clean_data(DATA_PATH, target_column=TARGET_COLUMN)
	perform_eda(df, TARGET_COLUMN, OUTPUT_DIR)

	X, y_raw = split_features_target(df, target_column=TARGET_COLUMN)
	y = encode_target(y_raw)

	if not set(pd.Series(y).dropna().unique()).issubset({0, 1}):
		raise ValueError("Target labels must be binary for churn classification.")

	numerical_features, categorical_features = identify_feature_types(X)
	print("\n=== FEATURE TYPE SUMMARY ===")
	print(f"Numerical features ({len(numerical_features)}): {numerical_features}")
	print(f"Categorical features ({len(categorical_features)}): {categorical_features}")

	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y,
		test_size=TEST_SIZE,
		random_state=RANDOM_STATE,
		stratify=y,
	)

	base_preprocessor = build_preprocessing_pipeline(numerical_features, categorical_features)
	model = build_model()

	print("\n=== MODEL TRAINING & EVALUATION ===")
	pipeline = Pipeline(
		steps=[
			("preprocessor", base_preprocessor),
			("classifier", model),
		]
	)

	metrics, cm, report, trained_pipeline = evaluate_model(
		"Logistic Regression", pipeline, X_train, X_test, y_train, y_test
	)

	print(f"\nModel: Logistic Regression")
	print(
		f"Accuracy={metrics['Accuracy']:.4f}, Precision={metrics['Precision']:.4f}, "
		f"Recall={metrics['Recall']:.4f}, F1={metrics['F1']:.4f}, ROC_AUC={metrics['ROC_AUC']:.4f}"
	)
	print("Confusion Matrix:")
	print(cm)
	print("Classification Report:")
	print(report)

	plot_confusion_matrix(cm, "Logistic Regression", OUTPUT_DIR)

	print("\n=== MODEL METRICS ===")
	print(metrics)

	model_path, preprocessor_path = save_artifacts(trained_pipeline, OUTPUT_DIR)
	print(f"Saved model to: {model_path}")
	print(f"Saved preprocessing pipeline to: {preprocessor_path}")

	reload_and_predict_sample(model_path, preprocessor_path, X_test)


if __name__ == "__main__":
	main()
