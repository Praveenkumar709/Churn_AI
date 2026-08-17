from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.connection import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    customer_id = Column(
        String,
        index=True,
        nullable=False,
    )

    churn_probability = Column(
        Float,
        nullable=False,
    )

    churn_label = Column(
        String,
        nullable=False,
    )

    churn_reason = Column(
        String,
        nullable=True,
    )

    recommendations = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        index=True,
    )

    owner = relationship(
        "User",
        back_populates="predictions",
    )