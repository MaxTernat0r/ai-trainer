from datetime import date

from pydantic import BaseModel


class WeightLogCreate(BaseModel):
    weight_kg: float
    logged_at: date


class WeightLogRead(BaseModel):
    id: str
    weight_kg: float
    logged_at: date

    model_config = {"from_attributes": True}


class MeasurementCreate(BaseModel):
    measurement_type: str
    value_cm: float
    logged_at: date


class MeasurementRead(BaseModel):
    id: str
    measurement_type: str
    value_cm: float
    logged_at: date

    model_config = {"from_attributes": True}


class DashboardData(BaseModel):
    current_weight: float | None = None
    weight_change_30d: float | None = None
    workouts_this_week: int = 0
    calories_today: float = 0
    protein_today: float = 0
    streak_days: int = 0
