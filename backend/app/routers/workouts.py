import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.base  # noqa: F401 — ensure all models are registered for relationships

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workout import ExerciseSet, ScheduledWorkout, WorkoutExercise, WorkoutPlan, WorkoutSession
from app.schemas.workout import (
    AddScheduleEntryRequest,
    CalendarEntry,
    CompleteEntryRequest,
    ExerciseSetLog,
    ExerciseSetRead,
    GenerateWorkoutRequest,
    RescheduleRequest,
    WorkoutExerciseRead,
    WorkoutPlanListRead,
    WorkoutPlanRead,
    WorkoutSessionRead,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/generate", response_model=WorkoutPlanRead)
async def generate_workout(
    data: GenerateWorkoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    from app.services.ai.workout_generator import generate_workout_plan

    plan = await generate_workout_plan(user, data, db)
    return plan


@router.get("/plans", response_model=list[WorkoutPlanListRead])
async def list_plans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.user_id == user.id).order_by(WorkoutPlan.created_at.desc())
    )
    return [
        WorkoutPlanListRead(
            id=str(p.id),
            title=p.title,
            goal=p.goal,
            difficulty=p.difficulty,
            duration_weeks=p.duration_weeks,
            days_per_week=p.days_per_week,
            is_ai_generated=p.is_ai_generated,
            is_active=p.is_active,
        )
        for p in result.scalars()
    ]


