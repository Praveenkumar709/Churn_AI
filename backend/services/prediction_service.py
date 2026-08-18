import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add backend directory to Python path
sys.path.append(
    str(Path(__file__).parent.parent)
)

from ml.predictor import get_predictor


class PredictionService:

    def __init__(self):

        # New Logistic Regression model location:
        # backend/models/logistic_regression_100k.joblib
        self.models_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "models"
        )

        self.predictor = None

    def initialize(self):

        try:

            self.predictor = get_predictor(
                self.models_dir
            )

            print(
                "Prediction service initialized "
                "with Logistic Regression"
            )

            return True

        except Exception as e:

            print(
                f"Error initializing prediction service: {e}"
            )

            return False

    def predict_churn(
        self,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        if self.predictor is None:

            if not self.initialize():

                return {
                    "success": False,
                    "error": "Failed to initialize prediction service: Churn model could not be loaded."
                }

        try:

            result = self.predictor.predict(
                customer_data
            )

            return {
                "success": True,
                "data": {
                    "prediction":
                        result["prediction"],

                    "probability":
                        result["probability"],

                    "churn_reason":
                        result.get(
                            "churn_reason"
                        ),

                    "recommendations":
                        result.get(
                            "recommendations"
                        ),

                    "model_used":
                        result.get(
                            "model_used"
                        ),

                    "model_accuracy":
                        result.get(
                            "model_accuracy"
                        ),
                }
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def predict_batch_churn(
        self,
        customers_data: List[
            Dict[str, Any]
        ]
    ) -> Dict[str, Any]:

        if self.predictor is None:

            if not self.initialize():

                return {
                    "success": False,
                    "error": "Failed to initialize prediction service: Churn model could not be loaded."
                }

        try:

            results = (
                self.predictor.predict_batch(
                    customers_data
                )
            )

            enhanced_results = []

            for i, result in enumerate(
                results
            ):

                enhanced_results.append({
                    "original_data":
                        customers_data[i],

                    "prediction":
                        result["prediction"],

                    "probability":
                        result["probability"],

                    "churn_reason":
                        result.get(
                            "churn_reason"
                        ),

                    "recommendations":
                        result.get(
                            "recommendations"
                        ),

                    "model_used":
                        result.get(
                            "model_used"
                        ),

                    "model_accuracy":
                        result.get(
                            "model_accuracy"
                        ),
                })

            overview = (
                self.predictor
                .generate_overview_data(
                    enhanced_results
                )
            )

            return {
                "success": True,
                "data": enhanced_results,
                "count":
                    len(enhanced_results),
                "overview":
                    overview
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def get_model_info(
        self
    ) -> Dict[str, Any]:

        if self.predictor is None:

            if not self.initialize():

                return {
                    "success": False,
                    "error": "Failed to initialize prediction service: Churn model could not be loaded."
                }

        try:

            info = (
                self.predictor
                .get_model_info()
            )

            return {
                "success": True,
                "data": info
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    def health_check(
        self
    ) -> Dict[str, Any]:

        if self.predictor is None:

            initialized = (
                self.initialize()
            )

        else:

            initialized = True

        return {
            "status":
                (
                    "healthy"
                    if initialized
                    else "unhealthy"
                ),

            "models_loaded":
                initialized
        }


_prediction_service_instance = None


def get_prediction_service():

    global _prediction_service_instance

    if (
        _prediction_service_instance
        is None
    ):

        _prediction_service_instance = (
            PredictionService()
        )

        _prediction_service_instance.initialize()

    return (
        _prediction_service_instance
    )
