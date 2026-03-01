from datetime import date

from pydantic import BaseModel


class ProfileCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    experience_level: str = "beginner"
    goal: str | None = None
    sport_type: str | None = None
    activity_level: str | None = None
    target_weight_kg: float | None = None
    equipment_available: str | None = None
    training_days_per_week: int | None = None
    medical_restriction_ids: list[str] | None = None


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
    medical_restrictions: list["MedicalRestrictionRead"] = []

    model_config = {"from_attributes": True}


class ProfileUpdate(ProfileCreate):
    pass


class MedicalRestrictionRead(BaseModel):
    id: str
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}
