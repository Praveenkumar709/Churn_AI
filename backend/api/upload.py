import io
import json
import os
import tempfile

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from core.security import get_current_user_email
from database.connection import get_db

from db_models.prediction import Prediction
from db_models.user import User

from schemas.prediction import (
    BulkUploadResponse,
    OverviewData,
)

from services.prediction_service import (
    get_prediction_service,
)


router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


# ============================================================
# LATEST UPLOAD OVERVIEW
# ============================================================

LATEST_UPLOAD_OVERVIEW = None

OVERVIEW_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(__file__)
    ),
    "latest_overview.json",
)


# ============================================================
# SAVE OVERVIEW
# ============================================================

def save_overview_to_file(
    overview: dict,
) -> None:

    global LATEST_UPLOAD_OVERVIEW

    LATEST_UPLOAD_OVERVIEW = overview

    try:

        with open(
            OVERVIEW_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                overview,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(
            f"Overview saved to: {OVERVIEW_FILE}"
        )

    except Exception as exc:

        print(
            f"Warning: could not save overview: {exc}"
        )


# ============================================================
# LOAD OVERVIEW
# ============================================================

def load_overview_from_file():

    global LATEST_UPLOAD_OVERVIEW

    if LATEST_UPLOAD_OVERVIEW is not None:
        return LATEST_UPLOAD_OVERVIEW

    if not os.path.exists(
        OVERVIEW_FILE
    ):
        return None

    try:

        with open(
            OVERVIEW_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            overview = json.load(file)

        LATEST_UPLOAD_OVERVIEW = overview

        print(
            f"Overview loaded from: {OVERVIEW_FILE}"
        )

        return overview

    except Exception as exc:

        print(
            f"Warning: could not load overview: {exc}"
        )

        return None


# ============================================================
# REQUIRED COLUMNS
# ============================================================

ENCODED_REQUIRED_COLUMNS = [

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

    "Churn",
]


# ============================================================
# CUSTOMER ID
# ============================================================

def get_customer_id(
    customer_data: dict,
    index: int,
) -> str:

    customer_id = customer_data.get(
        "CustomerID"
    )

    if customer_id is not None:

        customer_id = str(
            customer_id
        ).strip()

        if customer_id:
            return customer_id

    return f"cust_{index + 1}"


# ============================================================
# DATASET VALIDATION
# ============================================================

def validate_dataset(
    df: pd.DataFrame,
) -> None:

    if df.empty:

        raise HTTPException(
            status_code=400,
            detail="CSV file contains no customer records.",
        )

    missing_columns = [

        column

        for column in ENCODED_REQUIRED_COLUMNS

        if column not in df.columns

    ]

    if missing_columns:

        raise HTTPException(

            status_code=400,

            detail=(
                "CSV is missing required columns: "
                + ", ".join(
                    missing_columns
                )
            ),

        )


# ============================================================
# GET CURRENT USER
# ============================================================

def get_user(
    db: Session,
    current_email: str,
) -> User:

    user = (

        db.query(User)

        .filter(
            User.email == current_email
        )

        .first()

    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# ============================================================
# DELETE PREVIOUS PREDICTIONS
# ============================================================

def clear_previous_predictions(
    db: Session,
    user_id: int,
) -> None:

    db.query(
        Prediction
    ).filter(

        Prediction.owner_id == user_id

    ).delete(

        synchronize_session=False

    )

    db.commit()


# ============================================================
# STORE PREDICTIONS
# ============================================================

def store_predictions(
    db: Session,
    current_email: str,
    prediction_data: list,
) -> None:

    user = get_user(
        db,
        current_email,
    )

    clear_previous_predictions(
        db,
        user.id,
    )

    records = []

    for index, customer_result in enumerate(
        prediction_data
    ):

        original = customer_result.get(
            "original_data",
            {},
        )

        customer_id = get_customer_id(
            original,
            index,
        )

        prediction = customer_result.get(
            "prediction",
            0,
        )

        probability = customer_result.get(
            "probability",
            0.0,
        )

        churn_reason = customer_result.get(
            "churn_reason"
        )

        recommendations = customer_result.get(
            "recommendations"
        )

        if recommendations is None:

            recommendations_json = None

        elif isinstance(
            recommendations,
            list,
        ):

            recommendations_json = json.dumps(
                recommendations
            )

        else:

            recommendations_json = json.dumps(
                [str(recommendations)]
            )

        records.append({

            "customer_id":
                str(customer_id),

            "churn_probability":
                float(probability),

            "churn_label":
                (
                    "Yes"
                    if prediction == 1
                    else "No"
                ),

            "churn_reason":
                (
                    str(churn_reason)
                    if churn_reason is not None
                    else None
                ),

            "recommendations":
                recommendations_json,

            "owner_id":
                user.id,

        })

    if records:

        db.bulk_insert_mappings(
            Prediction,
            records,
        )

    db.commit()


# ============================================================
# BUILD OVERVIEW
# ============================================================

def build_detailed_overview(
    df: pd.DataFrame,
    prediction_data: list,
) -> dict:

    total = len(df)

    high_risk = 0
    medium_risk = 0
    low_risk = 0
    churned = 0

    probabilities = []

    # --------------------------------------------------------
    # Risk distribution
    # --------------------------------------------------------

    for item in prediction_data:

        probability = float(
            item.get(
                "probability",
                0,
            )
        )

        if probability > 1:
            probability /= 100

        probability = max(
            0.0,
            min(
                probability,
                1.0,
            ),
        )

        probabilities.append(
            probability
        )

        if probability >= 0.70:

            high_risk += 1

        elif probability >= 0.40:

            medium_risk += 1

        else:

            low_risk += 1

        if int(
            item.get(
                "prediction",
                0,
            )
        ) == 1:

            churned += 1

    # --------------------------------------------------------
    # Prediction mask
    # --------------------------------------------------------

    churn_mask = pd.Series(

        [
            int(
                item.get(
                    "prediction",
                    0,
                )
            ) == 1

            for item in prediction_data
        ],

        index=df.index,
    )

    # --------------------------------------------------------
    # Contract
    #
    # Dataset is already one-hot encoded.
    # --------------------------------------------------------

    contract_counts = {}

    contract_columns = {

        "Month-to-month":
            "Contract_Type_Month-to-month",

        "One year":
            "Contract_Type_One year",

        "Two year":
            "Contract_Type_Two year",

    }

    for name, column in contract_columns.items():

        if column in df.columns:

            contract_counts[name] = int(
                pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0).sum()
            )

    # --------------------------------------------------------
    # Payment method
    # --------------------------------------------------------

    payment_counts = {}

    payment_columns = {

        "Bank transfer (auto)":
            "Payment_Method_Bank transfer (auto)",

        "Credit card (auto)":
            "Payment_Method_Credit card (auto)",

        "Electronic check":
            "Payment_Method_Electronic check",

        "Mailed check":
            "Payment_Method_Mailed check",

    }

    for name, column in payment_columns.items():

        if column in df.columns:

            payment_counts[name] = int(
                pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0).sum()
            )

    # --------------------------------------------------------
    # Internet service
    # --------------------------------------------------------

    internet_service_counts = {}

    if "Internet_Service" in df.columns:

        values = (
            df["Internet_Service"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .value_counts()
            .to_dict()
        )

        internet_service_counts = {
            str(k): int(v)
            for k, v in values.items()
        }

    # --------------------------------------------------------
    # Tenure
    # --------------------------------------------------------

    average_tenure_churn = 0.0
    average_tenure_no_churn = 0.0

    if "Tenure_Months" in df.columns:

        tenure = pd.to_numeric(
            df["Tenure_Months"],
            errors="coerce",
        )

        churn_tenure = tenure[
            churn_mask
        ].dropna()

        no_churn_tenure = tenure[
            ~churn_mask
        ].dropna()

        if not churn_tenure.empty:

            average_tenure_churn = round(
                float(
                    churn_tenure.mean()
                ),
                2,
            )

        if not no_churn_tenure.empty:

            average_tenure_no_churn = round(
                float(
                    no_churn_tenure.mean()
                ),
                2,
            )

    # --------------------------------------------------------
    # Monthly bill
    # --------------------------------------------------------

    monthly_distribution = {

        "min": 0.0,
        "max": 0.0,
        "avg": 0.0,

    }

    if "Current_Monthly_Bill" in df.columns:

        monthly_bill = pd.to_numeric(
            df["Current_Monthly_Bill"],
            errors="coerce",
        ).dropna()

        if not monthly_bill.empty:

            monthly_distribution = {

                "min":
                    round(
                        float(
                            monthly_bill.min()
                        ),
                        2,
                    ),

                "max":
                    round(
                        float(
                            monthly_bill.max()
                        ),
                        2,
                    ),

                "avg":
                    round(
                        float(
                            monthly_bill.mean()
                        ),
                        2,
                    ),

            }

    # --------------------------------------------------------
    # Churn drivers
    # --------------------------------------------------------

    churn_drivers = []

    driver_definitions = {

        "Short Tenure":
            (
                "Tenure_Months",
                "short_tenure",
            ),

        "Late Payments":
            (
                "Late_Payments",
                "positive",
            ),

        "Support Tickets":
            (
                "Support_Tickets",
                "positive",
            ),

        "Customer Complaints":
            (
                "Complaints",
                "positive",
            ),

        "Bill Increase":
            (
                "Bill_Change_Pct",
                "positive",
            ),

        "Network Issues":
            (
                "Network_Issues",
                "positive",
            ),

        "Service Downtime":
            (
                "Downtime_Hours",
                "positive",
            ),

    }

    for driver_name, (
        column,
        driver_type,
    ) in driver_definitions.items():

        if column not in df.columns:
            continue

        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        if driver_type == "short_tenure":

            affected = values < 12

        else:

            affected = values > 0

        affected_count = int(
            affected.sum()
        )

        if affected_count == 0:
            continue

        affected_churned = int(
            (
                affected
                & churn_mask
            ).sum()
        )

        churn_rate = (
            affected_churned
            / affected_count
        ) * 100

        churn_drivers.append({

            "name":
                driver_name,

            "affected_customers":
                affected_count,

            "churned_customers":
                affected_churned,

            "churn_rate":
                round(
                    churn_rate,
                    2,
                ),

        })

    churn_drivers.sort(
        key=lambda item:
            item["churn_rate"],
        reverse=True,
    )

    # --------------------------------------------------------
    # Final overview
    # --------------------------------------------------------

    return {

        "total_customers":
            total,

        "churn_risk": {

            "high":
                high_risk,

            "medium":
                medium_risk,

            "low":
                low_risk,

        },

        "churn_by_contract":
            contract_counts,

        "churn_by_internet_service":
            internet_service_counts,

        "churn_by_payment_method":
            payment_counts,

        "average_tenure_churn":
            average_tenure_churn,

        "average_tenure_no_churn":
            average_tenure_no_churn,

        "monthly_charges_distribution":
            monthly_distribution,

        "churn_drivers":
            churn_drivers,

    }


# ============================================================
# PROCESS UPLOADED FILE
# ============================================================

def process_uploaded_file(
    contents: bytes,
):

    try:

        df = pd.read_csv(
            io.BytesIO(contents)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not parse CSV file: {exc}"
            ),
        )

    # Clean column names

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    validate_dataset(
        df
    )

    customers_data = df.to_dict(
        orient="records"
    )

    prediction_service = (
        get_prediction_service()
    )

    result = (
        prediction_service
        .predict_batch_churn(
            customers_data
        )
    )

    if not result.get("success"):

        raise HTTPException(
            status_code=500,
            detail=result.get(
                "error",
                "Prediction failed",
            ),
        )

    detailed_overview = (
        build_detailed_overview(
            df,
            result["data"],
        )
    )

    result["overview"] = (
        detailed_overview
    )

    return df, result


# ============================================================
# UPLOAD CSV
# ============================================================

@router.post(
    "",
    response_model=BulkUploadResponse,
)
async def upload_csv(

    file: UploadFile = File(...),

    db: Session = Depends(
        get_db
    ),

    current_email: str = Depends(
        get_current_user_email
    ),

):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    if not file.filename.lower().endswith(
        ".csv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    df, result = (
        process_uploaded_file(
            contents
        )
    )

    save_overview_to_file(
        result["overview"]
    )

    store_predictions(
        db=db,
        current_email=current_email,
        prediction_data=result["data"],
    )

    formatted_results = []

    for index, customer_result in enumerate(
        result["data"]
    ):

        original = customer_result.get(
            "original_data",
            {},
        )

        formatted_results.append({

            "customer_id":
                get_customer_id(
                    original,
                    index,
                ),

            "churn_probability":
                float(
                    customer_result[
                        "probability"
                    ]
                ),

            "churn_label":
                (
                    "Yes"
                    if customer_result[
                        "prediction"
                    ] == 1
                    else "No"
                ),

            "churn_reason":
                customer_result.get(
                    "churn_reason"
                ),

            "recommendations":
                customer_result.get(
                    "recommendations"
                ),

        })

    return BulkUploadResponse(

        total_records=
            len(formatted_results),

        results=
            formatted_results,

        overview=
            result["overview"],

    )


# ============================================================
# GET UPLOAD OVERVIEW
# ============================================================

@router.get(
    "/overview",
    response_model=OverviewData,
)
async def get_upload_overview(

    db: Session = Depends(
        get_db
    ),

    current_email: str = Depends(
        get_current_user_email
    ),

):

    overview = (
        load_overview_from_file()
    )

    if overview is not None:

        return OverviewData(
            **overview
        )

    user = get_user(
        db,
        current_email,
    )

    predictions = (

        db.query(
            Prediction
        )

        .filter(
            Prediction.owner_id == user.id
        )

        .order_by(
            Prediction.created_at.desc()
        )

        .all()

    )

    if not predictions:

        return OverviewData(

            total_customers=0,

            churn_risk={
                "high": 0,
                "medium": 0,
                "low": 0,
            },

            churn_by_contract={},

            churn_by_internet_service={},

            churn_by_payment_method={},

            average_tenure_churn=0.0,

            average_tenure_no_churn=0.0,

            monthly_charges_distribution={
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
            },

            churn_drivers=[],

        )

    total_customers = len(
        predictions
    )

    high_risk = 0
    medium_risk = 0
    low_risk = 0

    for prediction in predictions:

        probability = float(
            prediction.churn_probability or 0
        )

        if probability > 1:
            probability /= 100

        probability = max(
            0.0,
            min(
                probability,
                1.0,
            ),
        )

        if probability >= 0.70:

            high_risk += 1

        elif probability >= 0.40:

            medium_risk += 1

        else:

            low_risk += 1

    return OverviewData(

        total_customers=
            total_customers,

        churn_risk={

            "high":
                high_risk,

            "medium":
                medium_risk,

            "low":
                low_risk,

        },

        churn_by_contract={},

        churn_by_internet_service={},

        churn_by_payment_method={},

        average_tenure_churn=0.0,

        average_tenure_no_churn=0.0,

        monthly_charges_distribution={

            "min": 0.0,

            "max": 0.0,

            "avg": 0.0,

        },

        churn_drivers=[],

    )


# ============================================================
# DOWNLOAD RESULTS
# ============================================================

@router.post(
    "/download"
)
async def download_results(

    file: UploadFile = File(...),

    db: Session = Depends(
        get_db
    ),

    current_email: str = Depends(
        get_current_user_email
    ),

):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected.",
        )

    if not file.filename.lower().endswith(
        ".csv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    df, result = (
        process_uploaded_file(
            contents
        )
    )

    save_overview_to_file(
        result["overview"]
    )

    results_data = []

    for customer_result in result["data"]:

        original = (
            customer_result[
                "original_data"
            ].copy()
        )

        original[
            "Churn_Probability"
        ] = float(
            customer_result[
                "probability"
            ]
        )

        original[
            "Churn_Prediction"
        ] = (

            "Yes"

            if customer_result[
                "prediction"
            ] == 1

            else "No"

        )

        original[
            "Churn_Reason"
        ] = customer_result.get(
            "churn_reason",
            "N/A",
        )

        recommendations = (
            customer_result.get(
                "recommendations",
                [],
            )
        )

        if isinstance(
            recommendations,
            list,
        ):

            original[
                "Recommendations"
            ] = "; ".join(
                str(item)
                for item in recommendations
            )

        else:

            original[
                "Recommendations"
            ] = str(
                recommendations
            )

        results_data.append(
            original
        )

    results_df = pd.DataFrame(
        results_data
    )

    temp_dir = tempfile.gettempdir()

    safe_email = (
        current_email
        .replace("@", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    output_filename = (
        f"churn_predictions_{safe_email}.csv"
    )

    output_path = os.path.join(
        temp_dir,
        output_filename,
    )

    results_df.to_csv(
        output_path,
        index=False,
    )

    store_predictions(
        db=db,
        current_email=current_email,
        prediction_data=result["data"],
    )

    return FileResponse(

        output_path,

        media_type="text/csv",

        filename="churn_analysis_results.csv",

    )