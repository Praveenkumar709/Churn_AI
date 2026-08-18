import pandas as pd


EXPECTED_FEATURES = [
    "Age",
    "Gender",
    "Dependents",
    "Tenure_Months",
    "Num_Services",
    "Traveler_Profile",
    "Data_Usage_GB",
    "Data_Usage_Change_Pct",
    "Call_Minutes",
    "Num_Calls",
    "SMS_Usage",
    "Usage_5G_4G_Pct",
    "Roaming_Usage_Mins",
    "International_Usage_Mins",
    "Plan_Price",
    "Average_Monthly_Bill",
    "Current_Monthly_Bill",
    "Bill_Change_Pct",
    "Late_Payments",
    "Dropped_Calls",
    "Network_Issues",
    "Downtime_Hours",
    "Complaints",
    "Support_Tickets",
    "Complaint_Resolution_Time_Hrs",

    "Family_Status_Married",
    "Family_Status_Married with Kids",
    "Family_Status_Single",
    "Family_Status_Single Parent",

    "Location_Rural",
    "Location_Suburban",
    "Location_Urban",

    "Contract_Type_Month-to-month",
    "Contract_Type_One year",
    "Contract_Type_Two year",

    "Payment_Method_Bank transfer (auto)",
    "Payment_Method_Credit card (auto)",
    "Payment_Method_Electronic check",
    "Payment_Method_Mailed check",
]


