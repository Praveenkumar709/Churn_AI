from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, report
from core.config import settings
from database.connection import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(report.router)

try:
    from api import predict, upload

    app.include_router(predict.router)
    app.include_router(upload.router)

    print("ML routes loaded successfully")

except Exception as exc:
    print(f"ML routes disabled during startup: {exc}")


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Churn Prediction API is running",
    }