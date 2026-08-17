from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    """Single customer's feature values."""

    customer_id: str
    tenure: int
    monthly_charges: float
    total_charges: float

    contract_type: str
    internet_service: str
    payment_method: str

    senior_citizen: int = 0

    partner: bool = False
    dependents: bool = False
    phone_service: bool = False
    multiple_lines: bool = False
    online_security: bool = False
    online_backup: bool = False
    device_protection: bool = False
    tech_support: bool = False
    streaming_tv: bool = False
    streaming_movies: bool = False
    paperless_billing: bool = False

    gender: str = "Female"


class PredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    churn_label: str

    churn_reason: Optional[str] = None
    recommendations: Optional[List[str]] = None


class PredictionHistoryItem(BaseModel):
    id: int
    customer_id: str
    churn_probability: float
    churn_label: str
    created_at: datetime

    churn_reason: Optional[str] = None

    # SQLite stores this field as TEXT/JSON.
    # Any prevents response validation from breaking
    # when the database contains a JSON string.
    recommendations: Optional[Any] = None

    class Config:
        from_attributes = True


class PaginatedPredictionHistory(BaseModel):
    items: List[PredictionHistoryItem]

    total: int
    page: int
    limit: int
    total_pages: int


class BulkUploadResponse(BaseModel):
    total_records: int

    results: List[PredictionResponse]

    overview: Optional[Dict[str, Any]] = None


class ReportSummary(BaseModel):
    total_predictions: int

    churn_count: int

    no_churn_count: int

    average_churn_probability: float


class OverviewData(BaseModel):
    total_customers: int

    churn_risk: Dict[str, int]

    churn_by_contract: Dict[str, int]

    churn_by_internet_service: Dict[str, int]

    churn_by_payment_method: Dict[str, int]

    average_tenure_churn: float

    average_tenure_no_churn: float

    monthly_charges_distribution: Dict[str, float]

    churn_drivers: List[Dict[str, Any]] = []


class CustomerAnalysis(BaseModel):
    customer_id: str

    original_data: Dict[str, Any]

    churn_probability: float

    churn_label: str

    churn_reason: str

    recommendations: List[str]