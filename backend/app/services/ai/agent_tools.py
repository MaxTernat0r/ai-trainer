"""Registry, Anthropic-format definitions and executors for all agent tools.

Conventions:
- Every tool function is async and accepts (input: dict, user: User, db:
  AsyncSession). It returns a JSON-serialisable Python object (dict or list).
- user_id is taken from the authenticated User, never from input.
- Validation errors raise ToolValidationError; ownership mismatches likewise.
- Read tools never mutate state. Write tools commit (or flush; the engine
  commits at the end) only after all checks pass.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import MeasurementLog, WeightLog
from app.models.exercise import Equipment, Exercise, MuscleGroup
from app.models.nutrition import (
    FoodItem,
    Meal,
    MealItem,
    NutritionLog,
    NutritionPlan,
)
from app.models.profile import (
    MedicalRestriction,
    UserMedicalRestriction,
    UserProfile,
)
from app.models.user import User
from app.models.workout import (
    ExerciseSet,
    ScheduledWorkout,
    WorkoutExercise,
    WorkoutPlan,
    WorkoutSession,
)
from app.schemas.nutrition import GenerateNutritionRequest
from app.schemas.workout import GenerateWorkoutRequest
from app.services.ai.agent_errors import ToolNotFoundError, ToolValidationError

logger = logging.getLogger(__name__)


# ---- Bounds ---------------------------------------------------------------

WEIGHT_BOUNDS = (30.0, 300.0)
HEIGHT_BOUNDS = (100.0, 250.0)
AGE_BOUNDS = (10, 100)
TARGET_WEIGHT_BOUNDS = (30.0, 300.0)
TRAINING_DAYS_BOUNDS = (1, 7)
MEALS_PER_DAY_BOUNDS = (2, 7)
MEASUREMENT_BOUNDS = (10.0, 250.0)


# ---- Helpers --------------------------------------------------------------


def _check_bounds(name: str, value: float | int | None, bounds: tuple[float, float], unit: str) -> None:
    if value is None:
        return
    lo, hi = bounds
    if value < lo or value > hi:
        raise ToolValidationError(
            f"{name} = {value} {unit} вне допустимого диапазона ({lo}–{hi} {unit}). "
            "Это похоже на ошибку ввода — уточни у пользователя."
        )


def _parse_uuid(value: str, field: str = "id") -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError) as exc:
        raise ToolValidationError(f"Поле {field} не является валидным UUID: {value!r}") from exc


def _parse_date(value: str | None, field: str = "logged_at") -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ToolValidationError(
            f"Поле {field}={value!r} должно быть в формате YYYY-MM-DD"
        ) from exc


async def _get_profile(user: User, db: AsyncSession) -> UserProfile | None:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def _require_profile(user: User, db: AsyncSession) -> UserProfile:
    profile = await _get_profile(user, db)
    if not profile:
        raise ToolValidationError(
            "Профиль не заполнен. Попроси пользователя заполнить онбординг "
            "перед тем, как выполнять это действие."
        )
    return profile


# ---- READ-ONLY TOOLS ------------------------------------------------------


async def get_profile(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    profile = await _get_profile(user, db)
    if not profile:
        return {"profile_filled": False, "message": "Профиль не заполнен"}

    age: int | None = None
    if profile.date_of_birth:
        today = date.today()
        age = today.year - profile.date_of_birth.year - (
            (today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day)
        )

    restrictions = []
    for umr in profile.medical_restrictions:
        r = umr.restriction
        restrictions.append({
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "notes": umr.notes,
        })

    return {
        "profile_filled": True,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
        "age": age,
        "gender": profile.gender,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "experience_level": profile.experience_level,
        "goal": profile.goal,
        "sport_type": profile.sport_type,
        "activity_level": profile.activity_level,
        "target_weight_kg": profile.target_weight_kg,
        "equipment_available": profile.equipment_available,
        "training_days_per_week": profile.training_days_per_week,
        "meals_per_day": profile.meals_per_day,
        "food_allergies": profile.food_allergies,
        "disliked_foods": profile.disliked_foods,
        "custom_health_notes": profile.custom_health_notes,
        "medical_restrictions": restrictions,
    }


async def list_medical_restrictions_catalog(
    input: dict[str, Any], user: User, db: AsyncSession
) -> list[dict[str, Any]]:
    result = await db.execute(select(MedicalRestriction).order_by(MedicalRestriction.name))
    return [
        {"id": str(r.id), "name": r.name, "description": r.description}
        for r in result.scalars()
    ]


async def get_active_plans(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    workout = (await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.user_id == user.id, WorkoutPlan.is_active.is_(True)
        )
    )).scalar_one_or_none()
    nutrition = (await db.execute(
        select(NutritionPlan).where(
            NutritionPlan.user_id == user.id, NutritionPlan.is_active.is_(True)
        )
    )).scalar_one_or_none()
    return {
        "active_workout_plan": {
            "id": str(workout.id),
            "title": workout.title,
            "goal": workout.goal,
            "difficulty": workout.difficulty,
            "duration_weeks": workout.duration_weeks,
            "days_per_week": workout.days_per_week,
        } if workout else None,
        "active_nutrition_plan": {
            "id": str(nutrition.id),
            "title": nutrition.title,
            "daily_calories": nutrition.daily_calories,
            "daily_protein_g": nutrition.daily_protein_g,
            "daily_fat_g": nutrition.daily_fat_g,
            "daily_carbs_g": nutrition.daily_carbs_g,
        } if nutrition else None,
    }


async def list_workout_plans(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    result = await db.execute(
        select(WorkoutPlan)
        .where(WorkoutPlan.user_id == user.id)
        .order_by(WorkoutPlan.created_at.desc())
    )
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "goal": p.goal,
            "difficulty": p.difficulty,
            "duration_weeks": p.duration_weeks,
            "days_per_week": p.days_per_week,
            "is_active": p.is_active,
            "is_ai_generated": p.is_ai_generated,
            "created_at": p.created_at.isoformat(),
        }
        for p in result.scalars()
    ]


async def list_nutrition_plans(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    result = await db.execute(
        select(NutritionPlan)
        .where(NutritionPlan.user_id == user.id)
        .order_by(NutritionPlan.created_at.desc())
    )
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "daily_calories": p.daily_calories,
            "daily_protein_g": p.daily_protein_g,
            "daily_fat_g": p.daily_fat_g,
            "daily_carbs_g": p.daily_carbs_g,
            "is_active": p.is_active,
            "is_ai_generated": p.is_ai_generated,
            "created_at": p.created_at.isoformat(),
        }
        for p in result.scalars()
    ]


async def get_workout_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    result = await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План тренировок не найден или принадлежит другому пользователю")
    return {
        "id": str(plan.id),
        "title": plan.title,
        "description": plan.description,
        "goal": plan.goal,
        "difficulty": plan.difficulty,
        "duration_weeks": plan.duration_weeks,
        "days_per_week": plan.days_per_week,
        "is_active": plan.is_active,
        "sessions": [
            {
                "id": str(s.id),
                "day_number": s.day_number,
                "name": s.name,
                "notes": s.notes,
                "exercises": [
                    {
                        "id": str(we.id),
                        "name_ru": we.exercise.name_ru if we.exercise else None,
                        "target_sets": we.target_sets,
                        "target_reps": we.target_reps,
                        "target_rest_seconds": we.target_rest_seconds,
                        "notes": we.notes,
                    }
                    for we in s.exercises
                ],
            }
            for s in plan.sessions
        ],
    }


async def get_nutrition_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    result = await db.execute(
        select(NutritionPlan).where(
            NutritionPlan.id == plan_id, NutritionPlan.user_id == user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План питания не найден или принадлежит другому пользователю")
    return {
        "id": str(plan.id),
        "title": plan.title,
        "daily_calories": plan.daily_calories,
        "daily_protein_g": plan.daily_protein_g,
        "daily_fat_g": plan.daily_fat_g,
        "daily_carbs_g": plan.daily_carbs_g,
        "is_active": plan.is_active,
        "meals": [
            {
                "id": str(m.id),
                "name": m.name,
                "target_calories": m.target_calories,
                "items": [
                    {
                        "food_name": item.food_item.name_ru if item.food_item else None,
                        "quantity_g": item.quantity_g,
                        "notes": item.notes,
                    }
                    for item in m.items
                ],
            }
            for m in plan.meals
        ],
    }


async def list_exercises(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    """Optional filters: muscle_group (substring match on name_ru), difficulty,
    equipment (substring match on name_ru), limit (default 30, max 100)."""
    muscle_group = (input.get("muscle_group") or "").strip().lower()
    difficulty = (input.get("difficulty") or "").strip().lower()
    equipment = (input.get("equipment") or "").strip().lower()
    limit = int(input.get("limit") or 30)
    limit = max(1, min(limit, 100))

    stmt = select(Exercise)
    if difficulty:
        stmt = stmt.where(func.lower(Exercise.difficulty) == difficulty)
    stmt = stmt.order_by(Exercise.name_ru).limit(limit * 4)  # we'll filter post

    result = await db.execute(stmt)
    items: list[dict[str, Any]] = []
    for ex in result.scalars():
        eq_name = (ex.equipment.name_ru if ex.equipment else "") or ""
        mg_names = [emg.muscle_group.name_ru.lower() for emg in ex.muscle_groups if emg.muscle_group]
        if equipment and equipment not in eq_name.lower():
            continue
        if muscle_group and not any(muscle_group in n for n in mg_names):
            continue
        items.append({
            "id": str(ex.id),
            "name_ru": ex.name_ru,
            "name": ex.name,
            "difficulty": ex.difficulty,
            "type": ex.exercise_type,
            "equipment": eq_name or None,
            "muscle_groups": [emg.muscle_group.name_ru for emg in ex.muscle_groups if emg.muscle_group],
        })
        if len(items) >= limit:
            break
    return items


async def get_weight_history(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    days = int(input.get("days") or 90)
    days = max(1, min(days, 365))
    cutoff = date.today() - timedelta(days=days)
    result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id, WeightLog.logged_at >= cutoff)
        .order_by(WeightLog.logged_at)
    )
    return [
        {"id": str(w.id), "weight_kg": w.weight_kg, "logged_at": w.logged_at.isoformat()}
        for w in result.scalars()
    ]


async def get_measurements_history(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    days = int(input.get("days") or 90)
    days = max(1, min(days, 365))
    measurement_type = (input.get("measurement_type") or "").strip().lower()
    cutoff = date.today() - timedelta(days=days)

    stmt = select(MeasurementLog).where(
        MeasurementLog.user_id == user.id,
        MeasurementLog.logged_at >= cutoff,
    )
    if measurement_type:
        stmt = stmt.where(func.lower(MeasurementLog.measurement_type) == measurement_type)
    stmt = stmt.order_by(MeasurementLog.logged_at)
    result = await db.execute(stmt)
    return [
        {
            "id": str(m.id),
            "measurement_type": m.measurement_type,
            "value_cm": m.value_cm,
            "logged_at": m.logged_at.isoformat(),
        }
        for m in result.scalars()
    ]


async def get_workout_calendar(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    today = date.today()
    year = int(input.get("year") or today.year)
    month = int(input.get("month") or today.month)
    if not (1 <= month <= 12):
        raise ToolValidationError("Поле month должно быть от 1 до 12")
    if not (2020 <= year <= 2100):
        raise ToolValidationError("Поле year выглядит подозрительно")

    import calendar as cal_mod
    first = date(year, month, 1)
    last = date(year, month, cal_mod.monthrange(year, month)[1])

    result = await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            ScheduledWorkout.scheduled_date >= first,
            ScheduledWorkout.scheduled_date <= last,
        )
        .order_by(ScheduledWorkout.scheduled_date)
    )
    out: list[dict[str, Any]] = []
    for sw in result.scalars():
        out.append({
            "id": str(sw.id),
            "scheduled_date": sw.scheduled_date.isoformat(),
            "session_name": sw.workout_session.name if sw.workout_session else None,
            "plan_id": str(sw.workout_plan_id),
            "plan_title": sw.workout_plan.title if sw.workout_plan else None,
            "is_completed": sw.is_completed,
        })
    return out


async def get_today_nutrition_log(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    logged_date = _parse_date(input.get("logged_at")) or date.today()
    result = await db.execute(
        select(NutritionLog)
        .where(NutritionLog.user_id == user.id, NutritionLog.logged_at == logged_date)
        .order_by(NutritionLog.created_at)
    )
    rows = result.scalars().all()
    items = [
        {
            "id": str(r.id),
            "food_name": r.food_name,
            "meal_type": r.meal_type,
            "quantity_g": r.quantity_g,
            "calories": r.calories,
            "protein_g": r.protein_g,
            "fat_g": r.fat_g,
            "carbs_g": r.carbs_g,
        }
        for r in rows
    ]
    totals = {
        "calories": sum(r.calories for r in rows),
        "protein_g": sum(r.protein_g for r in rows),
        "fat_g": sum(r.fat_g for r in rows),
        "carbs_g": sum(r.carbs_g for r in rows),
    }
    return {"date": logged_date.isoformat(), "items": items, "totals": totals}


async def get_recent_workout_logs(input: dict[str, Any], user: User, db: AsyncSession) -> list[dict[str, Any]]:
    days = int(input.get("days") or 14)
    days = max(1, min(days, 90))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(ExerciseSet)
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            ExerciseSet.completed_at >= cutoff,
        )
        .order_by(ExerciseSet.completed_at.desc())
        .limit(200)
    )
    return [
        {
            "id": str(es.id),
            "set_number": es.set_number,
            "reps_completed": es.reps_completed,
            "weight_kg": es.weight_kg,
            "duration_seconds": es.duration_seconds,
            "is_warmup": es.is_warmup,
            "completed_at": es.completed_at.isoformat(),
            "exercise_name": es.workout_exercise.exercise.name_ru
                if es.workout_exercise and es.workout_exercise.exercise else None,
        }
        for es in result.scalars()
    ]


async def analyze_progress(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    days = int(input.get("days") or 30)
    days = max(7, min(days, 365))
    cutoff = date.today() - timedelta(days=days)
    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=days)

    # Weight trend
    weights = (await db.execute(
        select(WeightLog).where(
            WeightLog.user_id == user.id, WeightLog.logged_at >= cutoff
        ).order_by(WeightLog.logged_at)
    )).scalars().all()
    weight_summary: dict[str, Any] = {"entries": len(weights)}
    if weights:
        weight_summary["start_kg"] = weights[0].weight_kg
        weight_summary["latest_kg"] = weights[-1].weight_kg
        weight_summary["delta_kg"] = round(weights[-1].weight_kg - weights[0].weight_kg, 2)

    # Workouts completed
    completed = (await db.execute(
        select(func.count(ScheduledWorkout.id))
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            ScheduledWorkout.scheduled_date >= cutoff,
            ScheduledWorkout.is_completed.is_(True),
        )
    )).scalar() or 0

    # Sets logged
    sets_logged = (await db.execute(
        select(func.count(ExerciseSet.id))
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutPlan.user_id == user.id,
            ExerciseSet.completed_at >= cutoff_dt,
        )
    )).scalar() or 0

    # Nutrition averages
    nutrition_rows = (await db.execute(
        select(
            func.avg(NutritionLog.calories),
            func.avg(NutritionLog.protein_g),
            func.count(NutritionLog.id),
        ).where(
            NutritionLog.user_id == user.id,
            NutritionLog.logged_at >= cutoff,
        )
    )).first()
    nutrition_summary = {
        "logs_count": int(nutrition_rows[2] or 0),
        "avg_calories_per_entry": round(float(nutrition_rows[0] or 0), 1),
        "avg_protein_per_entry": round(float(nutrition_rows[1] or 0), 1),
    }

    return {
        "period_days": days,
        "weight": weight_summary,
        "workouts_completed": int(completed),
        "sets_logged": int(sets_logged),
        "nutrition": nutrition_summary,
    }


# ---- WRITE TOOLS ----------------------------------------------------------

# --- Profile ---


_ALLOWED_GENDERS = {"male", "female"}
_ALLOWED_GOALS = {"muscle_gain", "fat_loss", "endurance", "flexibility", "general_fitness"}
_ALLOWED_EXPERIENCE = {"beginner", "intermediate", "advanced"}
_ALLOWED_ACTIVITY = {"sedentary", "light", "moderate", "active", "very_active"}
_ALLOWED_SPORT = {"gym", "calisthenics", "running", "swimming", "martial_arts", "other"}
_ALLOWED_EQUIPMENT = {"full_gym", "home_basic", "bodyweight", "outdoor"}


async def update_profile(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    profile = await _get_profile(user, db)

    height = input.get("height_cm")
    weight = input.get("weight_kg")
    target_weight = input.get("target_weight_kg")
    age = input.get("age")
    training_days = input.get("training_days_per_week")
    meals_per_day = input.get("meals_per_day")
    gender = input.get("gender")
    goal = input.get("goal")
    experience = input.get("experience_level")
    activity = input.get("activity_level")
    sport = input.get("sport_type")
    equipment = input.get("equipment_available")
    first_name = input.get("first_name")
    last_name = input.get("last_name")
    food_allergies = input.get("food_allergies")
    disliked_foods = input.get("disliked_foods")
    custom_health_notes = input.get("custom_health_notes")
    date_of_birth = _parse_date(input.get("date_of_birth"), "date_of_birth")

    _check_bounds("Рост", height, HEIGHT_BOUNDS, "см")
    _check_bounds("Вес", weight, WEIGHT_BOUNDS, "кг")
    _check_bounds("Целевой вес", target_weight, TARGET_WEIGHT_BOUNDS, "кг")
    _check_bounds("Возраст", age, AGE_BOUNDS, "лет")
    _check_bounds("Тренировок в неделю", training_days, TRAINING_DAYS_BOUNDS, "")
    _check_bounds("Приёмов пищи в день", meals_per_day, MEALS_PER_DAY_BOUNDS, "")

    if gender is not None and gender not in _ALLOWED_GENDERS:
        raise ToolValidationError(f"gender должно быть одним из {sorted(_ALLOWED_GENDERS)}")
    if goal is not None and goal not in _ALLOWED_GOALS:
        raise ToolValidationError(f"goal должно быть одним из {sorted(_ALLOWED_GOALS)}")
    if experience is not None and experience not in _ALLOWED_EXPERIENCE:
        raise ToolValidationError(f"experience_level должно быть одним из {sorted(_ALLOWED_EXPERIENCE)}")
    if activity is not None and activity not in _ALLOWED_ACTIVITY:
        raise ToolValidationError(f"activity_level должно быть одним из {sorted(_ALLOWED_ACTIVITY)}")
    if sport is not None and sport not in _ALLOWED_SPORT:
        raise ToolValidationError(f"sport_type должно быть одним из {sorted(_ALLOWED_SPORT)}")
    if equipment is not None and equipment not in _ALLOWED_EQUIPMENT:
        raise ToolValidationError(
            f"equipment_available должно быть одним из {sorted(_ALLOWED_EQUIPMENT)}"
        )

    # Sanity-check на абсурдные значения в текстовых полях
    for field_name, value in [
        ("food_allergies", food_allergies),
        ("disliked_foods", disliked_foods),
    ]:
        if value and isinstance(value, str):
            lowered = value.lower()
            for absurd in ("бензин", "песок", "металл", "пластик", "цемент", "дерево", "камн", "землю"):
                if absurd in lowered:
                    raise ToolValidationError(
                        f"В поле {field_name} обнаружен нереалистичный продукт ({absurd!r}). "
                        "Уточни у пользователя, имел ли он в виду что-то конкретное, "
                        "или это была шутка. Не сохраняй абсурд в профиль."
                    )

    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    if first_name is not None:
        profile.first_name = first_name
    if last_name is not None:
        profile.last_name = last_name
    if date_of_birth is not None:
        profile.date_of_birth = date_of_birth
    if gender is not None:
        profile.gender = gender
    if height is not None:
        profile.height_cm = float(height)
    if weight is not None:
        profile.weight_kg = float(weight)
    if target_weight is not None:
        profile.target_weight_kg = float(target_weight)
    if experience is not None:
        profile.experience_level = experience
    if goal is not None:
        profile.goal = goal
    if sport is not None:
        profile.sport_type = sport
    if activity is not None:
        profile.activity_level = activity
    if equipment is not None:
        profile.equipment_available = equipment
    if training_days is not None:
        profile.training_days_per_week = int(training_days)
    if meals_per_day is not None:
        profile.meals_per_day = int(meals_per_day)
    if food_allergies is not None:
        profile.food_allergies = food_allergies
    if disliked_foods is not None:
        profile.disliked_foods = disliked_foods
    if custom_health_notes is not None:
        profile.custom_health_notes = custom_health_notes

    await db.flush()
    return {"ok": True, "message": "Профиль обновлён"}


async def add_medical_restriction(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    profile = await _require_profile(user, db)
    restriction_id = _parse_uuid(input.get("restriction_id"), "restriction_id")
    notes = input.get("notes")

    restr = (await db.execute(
        select(MedicalRestriction).where(MedicalRestriction.id == restriction_id)
    )).scalar_one_or_none()
    if not restr:
        raise ToolValidationError(
            "Такого ограничения нет в каталоге. Сначала вызови list_medical_restrictions_catalog."
        )

    existing = (await db.execute(
        select(UserMedicalRestriction).where(
            UserMedicalRestriction.user_profile_id == profile.id,
            UserMedicalRestriction.medical_restriction_id == restriction_id,
        )
    )).scalar_one_or_none()
    if existing:
        if notes is not None:
            existing.notes = notes
            await db.flush()
        return {"ok": True, "message": "Это ограничение уже есть в профиле", "restriction": restr.name}

    db.add(UserMedicalRestriction(
        user_profile_id=profile.id,
        medical_restriction_id=restriction_id,
        notes=notes,
    ))
    await db.flush()
    return {"ok": True, "message": "Ограничение добавлено", "restriction": restr.name}


async def remove_medical_restriction(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    profile = await _require_profile(user, db)
    restriction_id = _parse_uuid(input.get("restriction_id"), "restriction_id")
    result = await db.execute(
        delete(UserMedicalRestriction).where(
            UserMedicalRestriction.user_profile_id == profile.id,
            UserMedicalRestriction.medical_restriction_id == restriction_id,
        )
    )
    await db.flush()
    return {
        "ok": True,
        "removed": result.rowcount or 0,
        "message": "Ограничение удалено" if result.rowcount else "Такого ограничения не было",
    }


# --- Workouts ---


async def generate_workout_plan_tool(
    input: dict[str, Any], user: User, db: AsyncSession
) -> dict[str, Any]:
    profile = await _require_profile(user, db)
    if not profile.weight_kg or not profile.height_cm:
        raise ToolValidationError(
            "Для генерации плана тренировок нужны вес и рост в профиле."
        )
    weeks = int(input.get("weeks") or 4)
    days_per_week = int(input.get("days_per_week") or profile.training_days_per_week or 3)
    periodization = (input.get("periodization") or "linear").strip().lower()

    if not (1 <= weeks <= 52):
        raise ToolValidationError("weeks должно быть от 1 до 52")
    _check_bounds("Дней в неделю", days_per_week, TRAINING_DAYS_BOUNDS, "")
    if periodization not in {"linear", "undulating", "block"}:
        raise ToolValidationError("periodization должно быть 'linear', 'undulating' или 'block'")

    from app.services.ai.workout_generator import generate_workout_plan

    request = GenerateWorkoutRequest(
        weeks=weeks, days_per_week=days_per_week, periodization=periodization
    )
    plan = await generate_workout_plan(user, request, db)
    return {
        "ok": True,
        "plan_id": plan.id,
        "title": plan.title,
        "goal": plan.goal,
        "difficulty": plan.difficulty,
        "duration_weeks": plan.duration_weeks,
        "days_per_week": plan.days_per_week,
        "sessions_count": len(plan.sessions),
        "link": "/workouts",
    }


async def activate_workout_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    plan = (await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id
        )
    )).scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План не найден или принадлежит другому пользователю")

    await db.execute(
        update(WorkoutPlan).where(WorkoutPlan.user_id == user.id).values(is_active=False)
    )
    plan.is_active = True
    await db.flush()
    return {"ok": True, "plan_id": str(plan.id), "title": plan.title}


async def delete_workout_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    plan = (await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id
        )
    )).scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План не найден или принадлежит другому пользователю")
    title = plan.title
    await db.delete(plan)
    await db.flush()
    return {"ok": True, "message": f"План «{title}» удалён"}


async def schedule_workout_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    from datetime import timedelta

    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    plan = (await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user.id
        )
    )).scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План не найден или принадлежит другому пользователю")

    await db.execute(
        delete(ScheduledWorkout).where(ScheduledWorkout.workout_plan_id == plan.id)
    )

    sessions = plan.sessions
    if not sessions:
        return {"ok": True, "message": "В плане нет сессий — нечего распределять", "scheduled": 0}

    if plan.days_per_week <= 3:
        weekdays = [0, 2, 4][: plan.days_per_week]
    elif plan.days_per_week == 4:
        weekdays = [0, 1, 3, 4]
    elif plan.days_per_week == 5:
        weekdays = [0, 1, 2, 3, 4]
    elif plan.days_per_week == 6:
        weekdays = [0, 1, 2, 3, 4, 5]
    else:
        weekdays = list(range(7))

    today = date.today()
    num_sessions = len(sessions)
    total = 0
    for week in range(plan.duration_weeks):
        week_start = today + timedelta(weeks=week)
        week_monday = week_start - timedelta(days=week_start.weekday())
        for day_idx, weekday in enumerate(weekdays):
            session = sessions[day_idx % num_sessions]
            training_date = week_monday + timedelta(days=weekday)
            if training_date < today:
                continue
            db.add(ScheduledWorkout(
                workout_plan_id=plan.id,
                workout_session_id=session.id,
                scheduled_date=training_date,
                week_number=week + 1,
            ))
            total += 1
    await db.flush()
    return {"ok": True, "scheduled": total, "weeks": plan.duration_weeks, "link": "/workouts"}


async def reschedule_workout_entry(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    entry_id = _parse_uuid(input.get("entry_id"), "entry_id")
    new_date = _parse_date(input.get("new_date"), "new_date")
    if not new_date:
        raise ToolValidationError("Поле new_date обязательно (YYYY-MM-DD)")

    sw = (await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            ScheduledWorkout.id == entry_id,
            WorkoutPlan.user_id == user.id,
        )
    )).scalar_one_or_none()
    if not sw:
        raise ToolValidationError("Запись календаря не найдена")
    sw.scheduled_date = new_date
    await db.flush()
    return {"ok": True, "scheduled_date": new_date.isoformat()}


async def toggle_workout_complete(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    entry_id = _parse_uuid(input.get("entry_id"), "entry_id")
    sw = (await db.execute(
        select(ScheduledWorkout)
        .join(WorkoutPlan, ScheduledWorkout.workout_plan_id == WorkoutPlan.id)
        .where(
            ScheduledWorkout.id == entry_id,
            WorkoutPlan.user_id == user.id,
        )
    )).scalar_one_or_none()
    if not sw:
        raise ToolValidationError("Запись календаря не найдена")
    sw.is_completed = not sw.is_completed
    await db.flush()
    return {"ok": True, "is_completed": sw.is_completed}


async def log_exercise_set(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    we_id = _parse_uuid(input.get("workout_exercise_id"), "workout_exercise_id")
    set_number = int(input.get("set_number") or 1)
    reps = input.get("reps_completed")
    weight_kg = input.get("weight_kg")
    duration = input.get("duration_seconds")
    is_warmup = bool(input.get("is_warmup") or False)
    scheduled_id = input.get("scheduled_workout_id")
    scheduled_uuid = _parse_uuid(scheduled_id, "scheduled_workout_id") if scheduled_id else None

    if weight_kg is not None:
        _check_bounds("Вес снаряда", weight_kg, (0.0, 1000.0), "кг")
    if reps is not None and (reps < 0 or reps > 1000):
        raise ToolValidationError("reps_completed должен быть от 0 до 1000")

    we = (await db.execute(
        select(WorkoutExercise)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .join(WorkoutPlan, WorkoutSession.workout_plan_id == WorkoutPlan.id)
        .where(
            WorkoutExercise.id == we_id,
            WorkoutPlan.user_id == user.id,
        )
    )).scalar_one_or_none()
    if not we:
        raise ToolValidationError("Упражнение не найдено в твоих планах")

    db.add(ExerciseSet(
        workout_exercise_id=we.id,
        scheduled_workout_id=scheduled_uuid,
        set_number=set_number,
        reps_completed=reps,
        weight_kg=weight_kg,
        duration_seconds=duration,
        is_warmup=is_warmup,
        completed_at=datetime.now(timezone.utc),
    ))
    await db.flush()
    return {"ok": True, "message": "Подход записан"}


# --- Nutrition ---


async def generate_nutrition_plan_tool(
    input: dict[str, Any], user: User, db: AsyncSession
) -> dict[str, Any]:
    profile = await _require_profile(user, db)
    if not profile.weight_kg or not profile.height_cm:
        raise ToolValidationError("Для генерации плана питания нужны вес и рост в профиле.")
    if not profile.date_of_birth:
        raise ToolValidationError("Для генерации плана питания нужна дата рождения в профиле.")

    meals = int(input.get("meals_per_day") or profile.meals_per_day or 4)
    _check_bounds("Приёмов пищи в день", meals, MEALS_PER_DAY_BOUNDS, "")

    from app.services.ai.nutrition_generator import generate_nutrition_plan

    request = GenerateNutritionRequest(meals_per_day=meals)
    plan = await generate_nutrition_plan(user, request, db)
    return {
        "ok": True,
        "plan_id": plan.id,
        "title": plan.title,
        "daily_calories": plan.daily_calories,
        "daily_protein_g": plan.daily_protein_g,
        "daily_fat_g": plan.daily_fat_g,
        "daily_carbs_g": plan.daily_carbs_g,
        "meals_count": len(plan.meals),
        "link": "/nutrition",
    }


async def activate_nutrition_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    plan = (await db.execute(
        select(NutritionPlan).where(
            NutritionPlan.id == plan_id, NutritionPlan.user_id == user.id
        )
    )).scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План не найден или принадлежит другому пользователю")
    await db.execute(
        update(NutritionPlan).where(NutritionPlan.user_id == user.id).values(is_active=False)
    )
    plan.is_active = True
    await db.flush()
    return {"ok": True, "plan_id": str(plan.id), "title": plan.title}


async def delete_nutrition_plan(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    plan_id = _parse_uuid(input.get("plan_id"), "plan_id")
    plan = (await db.execute(
        select(NutritionPlan).where(
            NutritionPlan.id == plan_id, NutritionPlan.user_id == user.id
        )
    )).scalar_one_or_none()
    if not plan:
        raise ToolValidationError("План не найден или принадлежит другому пользователю")
    title = plan.title
    await db.delete(plan)
    await db.flush()
    return {"ok": True, "message": f"План «{title}» удалён"}


async def log_food(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    food_name = (input.get("food_name") or "").strip()
    if not food_name:
        raise ToolValidationError("food_name обязателен")
    meal_type = (input.get("meal_type") or "snack").strip().lower()
    if meal_type not in {"breakfast", "lunch", "dinner", "snack"}:
        raise ToolValidationError("meal_type должно быть breakfast/lunch/dinner/snack")

    quantity_g = float(input.get("quantity_g") or 0)
    if quantity_g <= 0 or quantity_g > 5000:
        raise ToolValidationError("quantity_g должно быть от 1 до 5000")

    calories = float(input.get("calories") or 0)
    protein_g = float(input.get("protein_g") or 0)
    fat_g = float(input.get("fat_g") or 0)
    carbs_g = float(input.get("carbs_g") or 0)
    if calories < 0 or calories > 10000:
        raise ToolValidationError("calories должно быть от 0 до 10000")

    logged_at = _parse_date(input.get("logged_at")) or date.today()
    notes = input.get("notes")

    db.add(NutritionLog(
        user_id=user.id,
        food_name=food_name,
        meal_type=meal_type,
        quantity_g=quantity_g,
        calories=calories,
        protein_g=protein_g,
        fat_g=fat_g,
        carbs_g=carbs_g,
        logged_at=logged_at,
        notes=notes,
    ))
    await db.flush()
    return {"ok": True, "message": "Еда добавлена в дневник"}


async def delete_nutrition_log(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    log_id = _parse_uuid(input.get("log_id"), "log_id")
    row = (await db.execute(
        select(NutritionLog).where(
            NutritionLog.id == log_id, NutritionLog.user_id == user.id
        )
    )).scalar_one_or_none()
    if not row:
        raise ToolValidationError("Запись не найдена")
    await db.delete(row)
    await db.flush()
    return {"ok": True, "message": "Запись удалена"}


# --- Progress ---


async def log_weight(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    weight_kg = input.get("weight_kg")
    if weight_kg is None:
        raise ToolValidationError("weight_kg обязателен")
    weight_kg = float(weight_kg)
    _check_bounds("Вес", weight_kg, WEIGHT_BOUNDS, "кг")
    logged_at = _parse_date(input.get("logged_at")) or date.today()

    db.add(WeightLog(user_id=user.id, weight_kg=weight_kg, logged_at=logged_at))
    await db.flush()
    return {"ok": True, "weight_kg": weight_kg, "logged_at": logged_at.isoformat()}


async def delete_weight_log(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    log_id = _parse_uuid(input.get("log_id"), "log_id")
    row = (await db.execute(
        select(WeightLog).where(
            WeightLog.id == log_id, WeightLog.user_id == user.id
        )
    )).scalar_one_or_none()
    if not row:
        raise ToolValidationError("Запись не найдена")
    await db.delete(row)
    await db.flush()
    return {"ok": True, "message": "Запись веса удалена"}


_ALLOWED_MEASUREMENT_TYPES = {
    "chest", "waist", "hips", "thigh", "biceps", "neck", "forearm", "calf", "shoulders",
}


async def log_measurement(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    measurement_type = (input.get("measurement_type") or "").strip().lower()
    if measurement_type not in _ALLOWED_MEASUREMENT_TYPES:
        raise ToolValidationError(
            f"measurement_type должно быть одним из {sorted(_ALLOWED_MEASUREMENT_TYPES)}"
        )
    value_cm = input.get("value_cm")
    if value_cm is None:
        raise ToolValidationError("value_cm обязателен")
    value_cm = float(value_cm)
    _check_bounds("Замер", value_cm, MEASUREMENT_BOUNDS, "см")
    logged_at = _parse_date(input.get("logged_at")) or date.today()

    db.add(MeasurementLog(
        user_id=user.id,
        measurement_type=measurement_type,
        value_cm=value_cm,
        logged_at=logged_at,
    ))
    await db.flush()
    return {"ok": True, "measurement_type": measurement_type, "value_cm": value_cm}


async def delete_measurement(input: dict[str, Any], user: User, db: AsyncSession) -> dict[str, Any]:
    log_id = _parse_uuid(input.get("log_id"), "log_id")
    row = (await db.execute(
        select(MeasurementLog).where(
            MeasurementLog.id == log_id, MeasurementLog.user_id == user.id
        )
    )).scalar_one_or_none()
    if not row:
        raise ToolValidationError("Замер не найден")
    await db.delete(row)
    await db.flush()
    return {"ok": True, "message": "Замер удалён"}


# ---- Registry & Anthropic tool definitions --------------------------------

READ_TOOLS: dict[str, Any] = {
    "get_profile": get_profile,
    "list_medical_restrictions_catalog": list_medical_restrictions_catalog,
    "get_active_plans": get_active_plans,
    "list_workout_plans": list_workout_plans,
    "list_nutrition_plans": list_nutrition_plans,
    "get_workout_plan": get_workout_plan,
    "get_nutrition_plan": get_nutrition_plan,
    "list_exercises": list_exercises,
    "get_weight_history": get_weight_history,
    "get_measurements_history": get_measurements_history,
    "get_workout_calendar": get_workout_calendar,
    "get_today_nutrition_log": get_today_nutrition_log,
    "get_recent_workout_logs": get_recent_workout_logs,
    "analyze_progress": analyze_progress,
}

WRITE_TOOLS: dict[str, Any] = {
    "update_profile": update_profile,
    "add_medical_restriction": add_medical_restriction,
    "remove_medical_restriction": remove_medical_restriction,
    "generate_workout_plan": generate_workout_plan_tool,
    "activate_workout_plan": activate_workout_plan,
    "delete_workout_plan": delete_workout_plan,
    "schedule_workout_plan": schedule_workout_plan,
    "reschedule_workout_entry": reschedule_workout_entry,
    "toggle_workout_complete": toggle_workout_complete,
    "log_exercise_set": log_exercise_set,
    "generate_nutrition_plan": generate_nutrition_plan_tool,
    "activate_nutrition_plan": activate_nutrition_plan,
    "delete_nutrition_plan": delete_nutrition_plan,
    "log_food": log_food,
    "delete_nutrition_log": delete_nutrition_log,
    "log_weight": log_weight,
    "delete_weight_log": delete_weight_log,
    "log_measurement": log_measurement,
    "delete_measurement": delete_measurement,
}


async def execute_read_tool(name: str, input: dict[str, Any], user: User, db: AsyncSession) -> Any:
    fn = READ_TOOLS.get(name)
    if not fn:
        raise ToolNotFoundError(name)
    return await fn(input or {}, user, db)


async def execute_write_tool(name: str, input: dict[str, Any], user: User, db: AsyncSession) -> Any:
    fn = WRITE_TOOLS.get(name)
    if not fn:
        raise ToolNotFoundError(name)
    return await fn(input or {}, user, db)


# Anthropic tool definitions (input_schema = JSON Schema subset).

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    # Read
    {
        "name": "get_profile",
        "description": "Получить полный профиль пользователя: пол, возраст, рост, вес, цели, ограничения. Вызывай перед любой персонализированной рекомендацией.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_medical_restrictions_catalog",
        "description": "Получить справочник доступных медицинских ограничений (диабет, гипертония и т.д.). Используй когда нужно добавить ограничение пользователю — сначала найди id из этого списка.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_active_plans",
        "description": "Получить активные план тренировок и план питания пользователя.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_workout_plans",
        "description": "Список всех планов тренировок пользователя (включая неактивные).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_nutrition_plans",
        "description": "Список всех планов питания пользователя (включая неактивные).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_workout_plan",
        "description": "Получить детали плана тренировок: сессии, упражнения, повторы, отдых.",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string", "description": "UUID плана"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "get_nutrition_plan",
        "description": "Получить детали плана питания: блюда, продукты, граммы, калории.",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string", "description": "UUID плана"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "list_exercises",
        "description": "Поиск упражнений в каталоге с фильтрами. Используй когда юзер спрашивает про конкретное упражнение или просит подобрать.",
        "input_schema": {
            "type": "object",
            "properties": {
                "muscle_group": {"type": "string", "description": "Часть имени мышечной группы на русском (например 'груд', 'спин', 'ноги')"},
                "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                "equipment": {"type": "string", "description": "Часть имени оборудования (например 'штанг', 'гантел', 'трен')"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
        },
    },
    {
        "name": "get_weight_history",
        "description": "История замеров веса за последние N дней (по умолчанию 90).",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "minimum": 1, "maximum": 365}},
        },
    },
    {
        "name": "get_measurements_history",
        "description": "История замеров обхватов (грудь, талия, бёдра, плечо и т.п.).",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "minimum": 1, "maximum": 365},
                "measurement_type": {"type": "string", "description": "Опциональный фильтр по типу замера"},
            },
        },
    },
    {
        "name": "get_workout_calendar",
        "description": "Запланированные тренировки на конкретный месяц.",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer"},
                "month": {"type": "integer", "minimum": 1, "maximum": 12},
            },
        },
    },
    {
        "name": "get_today_nutrition_log",
        "description": "Что юзер съел сегодня (или в указанный день).",
        "input_schema": {
            "type": "object",
            "properties": {"logged_at": {"type": "string", "description": "YYYY-MM-DD, по умолчанию сегодня"}},
        },
    },
    {
        "name": "get_recent_workout_logs",
        "description": "Последние логи подходов за N дней (рабочие веса, повторы).",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "minimum": 1, "maximum": 90}},
        },
    },
    {
        "name": "analyze_progress",
        "description": "Сводная статистика прогресса за период: динамика веса, выполненные тренировки, средние калории.",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "minimum": 7, "maximum": 365}},
        },
    },
    # Write
    {
        "name": "update_profile",
        "description": (
            "Обновить поля профиля. ВАЖНО: НЕ вызывай если данные нереалистичны "
            "(вес < 30 или > 300 кг, рост < 100 или > 250 см). В таких случаях "
            "ответь словами и попроси уточнить. НЕ принимай мусор в food_allergies/disliked_foods (бензин, песок и т.п.)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "date_of_birth": {"type": "string", "description": "YYYY-MM-DD"},
                "gender": {"type": "string", "enum": ["male", "female"]},
                "height_cm": {"type": "number", "minimum": 100, "maximum": 250},
                "weight_kg": {"type": "number", "minimum": 30, "maximum": 300},
                "target_weight_kg": {"type": "number", "minimum": 30, "maximum": 300},
                "experience_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
                "goal": {"type": "string", "enum": ["muscle_gain", "fat_loss", "endurance", "flexibility", "general_fitness"]},
                "sport_type": {"type": "string", "enum": ["gym", "calisthenics", "running", "swimming", "martial_arts", "other"]},
                "activity_level": {"type": "string", "enum": ["sedentary", "light", "moderate", "active", "very_active"]},
                "equipment_available": {"type": "string", "enum": ["full_gym", "home_basic", "bodyweight", "outdoor"]},
                "training_days_per_week": {"type": "integer", "minimum": 1, "maximum": 7},
                "meals_per_day": {"type": "integer", "minimum": 2, "maximum": 7},
                "food_allergies": {"type": "string"},
                "disliked_foods": {"type": "string"},
                "custom_health_notes": {"type": "string"},
            },
        },
    },
    {
        "name": "add_medical_restriction",
        "description": "Добавить медицинское ограничение из каталога. Сначала вызови list_medical_restrictions_catalog чтобы получить id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "restriction_id": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["restriction_id"],
        },
    },
    {
        "name": "remove_medical_restriction",
        "description": "Убрать ограничение из профиля.",
        "input_schema": {
            "type": "object",
            "properties": {"restriction_id": {"type": "string"}},
            "required": ["restriction_id"],
        },
    },
    {
        "name": "generate_workout_plan",
        "description": (
            "Сгенерировать новый план тренировок (генератор сам учтёт профиль, "
            "ограничения и оборудование). Это занимает ~10-20 сек. ОБЯЗАТЕЛЬНО "
            "перед вызовом убедись что профиль заполнен (через get_profile)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "weeks": {"type": "integer", "minimum": 1, "maximum": 52, "description": "Длительность программы"},
                "days_per_week": {"type": "integer", "minimum": 1, "maximum": 7},
                "periodization": {"type": "string", "enum": ["linear", "undulating", "block"]},
            },
        },
    },
    {
        "name": "activate_workout_plan",
        "description": "Сделать план тренировок активным (деактивирует другие).",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "delete_workout_plan",
        "description": "Удалить план тренировок навсегда вместе со всеми сессиями и логами.",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "schedule_workout_plan",
        "description": "Авто-распределить план по календарю на всю длительность (1 ScheduledWorkout на день).",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "reschedule_workout_entry",
        "description": "Перенести запланированную тренировку на другую дату.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entry_id": {"type": "string", "description": "UUID ScheduledWorkout"},
                "new_date": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["entry_id", "new_date"],
        },
    },
    {
        "name": "toggle_workout_complete",
        "description": "Переключить флаг 'тренировка выполнена' для запланированной тренировки.",
        "input_schema": {
            "type": "object",
            "properties": {"entry_id": {"type": "string"}},
            "required": ["entry_id"],
        },
    },
    {
        "name": "log_exercise_set",
        "description": "Записать выполненный подход (рабочий вес, повторы или длительность).",
        "input_schema": {
            "type": "object",
            "properties": {
                "workout_exercise_id": {"type": "string"},
                "set_number": {"type": "integer", "minimum": 1, "maximum": 100},
                "reps_completed": {"type": "integer", "minimum": 0, "maximum": 1000},
                "weight_kg": {"type": "number", "minimum": 0, "maximum": 1000},
                "duration_seconds": {"type": "integer", "minimum": 0, "maximum": 36000},
                "is_warmup": {"type": "boolean"},
                "scheduled_workout_id": {"type": "string"},
            },
            "required": ["workout_exercise_id", "set_number"],
        },
    },
    {
        "name": "generate_nutrition_plan",
        "description": (
            "Сгенерировать план питания (учитывает профиль, цель, аллергии). "
            "Занимает ~5-15 сек. Перед вызовом проверь что профиль заполнен."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "meals_per_day": {"type": "integer", "minimum": 2, "maximum": 7},
            },
        },
    },
    {
        "name": "activate_nutrition_plan",
        "description": "Сделать план питания активным.",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "delete_nutrition_plan",
        "description": "Удалить план питания навсегда.",
        "input_schema": {
            "type": "object",
            "properties": {"plan_id": {"type": "string"}},
            "required": ["plan_id"],
        },
    },
    {
        "name": "log_food",
        "description": "Добавить запись о приёме пищи в дневник.",
        "input_schema": {
            "type": "object",
            "properties": {
                "food_name": {"type": "string"},
                "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"]},
                "quantity_g": {"type": "number", "minimum": 1, "maximum": 5000},
                "calories": {"type": "number", "minimum": 0, "maximum": 10000},
                "protein_g": {"type": "number", "minimum": 0, "maximum": 1000},
                "fat_g": {"type": "number", "minimum": 0, "maximum": 1000},
                "carbs_g": {"type": "number", "minimum": 0, "maximum": 2000},
                "logged_at": {"type": "string", "description": "YYYY-MM-DD, по умолчанию сегодня"},
                "notes": {"type": "string"},
            },
            "required": ["food_name", "meal_type", "quantity_g"],
        },
    },
    {
        "name": "delete_nutrition_log",
        "description": "Удалить запись из дневника питания.",
        "input_schema": {
            "type": "object",
            "properties": {"log_id": {"type": "string"}},
            "required": ["log_id"],
        },
    },
    {
        "name": "log_weight",
        "description": "Записать вес пользователя на дату.",
        "input_schema": {
            "type": "object",
            "properties": {
                "weight_kg": {"type": "number", "minimum": 30, "maximum": 300},
                "logged_at": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["weight_kg"],
        },
    },
    {
        "name": "delete_weight_log",
        "description": "Удалить запись веса.",
        "input_schema": {
            "type": "object",
            "properties": {"log_id": {"type": "string"}},
            "required": ["log_id"],
        },
    },
    {
        "name": "log_measurement",
        "description": "Записать обхват (грудь/талия/бёдра/плечо/...).",
        "input_schema": {
            "type": "object",
            "properties": {
                "measurement_type": {"type": "string", "enum": sorted(_ALLOWED_MEASUREMENT_TYPES)},
                "value_cm": {"type": "number", "minimum": 10, "maximum": 250},
                "logged_at": {"type": "string", "description": "YYYY-MM-DD"},
            },
            "required": ["measurement_type", "value_cm"],
        },
    },
    {
        "name": "delete_measurement",
        "description": "Удалить запись обхвата.",
        "input_schema": {
            "type": "object",
            "properties": {"log_id": {"type": "string"}},
            "required": ["log_id"],
        },
    },
]


# ---- Human-readable summaries for UI cards --------------------------------


_PROPOSAL_LABELS: dict[str, str] = {
    "get_profile": "Читаю профиль",
    "list_medical_restrictions_catalog": "Открываю каталог мед. ограничений",
    "get_active_plans": "Смотрю активные планы",
    "list_workout_plans": "Список планов тренировок",
    "list_nutrition_plans": "Список планов питания",
    "get_workout_plan": "Открываю план тренировок",
    "get_nutrition_plan": "Открываю план питания",
    "list_exercises": "Подбираю упражнения",
    "get_weight_history": "Смотрю историю веса",
    "get_measurements_history": "Смотрю историю замеров",
    "get_workout_calendar": "Открываю календарь тренировок",
    "get_today_nutrition_log": "Проверяю дневник питания",
    "get_recent_workout_logs": "Смотрю последние подходы",
    "analyze_progress": "Анализирую прогресс",
}


def summarize_proposal(tool_name: str, arguments: dict[str, Any]) -> str:
    """One-line human-readable summary used both for tool_use_start cards
    and for the proposal card before approval."""
    if tool_name in _PROPOSAL_LABELS:
        return _PROPOSAL_LABELS[tool_name]

    args = arguments or {}

    if tool_name == "update_profile":
        bits: list[str] = []
        for key, label in [
            ("weight_kg", "вес"), ("height_cm", "рост"), ("target_weight_kg", "цель веса"),
            ("goal", "цель"), ("activity_level", "активность"),
            ("training_days_per_week", "тренировок/нед"),
            ("meals_per_day", "приёмов/день"),
            ("food_allergies", "аллергии"),
            ("disliked_foods", "нелюбимые"),
            ("equipment_available", "оборудование"),
        ]:
            if args.get(key) is not None:
                bits.append(f"{label}={args[key]}")
        return "Обновить профиль: " + (", ".join(bits) if bits else "поля")
    if tool_name == "add_medical_restriction":
        return "Добавить медицинское ограничение"
    if tool_name == "remove_medical_restriction":
        return "Убрать медицинское ограничение"
    if tool_name == "generate_workout_plan":
        weeks = args.get("weeks", 4)
        dpw = args.get("days_per_week", 3)
        return f"Сгенерировать план тренировок: {weeks} нед × {dpw} дн/нед"
    if tool_name == "activate_workout_plan":
        return "Сделать план тренировок активным"
    if tool_name == "delete_workout_plan":
        return "Удалить план тренировок"
    if tool_name == "schedule_workout_plan":
        return "Распределить план по календарю"
    if tool_name == "reschedule_workout_entry":
        return f"Перенести тренировку на {args.get('new_date', '?')}"
    if tool_name == "toggle_workout_complete":
        return "Отметить выполненной/невыполненной"
    if tool_name == "log_exercise_set":
        reps = args.get("reps_completed")
        weight = args.get("weight_kg")
        return f"Записать подход: {reps or '-'} повт × {weight or '-'} кг"
    if tool_name == "generate_nutrition_plan":
        meals = args.get("meals_per_day", 4)
        return f"Сгенерировать план питания на {meals} приёма"
    if tool_name == "activate_nutrition_plan":
        return "Сделать план питания активным"
    if tool_name == "delete_nutrition_plan":
        return "Удалить план питания"
    if tool_name == "log_food":
        return f"Записать в дневник: {args.get('food_name', '?')} ({args.get('quantity_g', '?')} г)"
    if tool_name == "delete_nutrition_log":
        return "Удалить запись из дневника"
    if tool_name == "log_weight":
        return f"Записать вес: {args.get('weight_kg', '?')} кг"
    if tool_name == "delete_weight_log":
        return "Удалить запись веса"
    if tool_name == "log_measurement":
        return f"Записать замер: {args.get('measurement_type', '?')} = {args.get('value_cm', '?')} см"
    if tool_name == "delete_measurement":
        return "Удалить замер"
    return tool_name


def summarize_tool_result(tool_name: str, result: Any) -> str:
    """Short user-facing line shown after a tool finishes."""
    if not isinstance(result, dict):
        return "Готово"

    if tool_name == "get_profile":
        if not result.get("profile_filled"):
            return "Профиль не заполнен"
        bits = []
        if result.get("gender"):
            bits.append({"male": "М", "female": "Ж"}.get(result["gender"], result["gender"]))
        if result.get("age"):
            bits.append(f"{result['age']} лет")
        if result.get("height_cm"):
            bits.append(f"{result['height_cm']:.0f} см")
        if result.get("weight_kg"):
            bits.append(f"{result['weight_kg']:.1f} кг")
        return "Профиль: " + ", ".join(bits) if bits else "Профиль прочитан"
    if tool_name == "get_active_plans":
        wp = result.get("active_workout_plan")
        np = result.get("active_nutrition_plan")
        bits = []
        bits.append(f"тренировки: {wp['title'] if wp else 'нет'}")
        bits.append(f"питание: {np['title'] if np else 'нет'}")
        return "Активно — " + "; ".join(bits)
    if tool_name == "analyze_progress":
        days = result.get("period_days", "?")
        completed = result.get("workouts_completed", 0)
        return f"За {days} дн: тренировок {completed}, подходов {result.get('sets_logged', 0)}"
    if tool_name in {"list_workout_plans", "list_nutrition_plans"}:
        return f"Планов: {len(result) if isinstance(result, list) else 0}"
    if tool_name == "list_exercises":
        return f"Найдено упражнений: {len(result) if isinstance(result, list) else 0}"
    if tool_name in {"get_weight_history", "get_measurements_history", "get_recent_workout_logs", "get_workout_calendar"}:
        n = len(result) if isinstance(result, list) else 0
        return f"Записей: {n}"
    if tool_name == "get_today_nutrition_log":
        totals = result.get("totals", {})
        return f"Сегодня: {totals.get('calories', 0):.0f} ккал, {totals.get('protein_g', 0):.0f} г белка"
    if tool_name == "generate_workout_plan":
        return f"План создан: {result.get('title', '')} ({result.get('sessions_count', '?')} сессий)"
    if tool_name == "generate_nutrition_plan":
        return f"План создан: {result.get('daily_calories', '?')} ккал/день, {result.get('meals_count', '?')} приёма"
    if tool_name == "schedule_workout_plan":
        return f"Распределено {result.get('scheduled', 0)} тренировок"
    if tool_name == "log_weight":
        return f"Вес записан: {result.get('weight_kg')} кг"
    if tool_name == "log_food":
        return result.get("message", "Запись добавлена")
    if "message" in result:
        return result["message"]
    if result.get("ok"):
        return "Готово"
    return "Готово"


# Convenience: list of tool names for quick membership checks
WRITE_TOOL_NAMES = set(WRITE_TOOLS.keys())


def is_write_tool(name: str) -> bool:
    return name in WRITE_TOOL_NAMES
