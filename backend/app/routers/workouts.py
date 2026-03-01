import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workout import ExerciseSet, WorkoutExercise, WorkoutPlan
from app.schemas.workout import (
    ExerciseSetLog,
    ExerciseSetRead,
    GenerateWorkoutRequest,
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
    # AI generation will be implemented in Phase 7
    # For now, return a placeholder
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
    plan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Workout plan")

    sessions = []
    for s in plan.sessions:
        exercises = []
        for we in s.exercises:
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
                        for es in we.logged_sets
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
    plan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    # Deactivate all other plans
    await db.execute(
        update(WorkoutPlan)
        .where(WorkoutPlan.user_id == user.id)
        .values(is_active=False)
    )

    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Workout plan")

    plan.is_active = True
    return {"detail": "Plan activated"}


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
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
    workout_exercise_id: str,
    data: ExerciseSetLog,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WorkoutExercise).where(WorkoutExercise.id == workout_exercise_id)
    )
    we = result.scalar_one_or_none()
    if not we:
        raise NotFoundError("Workout exercise")

    exercise_set = ExerciseSet(
        workout_exercise_id=uuid.UUID(workout_exercise_id),
        set_number=data.set_number,
        reps_completed=data.reps_completed,
        weight_kg=data.weight_kg,
        duration_seconds=data.duration_seconds,
        is_warmup=data.is_warmup,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(exercise_set)
    await db.flush()

    return ExerciseSetRead(
        id=str(exercise_set.id),
        set_number=exercise_set.set_number,
        reps_completed=exercise_set.reps_completed,
        weight_kg=exercise_set.weight_kg,
        duration_seconds=exercise_set.duration_seconds,
        is_warmup=exercise_set.is_warmup,
        completed_at=exercise_set.completed_at,
    )
