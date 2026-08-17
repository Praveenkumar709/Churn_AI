import joblib
import os


class ModelLoader:
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.best_model = None
        self.preprocessor = None

        self.best_model_name = "Logistic Regression"
        self.best_accuracy = 0.9125
        self.models_loaded = False

        self.model_filename = "logistic_regression_100k.joblib"

    def load_preprocessor(self):
        """
        The 100k Logistic Regression model uses
        deployment_preprocessing.py directly.
        """

        print(
            "Using deployment preprocessing"
        )

        self.preprocessor = None

        return True

    def load_best_model(self):
        """Load the 100k Logistic Regression model."""

        model_path = os.path.join(
            self.models_dir,
            self.model_filename,
        )

        if not os.path.exists(model_path):
            print(
                f"Churn model not found: {model_path}"
            )
            return False

        try:
            self.best_model = joblib.load(
                model_path
            )

            print(
                "100k Logistic Regression model "
                "loaded successfully"
            )

            print(
                f"Model: {type(self.best_model).__name__}"
            )

            if hasattr(
                self.best_model,
                "n_features_in_",
            ):
                print(
                    f"Model features: "
                    f"{self.best_model.n_features_in_}"
                )

            return True

        except Exception as exc:
            print(
                f"Failed to load churn model: {exc}"
            )
            return False

    def load_specific_model(self, model_name):
        """Load the Logistic Regression model."""

        if model_name not in [
            "LogisticRegression",
            "Logistic Regression",
        ]:
            print(
                f"Unknown model name: {model_name}"
            )
            return None

        model_path = os.path.join(
            self.models_dir,
            self.model_filename,
        )

        if not os.path.exists(model_path):
            print(
                f"Model not found: {model_path}"
            )
            return None

        try:
            model = joblib.load(
                model_path
            )

            print(
                "Logistic Regression model "
                "loaded successfully"
            )

            return model

        except Exception as exc:
            print(
                f"Failed to load model: {exc}"
            )
            return None

    def load_all(self):
        """Load preprocessing and the 100k model."""

        preprocessor_loaded = (
            self.load_preprocessor()
        )

        model_loaded = (
            self.load_best_model()
        )

        self.models_loaded = (
            preprocessor_loaded
            and model_loaded
        )

        if self.models_loaded:
            print(
                "All ML components loaded successfully"
            )
        else:
            print(
                "Failed to load ML components"
            )

        return self.models_loaded

    def get_model_info(self):
        """Return information about the loaded model."""

        if not self.models_loaded:
            return None

        feature_columns = []

        try:
            from ml.deployment_preprocessing import (
                EXPECTED_FEATURES,
            )

            feature_columns = list(
                EXPECTED_FEATURES
            )

        except Exception:
            pass

        return {
            "model_name": self.best_model_name,
            "accuracy": self.best_accuracy,
            "feature_columns": feature_columns,
        }
