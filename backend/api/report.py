from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from core.security import get_current_user_email
from database.connection import get_db

from db_models.prediction import Prediction
from db_models.user import User

from schemas.prediction import (
    PredictionHistoryItem,
    PaginatedPredictionHistory,
    ReportSummary,
)


router = APIRouter(
    prefix="/report",
    tags=["Report"],
)


# ============================================================
# PREDICTION HISTORY
# ============================================================

@router.get(
    "/history",
    response_model=PaginatedPredictionHistory,
)
def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=200),
    search: str = Query(""),
    db: Session = Depends(get_db),
    current_email: str = Depends(
        get_current_user_email
    ),
):
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

    query = (
        db.query(Prediction)
        .filter(
            Prediction.owner_id == user.id
        )
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search.strip():
        query = query.filter(
            Prediction.customer_id.ilike(
                f"%{search.strip()}%"
            )
        )

    # --------------------------------------------------------
    # Total matching customers
    # --------------------------------------------------------

    total = query.count()

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * limit

    records = (
        query
        .order_by(
            Prediction.churn_probability.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_pages = (
        (total + limit - 1) // limit
        if total > 0
        else 1
    )

    return PaginatedPredictionHistory(
        items=records,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


# ============================================================
# RISK SUMMARY
# ============================================================

@router.get(
    "/risk-summary",
)
def get_risk_summary(
    db: Session = Depends(get_db),
    current_email: str = Depends(
        get_current_user_email
    ),
):
    """
    Calculate global churn-risk statistics.

    This queries the database directly instead of
    loading all 50,000 customers into the frontend.
    """

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

    result = (
        db.query(
            func.count(
                Prediction.id
            ).label("total"),

            func.sum(
                case(
                    (
                        Prediction.churn_probability >= 0.70,
                        1,
                    ),
                    else_=0,
                )
            ).label("high_risk"),

            func.max(
                Prediction.churn_probability
            ).label("highest_probability"),
        )
        .filter(
            Prediction.owner_id == user.id
        )
        .first()
    )

    total = int(
        result.total or 0
    )

    high_risk = int(
        result.high_risk or 0
    )

    highest_probability = float(
        result.highest_probability or 0
    )

    # Protect against percentages stored as 0-100.
    if highest_probability > 1:
        highest_probability /= 100.0

    highest_probability = max(
        0.0,
        min(
            highest_probability,
            1.0,
        ),
    )

    return {
        "total_customers": total,
        "high_risk": high_risk,
        "highest_probability": highest_probability,
    }


# ============================================================
# REPORT SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=ReportSummary,
)
def get_summary(
    db: Session = Depends(get_db),
    current_email: str = Depends(
        get_current_user_email
    ),
):
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

    summary = (
        db.query(
            func.count(
                Prediction.id
            ).label(
                "total_predictions"
            ),

            func.sum(
                case(
                    (
                        func.lower(
                            func.trim(
                                Prediction.churn_label
                            )
                        ).in_(
                            [
                                "yes",
                                "churn",
                                "churned",
                                "1",
                                "true",
                            ]
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label(
                "churn_count"
            ),

            func.avg(
                case(
                    (
                        Prediction.churn_probability > 1,
                        Prediction.churn_probability / 100.0,
                    ),
                    else_=Prediction.churn_probability,
                )
            ).label(
                "average_churn_probability"
            ),
        )
        .filter(
            Prediction.owner_id == user.id
        )
        .first()
    )

    total = int(
        summary.total_predictions or 0
    )

    churn_count = int(
        summary.churn_count or 0
    )

    no_churn_count = (
        total - churn_count
    )

    average_probability = float(
        summary.average_churn_probability
        or 0.0
    )

    average_probability = max(
        0.0,
        min(
            average_probability,
            1.0,
        ),
    )

    return ReportSummary(
        total_predictions=total,
        churn_count=churn_count,
        no_churn_count=no_churn_count,
        average_churn_probability=round(
            average_probability,
            4,
        ),
    )