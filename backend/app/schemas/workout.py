from datetime import datetime

from pydantic import BaseModel


class GenerateWorkoutRequest(BaseModel):
    weeks: int = 4
    days_per_week: int = 3
    periodization: str = "linear"


class ExerciseSetLog(BaseModel):
    set_number: int
    reps_completed: int | None = None
    weight_kg: float | None = None
    duration_seconds: int | None = None
    is_warmup: bool = False


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
    exercises: list[WorkoutExerciseRead] = []

    model_config = {"from_attributes": True}


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
