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
                f"Churn model not found: {model_path}. Attempting auto-training..."
            )
            if not self._auto_train_model(model_path):
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

    def _auto_train_model(self, model_path):
        """Auto-train Logistic Regression model if missing."""
        try:
            import pandas as pd
            from sklearn.linear_model import LogisticRegression
            from ml.deployment_preprocessing import prepare_for_model

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            candidate_paths = [
                os.path.join(base_dir, "backend", "ml", "data", "dataset.csv"),
                os.path.join(base_dir, "data", "telecom_churn_100k.csv"),
                os.path.join(base_dir, "sample_customer_churn.csv"),
            ]

            dataset_path = None
            for path in candidate_paths:
                if os.path.exists(path):
                    dataset_path = path
                    break

            if not dataset_path:
                print("No dataset found for auto-training.")
                return False

            print(f"Auto-training model on dataset: {dataset_path}")
            df = pd.read_csv(dataset_path)

            if "Churn" not in df.columns:
                print("Dataset missing 'Churn' column for training.")
                return False

            y = pd.to_numeric(df["Churn"], errors="coerce").fillna(0).astype(int)
            X = prepare_for_model(df)

            model = LogisticRegression(max_iter=1000, random_state=42)
            model.fit(X, y)

            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(model, model_path)
            self.best_model = model
            print(f"Auto-trained model saved to {model_path}")
            return True
        except Exception as exc:
            print(f"Auto-training failed: {exc}")
            return False
