import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel


class WorkoutPlan(BaseModel):
    __tablename__ = "workout_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    duration_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    days_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_prompt_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="workout_plans")  # type: ignore[name-defined]  # noqa: F821
    sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="workout_plan", lazy="selectin", order_by="WorkoutSession.order_index"
    )


class WorkoutSession(BaseModel):
    __tablename__ = "workout_sessions"

    workout_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    workout_plan: Mapped["WorkoutPlan"] = relationship(back_populates="sessions")
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout_session", lazy="selectin", order_by="WorkoutExercise.order_index"
    )


class WorkoutExercise(BaseModel):
    __tablename__ = "workout_exercises"

    workout_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    target_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    target_reps: Mapped[str] = mapped_column(String(20), nullable=False)
    target_rest_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    workout_session: Mapped["WorkoutSession"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(lazy="selectin")  # type: ignore[name-defined]  # noqa: F821
    logged_sets: Mapped[list["ExerciseSet"]] = relationship(back_populates="workout_exercise", lazy="selectin")


class ScheduledWorkout(BaseModel):
    """A single scheduled occurrence of a workout session.

    When a plan is distributed to the calendar, one row is created per
    session per week (e.g. 8 weeks × 2 days/week = 16 rows).  Each row
    can be individually rescheduled.
    """
    __tablename__ = "scheduled_workouts"

    workout_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False
    )
    workout_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    workout_plan: Mapped["WorkoutPlan"] = relationship(lazy="selectin")
    workout_session: Mapped["WorkoutSession"] = relationship(lazy="selectin")


class ExerciseSet(BaseModel):
    __tablename__ = "exercise_sets"

    workout_exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False
    )
    scheduled_workout_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scheduled_workouts.id", ondelete="SET NULL"), nullable=True
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_warmup: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="logged_sets")
    scheduled_workout: Mapped["ScheduledWorkout | None"] = relationship()
