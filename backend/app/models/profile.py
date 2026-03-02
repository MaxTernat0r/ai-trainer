import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_level: Mapped[str] = mapped_column(String(30), default="beginner")
    goal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sport_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    activity_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    target_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    equipment_available: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_days_per_week: Mapped[int | None] = mapped_column(nullable=True)
    meals_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    food_allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    disliked_foods: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_health_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")  # type: ignore[name-defined]  # noqa: F821
    medical_restrictions: Mapped[list["UserMedicalRestriction"]] = relationship(
        back_populates="profile", lazy="selectin"
    )


class MedicalRestriction(BaseModel):
    __tablename__ = "medical_restrictions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class UserMedicalRestriction(BaseModel):
    __tablename__ = "user_medical_restrictions"

    user_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False
    )
    medical_restriction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medical_restrictions.id", ondelete="CASCADE"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="medical_restrictions")
    restriction: Mapped["MedicalRestriction"] = relationship(lazy="selectin")
