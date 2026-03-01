import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_model import BaseModel


class WeightLog(BaseModel):
    __tablename__ = "weight_logs"
    __table_args__ = (Index("ix_weight_logs_user_date", "user_id", "logged_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    logged_at: Mapped[date] = mapped_column(Date, nullable=False)


class MeasurementLog(BaseModel):
    __tablename__ = "measurement_logs"
    __table_args__ = (
        Index("ix_measurement_logs_user_type_date", "user_id", "measurement_type", "logged_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    measurement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    value_cm: Mapped[float] = mapped_column(Float, nullable=False)
    logged_at: Mapped[date] = mapped_column(Date, nullable=False)