def prepare_for_model(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare telecom customer data for the
    100k Logistic Regression model.

    Supports:
    1. Already one-hot encoded 100k dataset
    2. Original/raw telecom dataset
    """

    df = df.copy()

    # Alias mapping for standard datasets
    alias_map = {
        "customer_id": "CustomerID",
        "customerid": "CustomerID",
        "gender": "Gender",
        "tenure": "Tenure_Months",
        "tenure_months": "Tenure_Months",
        "contract": "Contract_Type",
        "contract_type": "Contract_Type",
        "paymentmethod": "Payment_Method",
        "payment_method": "Payment_Method",
        "monthlycharges": "Current_Monthly_Bill",
        "current_monthly_bill": "Current_Monthly_Bill",
        "totalcharges": "Average_Monthly_Bill",
        "average_monthly_bill": "Average_Monthly_Bill",
        "dependents": "Dependents",
    }
    rename_dict = {}
    for col in df.columns:
        clean_col = str(col).strip()
        lower_col = clean_col.lower()
        if lower_col in alias_map and clean_col not in EXPECTED_FEATURES:
            rename_dict[col] = alias_map[lower_col]
    if rename_dict:
        df = df.rename(columns=rename_dict)

    # Convert SeniorCitizen to Age if Age not provided
    if "SeniorCitizen" in df.columns and "Age" not in df.columns:
        df["Age"] = df["SeniorCitizen"].apply(lambda x: 65 if str(x).strip() in ["1", "true", "True"] else 35)

    # Convert Partner/Dependents
    if "Partner" in df.columns and "Dependents" not in df.columns:
        df["Dependents"] = df["Partner"].apply(lambda x: 1 if str(x).strip().lower() in ["yes", "1", "true"] else 0)

    # =========================================================
    # REMOVE ID AND TARGET
    # =========================================================

    for column in ["CustomerID", "Churn"]:

        if column in df.columns:

            df = df.drop(
                columns=[column]
            )

    # =========================================================
    # DETECT DATASET FORMAT
    # =========================================================

    encoded_columns = [
        "Family_Status_Married",
        "Family_Status_Married with Kids",
        "Family_Status_Single",
        "Family_Status_Single Parent",

        "Location_Rural",
        "Location_Suburban",
        "Location_Urban",

        "Contract_Type_Month-to-month",
        "Contract_Type_One year",
        "Contract_Type_Two year",

        "Payment_Method_Bank transfer (auto)",
        "Payment_Method_Credit card (auto)",
        "Payment_Method_Electronic check",
        "Payment_Method_Mailed check",
    ]

    is_encoded_dataset = all(
        column in df.columns
        for column in encoded_columns
    )

    # =========================================================
    # RAW DATASET PROCESSING
    # =========================================================

    if not is_encoded_dataset:

        # -----------------------------------------------------
        # Gender
        # -----------------------------------------------------

        if "Gender" in df.columns:

            df["Gender"] = (
                df["Gender"]
                .astype(str)
                .str.strip()
                .map({
                    "Female": 0,
                    "Male": 1,
                    "0": 0,
                    "1": 1,
                })
                .fillna(0)
            )

        # -----------------------------------------------------
        # Traveler Profile
        # -----------------------------------------------------

        if "Traveler_Profile" in df.columns:

            df["Traveler_Profile"] = (
                df["Traveler_Profile"]
                .astype(str)
                .str.strip()
                .map({
                    "Local": 0,
                    "Frequent Traveler": 1,
                })
                .fillna(0)
            )

        # -----------------------------------------------------
        # Family Status
        # -----------------------------------------------------

        if "Family_Status" in df.columns:

            family_values = [
                "Married",
                "Married with Kids",
                "Single",
                "Single Parent",
            ]

            for value in family_values:

                feature_name = (
                    f"Family_Status_{value}"
                )

                df[feature_name] = (
                    df["Family_Status"]
                    .astype(str)
                    .str.strip()
                    == value
                ).astype(int)

        # -----------------------------------------------------
        # Location
        # -----------------------------------------------------

        if "Location" in df.columns:

            location_values = [
                "Rural",
                "Suburban",
                "Urban",
            ]

            for value in location_values:

                feature_name = (
                    f"Location_{value}"
                )

                df[feature_name] = (
                    df["Location"]
                    .astype(str)
                    .str.strip()
                    == value
                ).astype(int)

        # -----------------------------------------------------
        # Contract Type
        # -----------------------------------------------------

        if "Contract_Type" in df.columns:

            contract_values = [
                "Month-to-month",
                "One year",
                "Two year",
            ]

            for value in contract_values:

                feature_name = (
                    f"Contract_Type_{value}"
                )

                df[feature_name] = (
                    df["Contract_Type"]
                    .astype(str)
                    .str.strip()
                    == value
                ).astype(int)

        # -----------------------------------------------------
        # Payment Method
        # -----------------------------------------------------

        if "Payment_Method" in df.columns:

            payment_series = df["Payment_Method"].astype(str).str.strip().replace({
                "Bank transfer (automatic)": "Bank transfer (auto)",
                "Credit card (automatic)": "Credit card (auto)",
            })

            payment_values = [
                "Bank transfer (auto)",
                "Credit card (auto)",
                "Electronic check",
                "Mailed check",
            ]

            for value in payment_values:

                feature_name = (
                    f"Payment_Method_{value}"
                )

                df[feature_name] = (
                    payment_series == value
                ).astype(int)

    # =========================================================
    # ENSURE ENCODED COLUMNS EXIST
    # =========================================================

    for column in encoded_columns:

        if column not in df.columns:

            df[column] = 0

    # =========================================================
    # FILL MISSING EXPECTED FEATURES
    # =========================================================

    for column in EXPECTED_FEATURES:

        if column not in df.columns:

            df[column] = 0

    # =========================================================
    # SELECT EXACT 39 FEATURES
    # =========================================================

    X = df[
        EXPECTED_FEATURES
    ].copy()

    # =========================================================
    # CONVERT TO NUMERIC
    # =========================================================

    for column in X.columns:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce",
        )

    # =========================================================
    # HANDLE MISSING VALUES
    # =========================================================

    X = X.fillna(0)

    # =========================================================
    # FINAL SAFETY CHECK
    # =========================================================

    if X.shape[1] != 39:

        raise ValueError(
            f"Expected 39 model features, "
            f"but got {X.shape[1]}"
        )

    return X