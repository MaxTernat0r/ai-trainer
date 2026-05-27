from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.core.validators import (
    MEASUREMENT_CM_MAX,
    MEASUREMENT_CM_MIN,
    MeasurementType,
    WEIGHT_KG_MAX,
    WEIGHT_KG_MIN,
)


class WeightLogCreate(BaseModel):
    weight_kg: float = Field(ge=WEIGHT_KG_MIN, le=WEIGHT_KG_MAX)
    logged_at: str | None = None

    @field_validator("logged_at")
    @classmethod
    def _not_future(cls, v: str | None) -> str | None:
        if not v:
            return v
        try:
            parsed = datetime.fromisoformat(v.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError) as exc:
            raise ValueError("logged_at must be ISO date") from exc
        if parsed > date.today():
            raise ValueError("logged_at cannot be in the future")
        return v


class WeightLogRead(BaseModel):
    id: str
    weight_kg: float
    logged_at: date

    model_config = {"from_attributes": True}


class MeasurementCreate(BaseModel):
    measurement_type: MeasurementType
    value_cm: float = Field(ge=MEASUREMENT_CM_MIN, le=MEASUREMENT_CM_MAX)
    logged_at: str | None = None

    @field_validator("logged_at")
    @classmethod
    def _not_future(cls, v: str | None) -> str | None:
        if not v:
            return v
        try:
            parsed = datetime.fromisoformat(v.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError) as exc:
            raise ValueError("logged_at must be ISO date") from exc
        if parsed > date.today():
            raise ValueError("logged_at cannot be in the future")
        return v


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


# --- Exercise progress analytics ---


class ExerciseSummary(BaseModel):
    """An exercise the user has logged at least one set for."""
    exercise_id: str
    exercise_name: str
    exercise_name_ru: str
    total_sets: int


class SetDetail(BaseModel):
    """A single logged set within a session."""
    set_number: int
    reps_completed: int | None = None
    weight_kg: float | None = None
    duration_seconds: int | None = None
    is_warmup: bool = False
    completed_at: datetime


class SessionSets(BaseModel):
    """All sets for a given exercise in a single workout session."""
    session_date: datetime
    session_name: str
    workout_exercise_id: str
    scheduled_workout_id: str | None = None
    sets: list[SetDetail]


class BestSetPoint(BaseModel):
    """Best set for an exercise on a given day (for global progress chart)."""
    date: date
    weight_kg: float | None = None
    reps_completed: int | None = None
    volume: float = 0
    session_name: str = ""


# --- Workout history (per-session drill-down) ---


class CompletedExerciseBrief(BaseModel):
    """Exercise within a completed session (for picker)."""
    exercise_id: str
    exercise_name_ru: str
    workout_exercise_id: str
    sets_count: int


class CompletedSession(BaseModel):
    """A single completed workout occurrence."""
    entry_id: str
    session_name: str
    scheduled_date: date
    exercises: list[CompletedExerciseBrief]
