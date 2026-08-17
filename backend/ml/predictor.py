from __future__ import annotations

from typing import Dict, List, Any

import pandas as pd

from .model_loader import ModelLoader
from .deployment_preprocessing import prepare_for_model


class ChurnPredictor:

    def __init__(self, models_dir: str):
        self.models_dir = models_dir

        self.model_loader = ModelLoader(models_dir)

        if not self.model_loader.load_all():
            raise RuntimeError(
                "Failed to load ML model"
            )

        self.model = self.model_loader.best_model

    # ============================================================
    # SINGLE CUSTOMER PREDICTION
    # ============================================================

    def predict(
        self,
        customer_data: Dict[str, Any],
    ) -> Dict[str, Any]:

        try:
            df = pd.DataFrame([customer_data])

            # Convert raw customer data into the exact
            # 39 features expected by Logistic Regression.
            X = prepare_for_model(df)

            prediction = int(
                self.model.predict(X)[0]
            )

            probability = float(
                self.model.predict_proba(X)[0][1]
            )

            return {
                "prediction": prediction,
                "probability": probability,
                "churn_reason": self._get_churn_reason(
                    customer_data
                ),
                "recommendations": self._get_recommendations(
                    customer_data
                ),
                "model_used": "Logistic Regression",
                "model_accuracy": self.model_loader.best_accuracy,
            }

        except Exception as exc:
            raise RuntimeError(
                f"Prediction failed: {exc}"
            )

    # ============================================================
    # BATCH PREDICTION
    # ============================================================

    def predict_batch(
        self,
        customers_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        if not customers_data:
            return []

        try:
            df = pd.DataFrame(customers_data)

            # Prepare all customers using the same preprocessing
            # used during model training.
            X = prepare_for_model(df)

            predictions = self.model.predict(X)

            probabilities = (
                self.model.predict_proba(X)[:, 1]
            )

            results = []

            for i, customer in enumerate(customers_data):

                results.append({
                    "original_data": customer,

                    "prediction": int(
                        predictions[i]
                    ),

                    "probability": float(
                        probabilities[i]
                    ),

                    "churn_reason": self._get_churn_reason(
                        customer
                    ),

                    "recommendations": self._get_recommendations(
                        customer
                    ),

                    "model_used": "Logistic Regression",

                    "model_accuracy":
                        self.model_loader.best_accuracy,
                })

            return results

        except Exception as exc:
            raise RuntimeError(
                f"Batch prediction failed: {exc}"
            )

    # ============================================================
    # CHURN REASON
    # ============================================================

    def _get_churn_reason(
        self,
        customer: Dict[str, Any],
    ) -> str:

        reasons = []

        try:

            if float(
                customer.get(
                    "Tenure_Months",
                    0,
                )
            ) < 12:

                reasons.append(
                    "Short customer tenure"
                )

            if float(
                customer.get(
                    "Bill_Change_Pct",
                    0,
                )
            ) > 10:

                reasons.append(
                    "Monthly bill has increased"
                )

            if float(
                customer.get(
                    "Late_Payments",
                    0,
                )
            ) > 0:

                reasons.append(
                    "Late payment history"
                )

            if float(
                customer.get(
                    "Support_Tickets",
                    0,
                )
            ) > 0:

                reasons.append(
                    "Support issues reported"
                )

            if float(
                customer.get(
                    "Network_Issues",
                    0,
                )
            ) > 0:

                reasons.append(
                    "Network issues reported"
                )

            if float(
                customer.get(
                    "Complaints",
                    0,
                )
            ) > 0:

                reasons.append(
                    "Customer complaints"
                )

            if float(
                customer.get(
                    "Downtime_Hours",
                    0,
                )
            ) > 5:

                reasons.append(
                    "High service downtime"
                )

            if not reasons:
                return (
                    "No major churn risk factors identified"
                )

            return "; ".join(
                reasons[:3]
            )

        except Exception:
            return "Risk factors unavailable"

    # ============================================================
    # RETENTION RECOMMENDATIONS
    # ============================================================

    def _get_recommendations(
        self,
        customer: Dict[str, Any],
    ) -> List[str]:

        recommendations = []

        try:

            if float(
                customer.get(
                    "Tenure_Months",
                    0,
                )
            ) < 12:

                recommendations.append(
                    "Offer an early-tenure retention incentive"
                )

            if float(
                customer.get(
                    "Bill_Change_Pct",
                    0,
                )
            ) > 10:

                recommendations.append(
                    "Review pricing and offer a suitable plan"
                )

            if float(
                customer.get(
                    "Support_Tickets",
                    0,
                )
            ) > 0:

                recommendations.append(
                    "Follow up on unresolved support issues"
                )

            if float(
                customer.get(
                    "Network_Issues",
                    0,
                )
            ) > 0:

                recommendations.append(
                    "Investigate network quality problems"
                )

            if float(
                customer.get(
                    "Late_Payments",
                    0,
                )
            ) > 0:

                recommendations.append(
                    "Offer suitable payment assistance"
                )

            if not recommendations:

                recommendations.append(
                    "Maintain regular customer engagement"
                )

            return recommendations[:3]

        except Exception:

            return [
                "Maintain regular customer engagement"
            ]

    # ============================================================
    # DASHBOARD OVERVIEW
    # ============================================================

    def generate_overview_data(
        self,
        predictions_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        if not predictions_data:

            return {
                "total_customers": 0,
                "churned_customers": 0,
                "safe_customers": 0,
                "churn_rate": 0,
                "average_probability": 0,

                "churn_risk": {
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                },

                "churn_by_contract": {},

                "churn_by_internet_service": {},

                "churn_by_payment_method": {},

                "average_tenure_churn": 0,

                "average_tenure_no_churn": 0,

                "monthly_charges_distribution": {
                    "min": 0,
                    "max": 0,
                    "avg": 0,
                },

                "churn_drivers": [],
            }

        total = len(
            predictions_data
        )

        churned = sum(
            1
            for item in predictions_data
            if int(
                item.get(
                    "prediction",
                    0,
                )
            ) == 1
        )

        safe = total - churned

        probabilities = [
            float(
                item.get(
                    "probability",
                    0,
                )
            )
            for item in predictions_data
        ]

        average_probability = (
            sum(probabilities)
            / len(probabilities)
            if probabilities
            else 0
        )

        # --------------------------------------------------------
        # RISK
        # --------------------------------------------------------

        high_risk = sum(
            1
            for p in probabilities
            if p >= 0.70
        )

        medium_risk = sum(
            1
            for p in probabilities
            if 0.40 <= p < 0.70
        )

        low_risk = sum(
            1
            for p in probabilities
            if p < 0.40
        )

        # --------------------------------------------------------
        # ORIGINAL DATA
        # --------------------------------------------------------

        original_rows = [
            item.get(
                "original_data",
                {},
            )
            for item in predictions_data
        ]

        # --------------------------------------------------------
        # CONTRACT
        # --------------------------------------------------------

        contract_counts = {
            "Month-to-month": 0,
            "One year": 0,
            "Two year": 0,
        }

        for row in original_rows:

            contract = str(
                row.get(
                    "Contract_Type",
                    "",
                )
            ).strip()

            if contract in contract_counts:

                contract_counts[
                    contract
                ] += 1

            elif self._is_one(
                row.get(
                    "Contract_Type_Month-to-month"
                )
            ):

                contract_counts[
                    "Month-to-month"
                ] += 1

            elif self._is_one(
                row.get(
                    "Contract_Type_One year"
                )
            ):

                contract_counts[
                    "One year"
                ] += 1

            elif self._is_one(
                row.get(
                    "Contract_Type_Two year"
                )
            ):

                contract_counts[
                    "Two year"
                ] += 1

        # --------------------------------------------------------
        # PAYMENT
        # --------------------------------------------------------

        payment_counts = {
            "Bank transfer (auto)": 0,
            "Credit card (auto)": 0,
            "Electronic check": 0,
            "Mailed check": 0,
        }

        for row in original_rows:

            payment = str(
                row.get(
                    "Payment_Method",
                    "",
                )
            ).strip()

            if payment in payment_counts:

                payment_counts[
                    payment
                ] += 1

            elif self._is_one(
                row.get(
                    "Payment_Method_Bank transfer (auto)"
                )
            ):

                payment_counts[
                    "Bank transfer (auto)"
                ] += 1

            elif self._is_one(
                row.get(
                    "Payment_Method_Credit card (auto)"
                )
            ):

                payment_counts[
                    "Credit card (auto)"
                ] += 1

            elif self._is_one(
                row.get(
                    "Payment_Method_Electronic check"
                )
            ):

                payment_counts[
                    "Electronic check"
                ] += 1

            elif self._is_one(
                row.get(
                    "Payment_Method_Mailed check"
                )
            ):

                payment_counts[
                    "Mailed check"
                ] += 1

        # --------------------------------------------------------
        # TENURE
        # --------------------------------------------------------

        churn_tenures = []
        safe_tenures = []

        for item in predictions_data:

            row = item.get(
                "original_data",
                {},
            )

            try:
                tenure = float(
                    row.get(
                        "Tenure_Months",
                        0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            if int(
                item.get(
                    "prediction",
                    0,
                )
            ) == 1:

                churn_tenures.append(
                    tenure
                )

            else:

                safe_tenures.append(
                    tenure
                )

        average_tenure_churn = (
            round(
                sum(churn_tenures)
                / len(churn_tenures),
                2,
            )
            if churn_tenures
            else 0
        )

        average_tenure_no_churn = (
            round(
                sum(safe_tenures)
                / len(safe_tenures),
                2,
            )
            if safe_tenures
            else 0
        )

        # --------------------------------------------------------
        # MONTHLY BILL
        # --------------------------------------------------------

        monthly_bills = []

        for row in original_rows:

            value = row.get(
                "Current_Monthly_Bill"
            )

            try:
                monthly_bills.append(
                    float(value)
                )
            except (
                TypeError,
                ValueError,
            ):
                pass

        if monthly_bills:

            monthly_distribution = {
                "min": round(
                    min(monthly_bills),
                    2,
                ),
                "max": round(
                    max(monthly_bills),
                    2,
                ),
                "avg": round(
                    sum(monthly_bills)
                    / len(monthly_bills),
                    2,
                ),
            }

        else:

            monthly_distribution = {
                "min": 0,
                "max": 0,
                "avg": 0,
            }

        # --------------------------------------------------------
        # CHURN DRIVERS
        # --------------------------------------------------------

        driver_definitions = [
            (
                "Short Tenure",
                lambda r:
                    self._number(
                        r.get(
                            "Tenure_Months"
                        )
                    ) < 12,
            ),
            (
                "Late Payments",
                lambda r:
                    self._number(
                        r.get(
                            "Late_Payments"
                        )
                    ) > 0,
            ),
            (
                "Support Tickets",
                lambda r:
                    self._number(
                        r.get(
                            "Support_Tickets"
                        )
                    ) > 0,
            ),
            (
                "Customer Complaints",
                lambda r:
                    self._number(
                        r.get(
                            "Complaints"
                        )
                    ) > 0,
            ),
            (
                "Bill Increase",
                lambda r:
                    self._number(
                        r.get(
                            "Bill_Change_Pct"
                        )
                    ) > 10,
            ),
            (
                "Network Issues",
                lambda r:
                    self._number(
                        r.get(
                            "Network_Issues"
                        )
                    ) > 0,
            ),
            (
                "Service Downtime",
                lambda r:
                    self._number(
                        r.get(
                            "Downtime_Hours"
                        )
                    ) > 5,
            ),
        ]

        churn_drivers = []

        for name, condition in driver_definitions:

            affected = 0
            driver_churned = 0

            for item in predictions_data:

                row = item.get(
                    "original_data",
                    {},
                )

                try:
                    matches = condition(row)
                except Exception:
                    matches = False

                if matches:

                    affected += 1

                    if int(
                        item.get(
                            "prediction",
                            0,
                        )
                    ) == 1:

                        driver_churned += 1

            if affected > 0:

                rate = (
                    driver_churned
                    / affected
                ) * 100

                churn_drivers.append({
                    "name": name,
                    "affected_customers":
                        affected,
                    "churned_customers":
                        driver_churned,
                    "churn_rate":
                        round(rate, 2),
                })

        churn_drivers.sort(
            key=lambda x:
                x["churn_rate"],
            reverse=True,
        )

        return {
            "total_customers": total,
            "churned_customers": churned,
            "safe_customers": safe,

            "churn_rate": round(
                (
                    churned
                    / total
                ) * 100,
                2,
            ),

            "average_probability":
                round(
                    average_probability,
                    4,
                ),

            "churn_risk": {
                "high": high_risk,
                "medium": medium_risk,
                "low": low_risk,
            },

            "churn_by_contract":
                contract_counts,

            "churn_by_internet_service":
                {},

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
    # HELPERS
    # ============================================================

    @staticmethod
    def _number(value: Any) -> float:

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    @staticmethod
    def _is_one(value: Any) -> bool:

        if value is None:
            return False

        if isinstance(value, bool):
            return value

        try:
            return float(value) == 1

        except (
            TypeError,
            ValueError,
        ):
            return str(
                value
            ).strip().lower() in {
                "1",
                "true",
                "yes",
            }

    # ============================================================
    # MODEL INFORMATION
    # ============================================================

    def get_model_info(
        self,
    ) -> Dict[str, Any]:

        return self.model_loader.get_model_info()


_predictor_instance = None


def get_predictor(models_dir: str):

    global _predictor_instance

    if _predictor_instance is None:

        _predictor_instance = ChurnPredictor(
            models_dir
        )

    return _predictor_instance
