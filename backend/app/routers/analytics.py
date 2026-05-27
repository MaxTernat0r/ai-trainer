from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.base  # noqa: F401 — ensure all models are registered for relationships

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.analytics import MeasurementLog, WeightLog
from app.models.nutrition import NutritionLog
from app.models.profile import UserProfile
from app.models.exercise import Exercise
from app.models.workout import ExerciseSet, ScheduledWorkout, WorkoutExercise, WorkoutPlan, WorkoutSession
from app.models.user import User
from app.schemas.analytics import (
    BestSetPoint,
    CompletedExerciseBrief,
    CompletedSession,
    DashboardData,
    ExerciseSummary,
    MeasurementCreate,
    MeasurementRead,
    SessionSets,
    SetDetail,
    WeightLogCreate,
    WeightLogRead,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _resolve_current_weight(latest_weight: WeightLog | None, profile: UserProfile | None) -> float | None:
    if latest_weight is not None:
        return latest_weight.weight_kg
    if profile is not None:
        return profile.weight_kg
    return None


def _parse_optional_date(value: str | None) -> date:
    """Parse an optional ISO date string, falling back to today."""
    if value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            pass
    return date.today()


@router.post("/weight", response_model=WeightLogRead)
async def log_weight(
    data: WeightLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    logged_date = _parse_optional_date(data.logged_at)

    # Idempotent per day: ON CONFLICT (user_id, logged_at) DO UPDATE.
    # The unique index uq_weight_logs_user_date backs this.
    # Doing it as a single statement avoids the post-IntegrityError rollback
    # path that breaks the asyncpg greenlet under FastAPI's session dep.
    stmt = (
        pg_insert(WeightLog)
        .values(user_id=user.id, weight_kg=data.weight_kg, logged_at=logged_date)
        .on_conflict_do_update(
            index_elements=["user_id", "logged_at"],
            set_={"weight_kg": data.weight_kg},
        )
        .returning(WeightLog.id, WeightLog.weight_kg, WeightLog.logged_at)
    )
    row = (await db.execute(stmt)).one()
    return WeightLogRead(id=str(row.id), weight_kg=row.weight_kg, logged_at=row.logged_at)


@router.get("/weight", response_model=list[WeightLogRead])
async def get_weight_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get weight history. Frontend calls GET /analytics/weight with NO query params."""
    result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id)
        .order_by(WeightLog.logged_at)
    )
    return [
        WeightLogRead(id=str(w.id), weight_kg=w.weight_kg, logged_at=w.logged_at)
        for w in result.scalars()
    ]


@router.delete("/weight/{log_id}")
async def delete_weight(
    log_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WeightLog).where(WeightLog.id == log_id, WeightLog.user_id == user.id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise NotFoundError("Weight log")
    await db.delete(row)
    return {"detail": "Deleted"}


@router.post("/measurements", response_model=MeasurementRead)
async def log_measurement(
    data: MeasurementCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    logged_date = _parse_optional_date(data.logged_at)

    # ON CONFLICT (user_id, measurement_type, logged_at) DO UPDATE — see
    # log_weight for why we do this in one statement instead of catching
    # IntegrityError. uq_measurement_logs_user_type_date backs this.
    stmt = (
        pg_insert(MeasurementLog)
        .values(
            user_id=user.id,
            measurement_type=data.measurement_type,
            value_cm=data.value_cm,
            logged_at=logged_date,
        )
        .on_conflict_do_update(
            index_elements=["user_id", "measurement_type", "logged_at"],
            set_={"value_cm": data.value_cm},
        )
        .returning(
            MeasurementLog.id,
            MeasurementLog.measurement_type,
            MeasurementLog.value_cm,
            MeasurementLog.logged_at,
        )
    )
    row = (await db.execute(stmt)).one()
    return MeasurementRead(
        id=str(row.id),
        measurement_type=row.measurement_type,
        value_cm=row.value_cm,
        logged_at=row.logged_at,
    )


@router.get("/measurements", response_model=list[MeasurementRead])
async def get_measurements(
    type: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get measurements. Frontend calls GET /analytics/measurements?type=... (optional)."""
    query = select(MeasurementLog).where(MeasurementLog.user_id == user.id)
    if type:
        query = query.where(MeasurementLog.measurement_type == type)
    query = query.order_by(MeasurementLog.logged_at)

    result = await db.execute(query)
    return [
        MeasurementRead(
            id=str(m.id),
            measurement_type=m.measurement_type,
            value_cm=m.value_cm,
            logged_at=m.logged_at,
        )
        for m in result.scalars()
    ]


@router.delete("/measurements/{log_id}")
async def delete_measurement(
    log_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(MeasurementLog).where(
            MeasurementLog.id == log_id, MeasurementLog.user_id == user.id
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise NotFoundError("Measurement")
    await db.delete(row)
    return {"detail": "Deleted"}


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    week_start = today - timedelta(days=today.weekday())  # Monday of current week
    # ExerciseSet.completed_at is TIMESTAMPTZ; comparing to a naive datetime
    # makes Postgres interpret it in the session timezone (UTC under asyncpg)
    # which silently shifts the boundary for users in other timezones.
    week_start_dt = datetime.combine(week_start, time.min, tzinfo=timezone.utc)

    # Latest weight
    weight_result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id)
        .order_by(WeightLog.logged_at.desc())
        .limit(1)
    )
    latest_weight = weight_result.scalar_one_or_none()

    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    # Weight 30 days ago (closest entry before that date)
    weight_change_30d = None
    if latest_weight:
        old_weight_result = await db.execute(
            select(WeightLog)
            .where(
                WeightLog.user_id == user.id,
                WeightLog.logged_at <= thirty_days_ago,
            )
            .order_by(WeightLog.logged_at.desc())
            .limit(1)
        )
        old_weight = old_weight_result.scalar_one_or_none()
        if old_weight:
            weight_change_30d = round(latest_weight.weight_kg - old_weight.weight_kg, 1)

    # Today's nutrition
    nutrition_result = await db.execute(
        select(
            func.coalesce(func.sum(NutritionLog.calories), 0),
            func.coalesce(func.sum(NutritionLog.protein_g), 0),
        ).where(NutritionLog.user_id == user.id, NutritionLog.logged_at == today)
    )
    cal_today, protein_today = nutrition_result.one()

    # Workouts this week: count distinct days with logged exercise sets this week
    # filtered by the current user's workout plans (ownership chain).
    days_result = await db.execute(
        select(
            func.count(
                func.distinct(func.date_trunc("day", ExerciseSet.completed_at))
            )
        )
        .select_from(ExerciseSet)
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            ExerciseSet.completed_at >= week_start_dt,
        )
    )
    workouts_week = days_result.scalar() or 0

    # Streak: consecutive days with any logged activity (nutrition or exercise).
    # Old version fired up to 732 sequential queries — now we fetch the last
    # 366 distinct activity-days in two queries and walk them in Python.
    streak_window_start = today - timedelta(days=365)
    nutrition_days_result = await db.execute(
        select(func.distinct(NutritionLog.logged_at)).where(
            NutritionLog.user_id == user.id,
            NutritionLog.logged_at >= streak_window_start,
            NutritionLog.logged_at <= today,
        )
    )
    activity_days: set[date] = set(nutrition_days_result.scalars().all())

    set_days_result = await db.execute(
        select(
            func.distinct(func.date_trunc("day", ExerciseSet.completed_at))
        )
        .select_from(ExerciseSet)
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            ExerciseSet.completed_at >= datetime.combine(streak_window_start, time.min, tzinfo=timezone.utc),
        )
    )
    for day_dt in set_days_result.scalars().all():
        if day_dt is not None:
            activity_days.add(day_dt.date() if hasattr(day_dt, "date") else day_dt)

    streak_days = 0
    check_date = today
    while check_date in activity_days:
        streak_days += 1
        check_date -= timedelta(days=1)

    return DashboardData(
        current_weight=_resolve_current_weight(latest_weight, profile),
        weight_change_30d=weight_change_30d,
        workouts_this_week=workouts_week,
        calories_today=float(cal_today),
        protein_today=float(protein_today),
        streak_days=streak_days,
    )


