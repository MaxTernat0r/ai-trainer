from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.validators import (
    ActivityLevel,
    EquipmentAvailable,
    ExperienceLevel,
    Gender,
    Goal,
    HEIGHT_CM_MAX,
    HEIGHT_CM_MIN,
    MEALS_PER_DAY_MAX,
    MEALS_PER_DAY_MIN,
    SportType,
    TRAINING_DAYS_MAX,
    TRAINING_DAYS_MIN,
    WEIGHT_KG_MAX,
    WEIGHT_KG_MIN,
)


_FreeText = Annotated[str, Field(max_length=2000)]


class ProfileCreate(BaseModel):
    first_name: str | None = Field(None, max_length=60)
    last_name: str | None = Field(None, max_length=60)
    date_of_birth: date | None = None
    gender: Gender | None = None
    height_cm: float | None = Field(None, ge=HEIGHT_CM_MIN, le=HEIGHT_CM_MAX)
    weight_kg: float | None = Field(None, ge=WEIGHT_KG_MIN, le=WEIGHT_KG_MAX)
    experience_level: ExperienceLevel = "beginner"
    goal: Goal | None = None
    sport_type: SportType | None = None
    activity_level: ActivityLevel | None = None
    target_weight_kg: float | None = Field(None, ge=WEIGHT_KG_MIN, le=WEIGHT_KG_MAX)
    equipment_available: EquipmentAvailable | None = None
    training_days_per_week: int | None = Field(
        None, ge=TRAINING_DAYS_MIN, le=TRAINING_DAYS_MAX
    )
    meals_per_day: int | None = Field(
        None, ge=MEALS_PER_DAY_MIN, le=MEALS_PER_DAY_MAX
    )
    food_allergies: _FreeText | None = None
    disliked_foods: _FreeText | None = None
    custom_health_notes: _FreeText | None = None
    medical_restriction_ids: list[UUID] | None = Field(None, max_length=50)

    @field_validator("date_of_birth")
    @classmethod
    def _dob_not_future(cls, v: date | None) -> date | None:
        if v is not None and v > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return v


class ProfileRead(BaseModel):
    id: str
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    experience_level: str
    goal: str | None = None
    sport_type: str | None = None
    activity_level: str | None = None
    target_weight_kg: float | None = None
    equipment_available: str | None = None
    training_days_per_week: int | None = None
    meals_per_day: int | None = None
    food_allergies: str | None = None
    disliked_foods: str | None = None
    custom_health_notes: str | None = None
    medical_restrictions: list["MedicalRestrictionRead"] = []

    model_config = {"from_attributes": True}


class ProfileUpdate(ProfileCreate):
    pass


class MedicalRestrictionRead(BaseModel):
    id: str
    name: str
    description: str | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}
