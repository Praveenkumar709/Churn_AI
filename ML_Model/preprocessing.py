from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_and_clean_data(file_path: str, target_column: str = "Churn") -> pd.DataFrame:
	"""Load CSV, normalize missing values, and remove duplicates."""
	df = pd.read_csv(file_path)
	df.columns = [col.strip() for col in df.columns]

	if target_column not in df.columns:
		raise ValueError(
			f"Target column '{target_column}' not found. Available columns: {list(df.columns)}"
		)

	# Remove customer ID as it's not predictive
	if "customerID" in df.columns:
		df = df.drop(columns=["customerID"])

	# Common telecom datasets contain blank strings that should be treated as missing.
	object_cols = df.select_dtypes(include=["object"]).columns
	for col in object_cols:
		df[col] = df[col].astype(str).str.strip()
		df[col] = df[col].replace({"": np.nan, "NA": np.nan, "N/A": np.nan, "null": np.nan})

	# Coerce common numeric-like text columns to numeric when possible.
	if "TotalCharges" in df.columns:
		df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

	before_drop = len(df)
	df = df.drop_duplicates().reset_index(drop=True)
	after_drop = len(df)

	print(f"Loaded dataset shape: {df.shape}")
	print(f"Removed duplicates: {before_drop - after_drop}")
	print("Missing values per column:")
	print(df.isna().sum().sort_values(ascending=False))

	# Feature Engineering for actual dataset columns
	if "Tenure_Months" in df.columns:
		df["Tenure_bin"] = pd.cut(df["Tenure_Months"], bins=[0, 12, 24, 36, 48, 60, 72], labels=False)
		df["Tenure_bin"] = df["Tenure_bin"].fillna(0)

	if "Plan_Price" in df.columns and "Average_Monthly_Bill" in df.columns:
		df["Bill_to_Plan_ratio"] = df["Average_Monthly_Bill"] / (df["Plan_Price"] + 1)

	if "Current_Monthly_Bill" in df.columns and "Average_Monthly_Bill" in df.columns:
		df["Bill_Change_Indicator"] = (df["Current_Monthly_Bill"] > df["Average_Monthly_Bill"]).astype(int)

	if "Data_Usage_GB" in df.columns and "Call_Minutes" in df.columns:
		df["Data_to_Call_ratio"] = df["Data_Usage_GB"] / (df["Call_Minutes"] + 1)

	if "Num_Services" in df.columns:
		df["High_Service_User"] = (df["Num_Services"] > 3).astype(int)

	if "Late_Payments" in df.columns:
		df["Has_Late_Payments"] = (df["Late_Payments"] > 0).astype(int)

	if "Support_Tickets" in df.columns:
		df["Has_Support_Tickets"] = (df["Support_Tickets"] > 0).astype(int)

	# Create aggregated features from one-hot encoded columns
	contract_cols = [col for col in df.columns if col.startswith("Contract_Type_")]
	if contract_cols:
		df["Contract_Type_Sum"] = df[contract_cols].sum(axis=1)

	location_cols = [col for col in df.columns if col.startswith("Location_")]
	if location_cols:
		df["Location_Type_Sum"] = df[location_cols].sum(axis=1)

	family_cols = [col for col in df.columns if col.startswith("Family_Status_")]
	if family_cols:
		df["Family_Status_Sum"] = df[family_cols].sum(axis=1)

	payment_cols = [col for col in df.columns if col.startswith("Payment_Method_")]
	if payment_cols:
		df["Auto_Payment_Indicator"] = df[payment_cols].apply(lambda row: 1 if any('auto' in col.lower() for col in payment_cols if row[col] == 1) else 0, axis=1)

	return df


def split_features_target(df: pd.DataFrame, target_column: str = "Churn") -> Tuple[pd.DataFrame, pd.Series]:
	"""Return feature matrix X and target vector y."""
	X = df.drop(columns=[target_column])
	y = df[target_column].copy()
	return X, y


def identify_feature_types(X: pd.DataFrame) -> Tuple[List[str], List[str]]:
	"""Identify numerical and categorical columns."""
	numerical_features = X.select_dtypes(include=["number", "bool"]).columns.tolist()
	categorical_features = X.select_dtypes(exclude=["number", "bool"]).columns.tolist()
	return numerical_features, categorical_features


def build_preprocessing_pipeline(
	numerical_features: List[str], categorical_features: List[str]
) -> ColumnTransformer:
	"""Create a ColumnTransformer with scaling for numeric and OHE for categorical."""
	numeric_pipeline = Pipeline(
		steps=[
			("imputer", SimpleImputer(strategy="median")),
			("scaler", StandardScaler()),
		]
	)

	categorical_pipeline = Pipeline(
		steps=[
			("imputer", SimpleImputer(strategy="most_frequent")),
			("onehot", OneHotEncoder(handle_unknown="ignore")),
		]
	)

	preprocessor = ColumnTransformer(
		transformers=[
			("num", numeric_pipeline, numerical_features),
			("cat", categorical_pipeline, categorical_features),
		]
	)
	return preprocessor


def encode_target(y: pd.Series) -> pd.Series:
	"""Encode churn labels into 0/1 when needed."""
	lowered = y.astype(str).str.strip().str.lower()
	unique_vals = set(lowered.dropna().unique())
	if unique_vals.issubset({"yes", "no"}):
		return lowered.map({"no": 0, "yes": 1}).astype(int)
	return y