@router.get("/plans/{plan_id}", response_model=WorkoutPlanRead)
async def get_plan(
    plan_id: UUID,
    entry_id: str | None = Query(None, description="Filter logged_sets to this ScheduledWorkout"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Workout plan")

    # If entry_id is given, only show sets belonging to that scheduled workout
    entry_uuid: uuid.UUID | None = None
    if entry_id:
        try:
            entry_uuid = uuid.UUID(entry_id)
        except ValueError:
            from app.core.exceptions import BadRequestError
            raise BadRequestError("Invalid entry_id")

    sessions = []
    for s in plan.sessions:
        exercises = []
        for we in s.exercises:
            sets_to_show = we.logged_sets
            if entry_uuid is not None:
                sets_to_show = [es for es in sets_to_show if es.scheduled_workout_id == entry_uuid]

            exercises.append(
                WorkoutExerciseRead(
                    id=str(we.id),
                    exercise_id=str(we.exercise_id),
                    exercise_name=we.exercise.name if we.exercise else None,
                    exercise_name_ru=we.exercise.name_ru if we.exercise else None,
                    order_index=we.order_index,
                    target_sets=we.target_sets,
                    target_reps=we.target_reps,
                    target_rest_seconds=we.target_rest_seconds,
                    notes=we.notes,
                    logged_sets=[
                        ExerciseSetRead(
                            id=str(es.id),
                            set_number=es.set_number,
                            reps_completed=es.reps_completed,
                            weight_kg=es.weight_kg,
                            duration_seconds=es.duration_seconds,
                            is_warmup=es.is_warmup,
                            completed_at=es.completed_at,
                        )
                        for es in sets_to_show
                    ],
                )
            )
        sessions.append(
            WorkoutSessionRead(
                id=str(s.id),
                day_number=s.day_number,
                name=s.name,
                notes=s.notes,
                order_index=s.order_index,
                scheduled_date=s.scheduled_date,
                exercises=exercises,
            )
        )

    return WorkoutPlanRead(
        id=str(plan.id),
        title=plan.title,
        description=plan.description,
        goal=plan.goal,
        difficulty=plan.difficulty,
        duration_weeks=plan.duration_weeks,
        days_per_week=plan.days_per_week,
        is_ai_generated=plan.is_ai_generated,
        is_active=plan.is_active,
        sessions=sessions,
    )


@router.post("/plans/{plan_id}/activate")
async def activate_plan(
    plan_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    from sqlalchemy import text

    from app.core.locks import advisory_key

    # Verify the target plan belongs to the user BEFORE touching anything;
    # otherwise a 404 on a foreign plan_id would still have wiped is_active
    # on every plan the user owns.
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Workout plan")

    # Serialize concurrent activations for the same user. Two simultaneous
    # POSTs for different plan_ids would otherwise both deactivate, both
    # set their own is_active=True, and leave the user with multiple
    # active plans.
    lock_key = advisory_key("activate_workout_plan", str(user.id))
    await db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": lock_key})

    await db.execute(
        update(WorkoutPlan)
        .where(WorkoutPlan.user_id == user.id)
        .values(is_active=False)
    )

    plan.is_active = True
    return {"detail": "Plan activated"}


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Workout plan")
    await db.delete(plan)
    return {"detail": "Plan deleted"}


@router.post("/exercises/{workout_exercise_id}/log")
async def log_set(
    workout_exercise_id: UUID,
    data: ExerciseSetLog,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from app.core.exceptions import BadRequestError, ConflictError

    result = await db.execute(
        select(WorkoutExercise)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutExercise.id == workout_exercise_id,
            WorkoutPlan.user_id == user.id,
        )
    )
    we = result.scalar_one_or_none()
    if not we:
        raise NotFoundError("Workout exercise")

    # Cap unreasonable set numbers. We allow some slack over target_sets so a
    # user adding an extra "burnout" set isn't blocked, but reject obvious
    # garbage so analytics charts don't blow up.
    set_cap = max(20, (we.target_sets or 0) * 3)
    if data.set_number > set_cap:
        raise BadRequestError(
            f"set_number is too large for this exercise (cap {set_cap})"
        )

    if data.scheduled_workout_id:
        sw_owner = await db.execute(
            select(ScheduledWorkout.id)
            .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
            .where(
                ScheduledWorkout.id == data.scheduled_workout_id,
                WorkoutPlan.user_id == user.id,
            )
        )
        if sw_owner.scalar_one_or_none() is None:
            raise NotFoundError("Scheduled workout")

    completed_at = datetime.now(timezone.utc)
    stmt = (
        pg_insert(ExerciseSet)
        .values(
            workout_exercise_id=workout_exercise_id,
            scheduled_workout_id=data.scheduled_workout_id,
            set_number=data.set_number,
            reps_completed=data.reps_completed,
            weight_kg=data.weight_kg,
            duration_seconds=data.duration_seconds,
            is_warmup=data.is_warmup,
            completed_at=completed_at,
        )
        .on_conflict_do_nothing(
            index_elements=["workout_exercise_id", "scheduled_workout_id", "set_number"],
            index_where=ExerciseSet.scheduled_workout_id.isnot(None),
        )
        .returning(ExerciseSet.id)
    )
    inserted_id = (await db.execute(stmt)).scalar_one_or_none()
    if inserted_id is None:
        # Same (workout_exercise, scheduled_workout, set_number) already
        # exists — surface as 409 so the client knows it was a double-tap.
        raise ConflictError("Set already logged")

    exercise_set = ExerciseSet(
        id=inserted_id,
        workout_exercise_id=workout_exercise_id,
        scheduled_workout_id=data.scheduled_workout_id,
        set_number=data.set_number,
        reps_completed=data.reps_completed,
        weight_kg=data.weight_kg,
        duration_seconds=data.duration_seconds,
        is_warmup=data.is_warmup,
        completed_at=completed_at,
    )

    return ExerciseSetRead(
        id=str(exercise_set.id),
        set_number=exercise_set.set_number,
        reps_completed=exercise_set.reps_completed,
        weight_kg=exercise_set.weight_kg,
        duration_seconds=exercise_set.duration_seconds,
        is_warmup=exercise_set.is_warmup,
        completed_at=exercise_set.completed_at,
    )


@router.post("/schedule/start", response_model=CalendarEntry)
async def start_workout(
    data: AddScheduleEntryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Find or create a ScheduledWorkout for the given session + date.

    Used when the user starts a workout: if there's already a scheduled
    entry for this session on this date, return it; otherwise create one.
    """
    from sqlalchemy.exc import IntegrityError

    # Verify session belongs to user and fetch plan title
    result = await db.execute(
        select(WorkoutSession, WorkoutPlan.title)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutSession.id == data.session_id,
            WorkoutPlan.user_id == user.id,
        )
    )
    row = result.one_or_none()
    if not row:
        raise NotFoundError("Workout session")
    session, plan_title = row

    sw = await _find_or_create_scheduled_workout(
        db,
        plan_id=session.workout_plan_id,
        session_id=session.id,
        scheduled_date=data.scheduled_date,
        is_completed=False,
    )

    return CalendarEntry(
        id=str(sw.id),
        session_id=str(session.id),
        session_name=session.name,
        day_number=session.day_number,
        week_number=sw.week_number,
        scheduled_date=sw.scheduled_date,
        plan_id=str(session.workout_plan_id),
        plan_title=plan_title,
        is_completed=sw.is_completed,
    )


async def _find_or_create_scheduled_workout(
    db: AsyncSession,
    *,
    plan_id: uuid.UUID,
    session_id: uuid.UUID,
    scheduled_date,
    is_completed: bool,
) -> "ScheduledWorkout":
    """Race-safe find-or-create for ScheduledWorkout(session_id, date).

    Uses INSERT ... ON CONFLICT DO NOTHING so the conflict path stays inside
    a single statement — catching IntegrityError after a flush() leaves the
    asyncpg connection in a state that breaks the request-scoped session
    dependency (greenlet error on the trailing commit).
    """
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    stmt = (
        pg_insert(ScheduledWorkout)
        .values(
            workout_plan_id=plan_id,
            workout_session_id=session_id,
            scheduled_date=scheduled_date,
            week_number=0,
            is_completed=is_completed,
        )
        .on_conflict_do_nothing(
            index_elements=["workout_session_id", "scheduled_date"]
        )
    )
    await db.execute(stmt)

    fetched = await db.execute(
        select(ScheduledWorkout).where(
            ScheduledWorkout.workout_session_id == session_id,
            ScheduledWorkout.scheduled_date == scheduled_date,
        )
    )
    return fetched.scalar_one()


def _training_weekdays(days_per_week: int) -> list[int]:
    """Return weekday indices (Mon=0 .. Sun=6) for training days."""
    if days_per_week <= 3:
        return [0, 2, 4][:days_per_week]  # Mon, Wed, Fri
    if days_per_week == 4:
        return [0, 1, 3, 4]
    if days_per_week == 5:
        return [0, 1, 2, 3, 4]
    if days_per_week == 6:
        return [0, 1, 2, 3, 4, 5]
    return list(range(7))


@router.get("/calendar", response_model=list[CalendarEntry])
async def get_calendar(
    year: int = Query(..., ge=1970, le=2100),
    month: int = Query(..., ge=1, le=12),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Get scheduled workout entries for a given month."""
    from datetime import date
    import calendar as cal_mod

    first_day = date(year, month, 1)
    last_day = date(year, month, cal_mod.monthrange(year, month)[1])

    result = await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            WorkoutPlan.is_active == True,  # noqa: E712
            ScheduledWorkout.scheduled_date >= first_day,
            ScheduledWorkout.scheduled_date <= last_day,
        )
        .order_by(ScheduledWorkout.scheduled_date)
    )
    rows = result.scalars().all()

    entries = []
    for sw in rows:
        session = sw.workout_session

        entries.append(CalendarEntry(
            id=str(sw.id),
            session_id=str(session.id),
            session_name=session.name,
            day_number=session.day_number,
            week_number=sw.week_number,
            scheduled_date=sw.scheduled_date,
            plan_id=str(sw.workout_plan_id),
            plan_title=sw.workout_plan.title,
            is_completed=sw.is_completed,
        ))

    return entries


@router.patch("/schedule/{entry_id}/reschedule")
async def reschedule_entry(
    entry_id: UUID,
    data: RescheduleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Reschedule a single scheduled workout entry to a new date."""
    from app.core.exceptions import ConflictError

    result = await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            ScheduledWorkout.id == entry_id,
            WorkoutPlan.user_id == user.id,
        )
    )
    sw = result.scalar_one_or_none()
    if not sw:
        raise NotFoundError("Scheduled workout")

    # Reject moves that would collide with another entry of the same session
    # on that date — auto_schedule and start_workout treat (session, date) as
    # the dedup key, so we have to enforce the same invariant here.
    if sw.scheduled_date != data.scheduled_date:
        clash = await db.execute(
            select(ScheduledWorkout.id).where(
                ScheduledWorkout.workout_session_id == sw.workout_session_id,
                ScheduledWorkout.scheduled_date == data.scheduled_date,
                ScheduledWorkout.id != sw.id,
            )
        )
        if clash.scalar_one_or_none() is not None:
            raise ConflictError("Another entry already exists on that date")

    sw.scheduled_date = data.scheduled_date
    return {"detail": "Rescheduled", "scheduled_date": str(data.scheduled_date)}


@router.patch("/schedule/{entry_id}/complete")
async def toggle_complete_entry(
    entry_id: UUID,
    data: CompleteEntryRequest | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Set or toggle is_completed for a scheduled workout entry.

    Body {"is_completed": bool} sets explicitly. Empty body toggles
    (legacy behavior).
    """
    result = await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            ScheduledWorkout.id == entry_id,
            WorkoutPlan.user_id == user.id,
        )
    )
    sw = result.scalar_one_or_none()
    if not sw:
        raise NotFoundError("Scheduled workout")

    if data is not None and data.is_completed is not None:
        sw.is_completed = data.is_completed
    else:
        sw.is_completed = not sw.is_completed
    return {"detail": "Updated", "is_completed": sw.is_completed}


@router.post("/schedule")
async def add_schedule_entry(
    data: AddScheduleEntryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Add an ad-hoc workout to the calendar (e.g. unscheduled workout done today).

    If an entry already exists for this session on this date, return it
    instead of creating a duplicate — this is also the contract callers can
    rely on for idempotent retries.
    """
    # Verify session belongs to user's active plan and fetch plan title
    result = await db.execute(
        select(WorkoutSession, WorkoutPlan.title)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutSession.id == data.session_id,
            WorkoutPlan.user_id == user.id,
        )
    )
    row = result.one_or_none()
    if not row:
        raise NotFoundError("Workout session")
    session, plan_title = row

    sw = await _find_or_create_scheduled_workout(
        db,
        plan_id=session.workout_plan_id,
        session_id=session.id,
        scheduled_date=data.scheduled_date,
        is_completed=data.is_completed,
    )

    return CalendarEntry(
        id=str(sw.id),
        session_id=str(session.id),
        session_name=session.name,
        day_number=session.day_number,
        week_number=sw.week_number,
        scheduled_date=sw.scheduled_date,
        plan_id=str(session.workout_plan_id),
        plan_title=plan_title,
        is_completed=sw.is_completed,
    )


@router.delete("/schedule/{entry_id}")
async def delete_schedule_entry(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Remove a scheduled workout entry from the calendar."""
    result = await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            ScheduledWorkout.id == entry_id,
            WorkoutPlan.user_id == user.id,
        )
    )
    sw = result.scalar_one_or_none()
    if not sw:
        raise NotFoundError("Scheduled workout")

    await db.delete(sw)
    return {"detail": "Deleted"}


