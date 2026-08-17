from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user_email
from database.connection import get_db
from db_models.prediction import Prediction
from db_models.user import User
from schemas.prediction import PredictionRequest, PredictionResponse
from services.prediction_service import get_prediction_service

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("", response_model=PredictionResponse)
def predict_single(
    payload: PredictionRequest,
    db: Session = Depends(get_db),
    current_email: str = Depends(get_current_user_email),
):
    """Predict churn for a single customer with reasons and recommendations"""
    # Convert payload to dictionary format expected by the service
    customer_data = payload.dict()
    
    # Get prediction service
    prediction_service = get_prediction_service()
    
    # Process prediction
    result = prediction_service.predict_churn(customer_data)
    
    if not result['success']:
        raise Exception(result['error'])
    
    prediction_data = result['data']
    
    # Store in database
    user = db.query(User).filter(User.email == current_email).first()
    record = Prediction(
        customer_id=payload.customer_id,
        churn_probability=prediction_data['probability'],
        churn_label="Yes" if prediction_data['prediction'] == 1 else "No",
        owner_id=user.id if user else None,
    )
    db.add(record)
    db.commit()

    return PredictionResponse(
        customer_id=payload.customer_id,
        churn_probability=prediction_data['probability'],
        churn_label="Yes" if prediction_data['prediction'] == 1 else "No",
        churn_reason=prediction_data.get('churn_reason'),
        recommendations=prediction_data.get('recommendations')
    )