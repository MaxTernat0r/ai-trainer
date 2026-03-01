from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.exercise import Equipment, Exercise, ExerciseMuscleGroup, MuscleGroup
from app.models.user import User
from app.schemas.exercise import (
    EquipmentRead,
    ExerciseListRead,
    ExerciseMuscleGroupRead,
    ExerciseRead,
    MuscleGroupRead,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseListRead])
async def list_exercises(
    muscle_group_id: str | None = Query(None),
    equipment_id: str | None = Query(None),
    difficulty: str | None = Query(None),
    exercise_type: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    query = select(Exercise)

    if muscle_group_id:
        query = query.join(ExerciseMuscleGroup).where(
            ExerciseMuscleGroup.muscle_group_id == muscle_group_id
        )
    if equipment_id:
        query = query.where(Exercise.equipment_id == equipment_id)
    if difficulty:
        query = query.where(Exercise.difficulty == difficulty)
    if exercise_type:
        query = query.where(Exercise.exercise_type == exercise_type)
    if search:
        query = query.where(
            Exercise.name_ru.ilike(f"%{search}%") | Exercise.name.ilike(f"%{search}%")
        )

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    exercises = result.scalars().all()

    return [
        ExerciseListRead(
            id=str(e.id),
            name=e.name,
            name_ru=e.name_ru,
            difficulty=e.difficulty,
            exercise_type=e.exercise_type,
            equipment=EquipmentRead(
                id=str(e.equipment.id),
                name=e.equipment.name,
                name_ru=e.equipment.name_ru,
                category=e.equipment.category,
            ) if e.equipment else None,
            model_3d_key=e.model_3d_key,
        )
        for e in exercises
    ]


@router.get("/muscle-groups", response_model=list[MuscleGroupRead])
async def list_muscle_groups(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(select(MuscleGroup))
    return [
        MuscleGroupRead(id=str(mg.id), name=mg.name, name_ru=mg.name_ru, body_area=mg.body_area)
        for mg in result.scalars()
    ]


@router.get("/equipment", response_model=list[EquipmentRead])
async def list_equipment(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(select(Equipment))
    return [
        EquipmentRead(id=str(eq.id), name=eq.name, name_ru=eq.name_ru, category=eq.category)
        for eq in result.scalars()
    ]


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
    exercise_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise NotFoundError("Exercise")

    return ExerciseRead(
        id=str(exercise.id),
        name=exercise.name,
        name_ru=exercise.name_ru,
        description=exercise.description,
        description_ru=exercise.description_ru,
        instructions=exercise.instructions,
        instructions_ru=exercise.instructions_ru,
        difficulty=exercise.difficulty,
        exercise_type=exercise.exercise_type,
        equipment=EquipmentRead(
            id=str(exercise.equipment.id),
            name=exercise.equipment.name,
            name_ru=exercise.equipment.name_ru,
            category=exercise.equipment.category,
        ) if exercise.equipment else None,
        model_3d_key=exercise.model_3d_key,
        muscle_groups=[
            ExerciseMuscleGroupRead(
                muscle_group=MuscleGroupRead(
                    id=str(emg.muscle_group.id),
                    name=emg.muscle_group.name,
                    name_ru=emg.muscle_group.name_ru,
                    body_area=emg.muscle_group.body_area,
                ),
                is_primary=emg.is_primary,
            )
            for emg in exercise.muscle_groups
        ],
    )
