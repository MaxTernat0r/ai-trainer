from datetime import date, datetime

from pydantic import BaseModel


class WeightLogCreate(BaseModel):
    weight_kg: float
    logged_at: str | None = None


class WeightLogRead(BaseModel):
    id: str
    weight_kg: float
    logged_at: date

    model_config = {"from_attributes": True}


class MeasurementCreate(BaseModel):
    measurement_type: str
    value_cm: float
    logged_at: str | None = None


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
