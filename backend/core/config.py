from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Location of backend/.env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):

    # App
    APP_NAME: str = "Churn Prediction API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Auth / JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # ML
    MODEL_PATH: str = "backend/ml/saved_models/best_churn_model.pkl"

    # Pydantic settings
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()