@router.post("/plans/{plan_id}/schedule")
async def auto_schedule_plan(
    plan_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Auto-schedule all sessions of a plan across its full duration.

    Creates one ScheduledWorkout row per session per week.
    E.g. 8 weeks × 2 days/week = 16 rows.
    Respects days_per_week from the plan.

    Preserves any already-completed entries and any entries with logged sets
    so users don't lose history when they regenerate the schedule. Concurrent
    callers serialize on a per-plan advisory lock so a double-click can't
    leave duplicate rows behind.
    """
    from datetime import date, timedelta
    from sqlalchemy import delete, text

    from app.core.locks import advisory_key

    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Workout plan")

    lock_key = advisory_key("auto_schedule", str(plan.id))
    await db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": lock_key})

    has_set = (
        select(ExerciseSet.id)
        .where(ExerciseSet.scheduled_workout_id == ScheduledWorkout.id)
        .exists()
    )
    await db.execute(
        delete(ScheduledWorkout).where(
            ScheduledWorkout.workout_plan_id == plan.id,
            ScheduledWorkout.is_completed == False,  # noqa: E712
            ~has_set,
        )
    )
    await db.flush()

    sessions = plan.sessions
    if not sessions:
        return {"detail": "No sessions to schedule"}

    today = date.today()
    weekdays = _training_weekdays(plan.days_per_week)
    num_sessions = len(sessions)
    total_entries = 0

    existing_keys_result = await db.execute(
        select(
            ScheduledWorkout.workout_session_id,
            ScheduledWorkout.scheduled_date,
        ).where(ScheduledWorkout.workout_plan_id == plan.id)
    )
    existing_keys = {(sid, sd) for sid, sd in existing_keys_result.all()}

    # Anchor week 0 to "today onwards" so weekdays earlier than today don't
    # silently disappear from the first week. Otherwise a Wednesday-Friday
    # plan kicked off on Thursday loses its Wednesday session forever.
    week_one_monday = today - timedelta(days=today.weekday())
    for week in range(plan.duration_weeks):
        week_monday = week_one_monday + timedelta(weeks=week)

        for day_idx, weekday in enumerate(weekdays):
            session = sessions[day_idx % num_sessions]
            training_date = week_monday + timedelta(days=weekday)

            if training_date < today:
                # Past day in week 0 — push to the equivalent weekday after
                # the plan's normal end so the user still gets `duration_weeks`
                # worth of sessions.
                training_date = (
                    week_one_monday
                    + timedelta(weeks=plan.duration_weeks)
                    + timedelta(days=weekday)
                )

            if (session.id, training_date) in existing_keys:
                continue

            sw = ScheduledWorkout(
                workout_plan_id=plan.id,
                workout_session_id=session.id,
                scheduled_date=training_date,
                week_number=week + 1,
            )
            db.add(sw)
            existing_keys.add((session.id, training_date))
            total_entries += 1

    return {"detail": f"Scheduled {total_entries} workouts across {plan.duration_weeks} weeks"}
