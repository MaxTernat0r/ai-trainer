from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.validators import (
    Periodization,
    TRAINING_DAYS_MAX,
    TRAINING_DAYS_MIN,
    WORKOUT_WEEKS_MAX,
    WORKOUT_WEEKS_MIN,
)


_RESCHEDULE_FUTURE_LIMIT_DAYS = 365 * 5


class GenerateWorkoutRequest(BaseModel):
    weeks: int = Field(4, ge=WORKOUT_WEEKS_MIN, le=WORKOUT_WEEKS_MAX)
    days_per_week: int = Field(3, ge=TRAINING_DAYS_MIN, le=TRAINING_DAYS_MAX)
    periodization: Periodization = "linear"


class ExerciseSetLog(BaseModel):
    set_number: int = Field(ge=1, le=100)
    reps_completed: int | None = Field(None, ge=0, le=1000)
    weight_kg: float | None = Field(None, ge=0, le=1000)
    duration_seconds: int | None = Field(None, ge=0, le=36000)
    is_warmup: bool = False
    scheduled_workout_id: UUID | None = None

    @model_validator(mode="after")
    def _require_reps_or_duration(self) -> "ExerciseSetLog":
        # Set must register some kind of work. Allow reps=0 only for warmups
        # (e.g. a stretch or empty-bar set) or when duration_seconds was logged
        # (timed exercise like plank). Otherwise require reps >= 1.
        has_duration = self.duration_seconds is not None and self.duration_seconds > 0
        has_reps = self.reps_completed is not None and self.reps_completed >= 1
        if not has_reps and not has_duration and not self.is_warmup:
            raise ValueError(
                "reps_completed must be >= 1 (or set is_warmup or duration_seconds)"
            )
        return self


class WorkoutExerciseRead(BaseModel):
    id: str
    exercise_id: str
    exercise_name: str | None = None
    exercise_name_ru: str | None = None
    order_index: int
    target_sets: int
    target_reps: str
    target_rest_seconds: int | None = None
    notes: str | None = None
    logged_sets: list["ExerciseSetRead"] = []

    model_config = {"from_attributes": True}


class ExerciseSetRead(BaseModel):
    id: str
    set_number: int
    reps_completed: int | None = None
    weight_kg: float | None = None
    duration_seconds: int | None = None
    is_warmup: bool
    completed_at: datetime

    model_config = {"from_attributes": True}


class WorkoutSessionRead(BaseModel):
    id: str
    day_number: int
    name: str
    notes: str | None = None
    order_index: int
    scheduled_date: date | None = None
    exercises: list[WorkoutExerciseRead] = []

    model_config = {"from_attributes": True}


class RescheduleRequest(BaseModel):
    scheduled_date: date

    @field_validator("scheduled_date")
    @classmethod
    def _within_window(cls, v: date) -> date:
        # Allow today; reject anything more than a day in the past to prevent
        # streak/calendar corruption while leaving room for late-night fixes.
        # Cap the future too so a typo can't push the entry past the visible
        # calendar (year clamp is 1970..2100) and become unreachable from the UI.
        today = date.today()
        if v.toordinal() < today.toordinal() - 1:
            raise ValueError("scheduled_date cannot be in the past")
        if v.toordinal() > today.toordinal() + _RESCHEDULE_FUTURE_LIMIT_DAYS:
            raise ValueError("scheduled_date is too far in the future")
        return v


class AddScheduleEntryRequest(BaseModel):
    session_id: UUID
    scheduled_date: date
    is_completed: bool = False

    @field_validator("scheduled_date")
    @classmethod
    def _within_window(cls, v: date) -> date:
        # Mirror RescheduleRequest: no backdating completed workouts to game
        # streaks/analytics, no scheduling decades into the future.
        today = date.today()
        if v.toordinal() < today.toordinal() - 1:
            raise ValueError("scheduled_date cannot be in the past")
        if v.toordinal() > today.toordinal() + _RESCHEDULE_FUTURE_LIMIT_DAYS:
            raise ValueError("scheduled_date is too far in the future")
        return v


class CompleteEntryRequest(BaseModel):
    is_completed: bool | None = None


class CalendarEntry(BaseModel):
    id: str  # scheduled_workout id
    session_id: str
    session_name: str
    day_number: int
    week_number: int
    scheduled_date: date
    plan_id: str
    plan_title: str
    is_completed: bool = False


class WorkoutPlanRead(BaseModel):
    id: str
    title: str
    description: str | None = None
    goal: str
    difficulty: str
    duration_weeks: int
    days_per_week: int
    is_ai_generated: bool
    is_active: bool
    sessions: list[WorkoutSessionRead] = []

    model_config = {"from_attributes": True}


class WorkoutPlanListRead(BaseModel):
    id: str
    title: str
    goal: str
    difficulty: str
    duration_weeks: int
    days_per_week: int
    is_ai_generated: bool
    is_active: bool

    model_config = {"from_attributes": True}