# --- Exercise progress endpoints ---


@router.get("/exercises-summary", response_model=list[ExerciseSummary])
async def get_trained_exercises(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """List exercises that the user has logged at least one set for."""
    result = await db.execute(
        select(
            Exercise.id,
            Exercise.name,
            Exercise.name_ru,
            func.count(ExerciseSet.id).label("total_sets"),
        )
        .select_from(ExerciseSet)
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .join(Exercise, WorkoutExercise.exercise_id == Exercise.id)
        .where(WorkoutPlan.user_id == user.id)
        .group_by(Exercise.id, Exercise.name, Exercise.name_ru)
        .order_by(func.count(ExerciseSet.id).desc())
    )
    return [
        ExerciseSummary(
            exercise_id=str(row.id),
            exercise_name=row.name,
            exercise_name_ru=row.name_ru,
            total_sets=row.total_sets,
        )
        for row in result
    ]


@router.get("/exercise-progress/{exercise_id}", response_model=list[BestSetPoint])
async def get_exercise_progress(
    exercise_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get best set per training day for a given exercise (global progress chart).

    "Best set" = highest volume (weight_kg * reps_completed). If weight is null,
    falls back to most reps.
    """
    result = await db.execute(
        select(
            ExerciseSet.id,
            ExerciseSet.weight_kg,
            ExerciseSet.reps_completed,
            ExerciseSet.completed_at,
            WorkoutSession.name.label("session_name"),
        )
        .select_from(ExerciseSet)
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            WorkoutExercise.exercise_id == exercise_id,
            ExerciseSet.is_warmup == False,  # noqa: E712
        )
        .order_by(ExerciseSet.completed_at)
    )
    rows = result.all()

    # Group by day, keep the best set per day
    from collections import defaultdict
    day_sets: dict[date, list] = defaultdict(list)
    for row in rows:
        day = row.completed_at.date()
        day_sets[day].append(row)

    points = []
    for day in sorted(day_sets.keys()):
        sets = day_sets[day]
        # Pick best set by volume (weight × reps), fallback to reps
        best = max(
            sets,
            key=lambda s: (
                (s.weight_kg or 0) * (s.reps_completed or 0),
                s.reps_completed or 0,
            ),
        )
        weight = best.weight_kg
        reps = best.reps_completed
        volume = (weight or 0) * (reps or 0)
        points.append(BestSetPoint(
            date=day,
            weight_kg=weight,
            reps_completed=reps,
            volume=volume,
            session_name=best.session_name,
        ))

    return points


@router.get("/exercise-sessions/{exercise_id}", response_model=list[SessionSets])
async def get_exercise_sessions(
    exercise_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get set-by-set data for recent sessions containing a given exercise.

    Groups sets by scheduled_workout_id so each workout occurrence is separate.
    """
    from collections import defaultdict

    # Find workout_exercise records for this exercise belonging to the user
    we_result = await db.execute(
        select(WorkoutExercise.id, WorkoutSession.name)
        .select_from(WorkoutExercise)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            WorkoutExercise.exercise_id == exercise_id,
        )
    )
    we_rows = we_result.all()

    if not we_rows:
        return []

    we_ids = [row.id for row in we_rows]
    we_name = {row.id: row.name for row in we_rows}

    # Load all sets for these workout_exercise records
    sets_result = await db.execute(
        select(ExerciseSet)
        .where(ExerciseSet.workout_exercise_id.in_(we_ids))
        .order_by(ExerciseSet.completed_at, ExerciseSet.set_number)
    )
    all_sets = sets_result.scalars().all()

    # Group sets by (scheduled_workout_id, workout_exercise_id)
    # Sets without scheduled_workout_id fall back to workout_exercise_id only
    grouped: dict[tuple, list] = defaultdict(list)
    for s in all_sets:
        key = (s.scheduled_workout_id, s.workout_exercise_id)
        grouped[key].append(s)

    sessions = []
    for (sw_id, we_id), sets in grouped.items():
        if not sets:
            continue
        sessions.append(SessionSets(
            session_date=sets[0].completed_at,
            session_name=we_name.get(we_id, ""),
            workout_exercise_id=str(we_id),
            scheduled_workout_id=str(sw_id) if sw_id else None,
            sets=[
                SetDetail(
                    set_number=s.set_number,
                    reps_completed=s.reps_completed,
                    weight_kg=s.weight_kg,
                    duration_seconds=s.duration_seconds,
                    is_warmup=s.is_warmup,
                    completed_at=s.completed_at,
                )
                for s in sets
            ],
        ))

    # Sort chronologically and limit
    sessions.sort(key=lambda s: s.session_date)
    return sessions[-limit:]


@router.get("/completed-sessions", response_model=list[CompletedSession])
async def get_completed_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """List workout occurrences that have at least one logged set.

    Each entry corresponds to a ScheduledWorkout and includes the exercises
    that were performed with a count of logged sets.
    """
    from collections import defaultdict

    # Find all scheduled_workout_ids that have logged sets
    sw_result = await db.execute(
        select(
            ScheduledWorkout.id,
            ScheduledWorkout.scheduled_date,
            WorkoutSession.name,
        )
        .select_from(ScheduledWorkout)
        .join(WorkoutSession, ScheduledWorkout.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(WorkoutPlan.user_id == user.id)
        .order_by(ScheduledWorkout.scheduled_date.desc())
    )
    sw_rows = sw_result.all()

    if not sw_rows:
        return []

    sw_ids = [row.id for row in sw_rows]
    sw_meta = {row.id: row for row in sw_rows}

    # For each scheduled workout, find exercises with logged sets
    sets_result = await db.execute(
        select(
            ExerciseSet.scheduled_workout_id,
            ExerciseSet.workout_exercise_id,
            WorkoutExercise.exercise_id,
            Exercise.name_ru,
            func.count(ExerciseSet.id).label("sets_count"),
        )
        .select_from(ExerciseSet)
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(Exercise, WorkoutExercise.exercise_id == Exercise.id)
        .where(ExerciseSet.scheduled_workout_id.in_(sw_ids))
        .group_by(
            ExerciseSet.scheduled_workout_id,
            ExerciseSet.workout_exercise_id,
            WorkoutExercise.exercise_id,
            Exercise.name_ru,
        )
    )
    set_rows = sets_result.all()

    # Group by scheduled_workout_id
    grouped: dict[str, list] = defaultdict(list)
    for row in set_rows:
        grouped[row.scheduled_workout_id].append(
            CompletedExerciseBrief(
                exercise_id=str(row.exercise_id),
                exercise_name_ru=row.name_ru,
                workout_exercise_id=str(row.workout_exercise_id),
                sets_count=row.sets_count,
            )
        )

    sessions = []
    for sw_id in sw_ids:
        exercises = grouped.get(sw_id, [])
        if not exercises:
            continue
        meta = sw_meta[sw_id]
        sessions.append(CompletedSession(
            entry_id=str(sw_id),
            session_name=meta.name,
            scheduled_date=meta.scheduled_date,
            exercises=exercises,
        ))

    return sessions
