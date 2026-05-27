"""Workout plan generation using the configured AI provider.

Generates structured workout programs based on user profile, goals,
available exercises, and medical restrictions.
"""

import json
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AIServiceError
from app.models.exercise import Exercise
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutPlan, WorkoutSession
from app.schemas.workout import GenerateWorkoutRequest, WorkoutPlanRead
from app.services.ai.context_builder import build_user_context, extract_health_restrictions
from app.services.ai.provider import generate_json_completion, get_configured_ai_provider

logger = logging.getLogger(__name__)


def _clamp_int(value, default: int, lo: int, hi: int) -> int:
    """Coerce AI-returned int into [lo, hi]; default when unparsable."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(v, hi))


def _clamp_optional_int(value, lo: int, hi: int) -> int | None:
    """Same as _clamp_int but None if AI omitted the field."""
    if value is None:
        return None
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    return max(lo, min(v, hi))

WORKOUT_SYSTEM_PROMPT = """\
Ты являешься профессиональным фитнес-тренером со стажем работы в 10 лет. \
Воспитал много и олимпийских спортсменов, и просто помог людям влюбиться в спорт и похудеть.

Твоя задача — составить персонализированную тренировочную программу для клиента.

ПРАВИЛА:
1. Подбирай упражнения ТОЛЬКО из предоставленного списка доступных упражнений (используй их exercise_id).
2. Учитывай уровень подготовки при выборе количества подходов и повторений.
3. НИКОГДА не включай упражнения, которые противоречат медицинским ограничениям или травмам пользователя. При травмах ног и нижних конечностей — исключи бег, прыжки, скакалку, выпады с прыжком, плиометрику, приседания и любую ударную нагрузку на ноги. При травмах спины — исключи становую тягу, наклоны со штангой, тяжёлые приседания. При травмах плеча — исключи жимы над головой и подтягивания. При сомнениях — выбирай безопасную альтернативу или замени на упражнение для другой группы мышц.
4. Учитывай доступное оборудование.
5. Обеспечь прогрессивную нагрузку на протяжении программы.
6. Каждая тренировка должна включать разминочные и основные упражнения.
7. Сбалансируй нагрузку на разные мышечные группы в течение недели.
8. Поле sessions — это шаблоны тренировочных дней недели. НЕ создавай отдельные sessions для каждой недели программы.
9. Количество sessions должно строго соответствовать запрошенному количеству тренировочных дней в неделю.
10. В каждой тренировке должно быть не больше 5 упражнений, включая разминку.
11. Пиши короткие заметки: одна короткая фраза на session/exercise.
12. Возвращай компактный JSON без лишних пробелов и переносов, если это возможно.

Ответь СТРОГО валидным JSON без какого-либо дополнительного текста. Структура:
{
  "title": "Название программы",
  "description": "Краткое описание программы",
  "goal": "fat_loss | muscle_gain | strength | endurance | general_fitness",
  "difficulty": "beginner | intermediate | advanced",
  "sessions": [
    {
      "day_number": 1,
      "name": "Название тренировки (например: Грудь и трицепс)",
      "notes": "Заметки к тренировке",
      "exercises": [
        {
          "exercise_id": "uuid упражнения из списка",
          "target_sets": 3,
          "target_reps": "8-12",
          "target_rest_seconds": 90,
          "notes": "заметки к упражнению"
        }
      ]
    }
  ]
}

НЕ ПИШИ НИЧЕГО КРОМЕ JSON. Никаких пояснений, комментариев или markdown — только чистый JSON.
"""


async def _load_available_exercises(db: AsyncSession) -> list[dict]:
    """Load all exercises from the database for inclusion in the prompt."""
    result = await db.execute(
        select(Exercise).order_by(Exercise.name)
    )
    exercises = result.scalars().all()

    exercise_list = []
    for ex in exercises:
        equipment_name = ex.equipment.name_ru if ex.equipment else "без оборудования"
        muscle_groups = []
        for emg in ex.muscle_groups:
            mg = emg.muscle_group
            role = "основная" if emg.is_primary else "вспомогательная"
            muscle_groups.append(f"{mg.name_ru} ({role})")

        exercise_list.append({
            "exercise_id": str(ex.id),
            "name": ex.name,
            "name_ru": ex.name_ru,
            "difficulty": ex.difficulty,
            "type": ex.exercise_type,
            "equipment": equipment_name,
            "muscle_groups": muscle_groups,
        })

    return exercise_list


def _build_exercise_list_text(exercises: list[dict]) -> str:
    """Format the exercise list for inclusion in the AI prompt."""
    lines = ["ДОСТУПНЫЕ УПРАЖНЕНИЯ (используй ТОЛЬКО exercise_id из этого списка):"]
    for ex in exercises:
        mg_str = ", ".join(ex["muscle_groups"]) if ex["muscle_groups"] else "не указаны"
        lines.append(
            f'- exercise_id: {ex["exercise_id"]} | '
            f'{ex["name_ru"]} ({ex["name"]}) | '
            f'Сложность: {ex["difficulty"]} | '
            f'Тип: {ex["type"]} | '
            f'Оборудование: {ex["equipment"]} | '
            f'Мышцы: {mg_str}'
        )
    return "\n".join(lines)


def _build_valid_exercise_ids(exercises: list[dict]) -> set[str]:
    """Extract a set of valid exercise IDs for validation."""
    return {ex["exercise_id"] for ex in exercises}


def _exercise_matches(exercise: dict, keywords: list[str]) -> bool:
    haystack = " ".join(
        [
            exercise.get("name", ""),
            exercise.get("name_ru", ""),
            exercise.get("equipment", ""),
            " ".join(exercise.get("muscle_groups", [])),
        ]
    ).lower()
    return any(keyword.lower() in haystack for keyword in keywords)


def _select_fallback_exercises(
    exercises: list[dict], keywords: list[str], count: int
) -> list[dict]:
    selected = [ex for ex in exercises if _exercise_matches(ex, keywords)]
    if len(selected) < count:
        selected.extend(ex for ex in exercises if ex not in selected)
    return selected[:count]


def _build_fallback_workout_plan_data(
    request: GenerateWorkoutRequest,
    available_exercises: list[dict],
) -> dict:
    """Build a deterministic starter plan when OpenAI is not configured."""
    templates = [
        {
            "name": "Верх тела",
            "keywords": ["груд", "плеч", "трицеп", "жим", "отжим"],
            "notes": "Работайте в умеренном темпе, оставляя 1-2 повтора в запасе.",
        },
        {
            "name": "Низ тела",
            "keywords": ["ног", "бедр", "ягод", "присед", "выпад", "тяга"],
            "notes": "Следите за техникой колена и не работайте через боль.",
        },
        {
            "name": "Спина и корпус",
            "keywords": ["спин", "бицеп", "тяга", "подтяг", "планк", "скруч"],
            "notes": "Держите корпус стабильным и контролируйте амплитуду.",
        },
        {
            "name": "Функциональная тренировка",
            "keywords": ["кардио", "бег", "греб", "кор", "пресс", "планк"],
            "notes": "Держите пульс в комфортной зоне и отдыхайте по самочувствию.",
        },
    ]

    sessions = []
    days_per_week = max(1, min(request.days_per_week, 7))
    for day_idx in range(days_per_week):
        template = templates[day_idx % len(templates)]
        selected = _select_fallback_exercises(
            available_exercises, template["keywords"], count=5
        )
        exercises = [
            {
                "exercise_id": exercise["exercise_id"],
                "target_sets": 3 if exercise.get("exercise_type") != "cardio" else 2,
                "target_reps": "8-12"
                if exercise.get("exercise_type") != "cardio"
                else "10-15 мин",
                "target_rest_seconds": 90
                if exercise.get("exercise_type") != "cardio"
                else 60,
                "notes": "Начните с комфортной нагрузки и добавляйте вес постепенно.",
            }
            for exercise in selected
        ]
        sessions.append(
            {
                "day_number": day_idx + 1,
                "name": template["name"],
                "notes": template["notes"],
                "exercises": exercises,
            }
        )

    return {
        "title": f"Базовая программа на {request.weeks} недель",
        "description": (
            "Резервная программа, созданная без обращения к OpenAI. "
            "Подходит для демонстрации MVP и стартовой тренировки."
        ),
        "goal": "general_fitness",
        "difficulty": "intermediate",
        "is_ai_generated": False,
        "sessions": sessions,
    }


async def _save_workout_plan(
    user: User,
    request: GenerateWorkoutRequest,
    prompt_snapshot: str,
    plan_data: dict,
    valid_exercise_ids: set[str],
    db: AsyncSession,
) -> WorkoutPlanRead:
    # Save WorkoutPlan to database
    workout_plan = WorkoutPlan(
        user_id=user.id,
        title=plan_data.get("title", "AI Workout Plan"),
        description=plan_data.get("description"),
        goal=plan_data.get("goal", "general_fitness"),
        difficulty=plan_data.get("difficulty", "intermediate"),
        duration_weeks=request.weeks,
        days_per_week=request.days_per_week,
        is_ai_generated=plan_data.get("is_ai_generated", True),
        is_active=False,
        ai_prompt_snapshot=prompt_snapshot[:2000],
    )
    db.add(workout_plan)
    await db.flush()

    # Save WorkoutSessions and WorkoutExercises
    for session_idx, session_data in enumerate(plan_data["sessions"]):
        session = WorkoutSession(
            workout_plan_id=workout_plan.id,
            day_number=session_data.get("day_number", session_idx + 1),
            name=session_data.get("name", f"Day {session_idx + 1}"),
            notes=session_data.get("notes"),
            order_index=session_idx,
        )
        db.add(session)
        await db.flush()

        exercises_data = session_data.get("exercises", [])
        for ex_idx, ex_data in enumerate(exercises_data):
            exercise_id = ex_data.get("exercise_id", "")

            # Validate exercise_id exists in our database
            if exercise_id not in valid_exercise_ids:
                logger.warning(
                    "AI referenced unknown exercise_id: %s, skipping",
                    exercise_id,
                )
                continue

            workout_exercise = WorkoutExercise(
                workout_session_id=session.id,
                exercise_id=uuid.UUID(exercise_id),
                order_index=ex_idx,
                target_sets=_clamp_int(ex_data.get("target_sets"), 3, 1, 12),
                target_reps=str(ex_data.get("target_reps", "8-12"))[:20],
                target_rest_seconds=_clamp_optional_int(
                    ex_data.get("target_rest_seconds"), 0, 1800
                ),
                notes=(ex_data.get("notes") or None),
            )
            db.add(workout_exercise)

    await db.commit()

    # Refresh to load all relationships for the response
    await db.refresh(workout_plan, attribute_names=["sessions"])
    for session in workout_plan.sessions:
        await db.refresh(session, attribute_names=["exercises"])
        for exercise in session.exercises:
            await db.refresh(exercise, attribute_names=["exercise"])

    # Build the response using the schema
    return _build_plan_read(workout_plan)


async def generate_workout_plan(
    user: User,
    request: GenerateWorkoutRequest,
    db: AsyncSession,
) -> WorkoutPlanRead:
    """Generate a complete workout plan using the configured AI provider.

    Builds user context, queries available exercises, calls the AI model
    with structured output, parses the response, saves to database, and
    returns a WorkoutPlanRead schema.
    """
    try:
        # Build user context
        user_context = await build_user_context(user, db)
        health_block = await extract_health_restrictions(user, db)

        # Load available exercises
        available_exercises = await _load_available_exercises(db)
        if not available_exercises:
            raise AIServiceError(
                "No exercises found in the database. Please seed the exercise catalog first."
            )
        exercise_list_text = _build_exercise_list_text(available_exercises)
        valid_exercise_ids = _build_valid_exercise_ids(available_exercises)

        # Build the user message with all context
        restrictions_section = ""
        if health_block:
            restrictions_section = (
                "\n\n"
                "==============================================\n"
                "ВАЖНО — МЕДИЦИНСКИЕ ОГРАНИЧЕНИЯ И ТРАВМЫ:\n"
                f"{health_block}\n"
                "СТРОГО учитывай эти ограничения при подборе упражнений. "
                "ИСКЛЮЧИ любые движения, которые могут травмировать или нагружать ограниченные зоны (см. правило 3 системы).\n"
                "=============================================="
            )

        user_message = f"""\
{user_context}{restrictions_section}

Составь ему тренировочную программу со следующими параметрами:
- Длительность: {request.weeks} недель
- Дней тренировок в неделю: {request.days_per_week}
- Тип периодизации: {request.periodization}

Сгенерируй ровно {request.days_per_week} sessions: по одному шаблону на каждый тренировочный день недели.
Не умножай sessions на количество недель; прогрессию опиши коротко в notes.
В каждой session используй 3-5 упражнений максимум.

{exercise_list_text}
"""

        if get_configured_ai_provider():
            raw_content = await generate_json_completion(
                WORKOUT_SYSTEM_PROMPT,
                user_message,
                temperature=0.3,
                max_tokens=8192,
            )

            # Parse the JSON response
            try:
                plan_data = json.loads(raw_content)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse AI workout response: %s", e)
                raise AIServiceError("Failed to parse AI response into a valid workout plan")
        else:
            logger.warning("AI provider is not configured; using fallback workout plan")
            plan_data = _build_fallback_workout_plan_data(
                request, available_exercises
            )

        # Validate required fields
        if "sessions" not in plan_data or not plan_data["sessions"]:
            raise AIServiceError("AI generated an empty workout plan with no sessions")

        return await _save_workout_plan(
            user, request, user_message, plan_data, valid_exercise_ids, db
        )

    except AIServiceError:
        raise
    except Exception as e:
        logger.exception("Unexpected error during workout generation")
        await db.rollback()
        raise AIServiceError(f"Failed to generate workout plan: {e}") from e


def _build_plan_read(plan: WorkoutPlan) -> WorkoutPlanRead:
    """Convert a WorkoutPlan ORM model to a WorkoutPlanRead schema."""
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
        sessions=[
            {
                "id": str(s.id),
                "day_number": s.day_number,
                "name": s.name,
                "notes": s.notes,
                "order_index": s.order_index,
                "exercises": [
                    {
                        "id": str(ex.id),
                        "exercise_id": str(ex.exercise_id),
                        "exercise_name": ex.exercise.name if ex.exercise else None,
                        "exercise_name_ru": ex.exercise.name_ru if ex.exercise else None,
                        "order_index": ex.order_index,
                        "target_sets": ex.target_sets,
                        "target_reps": ex.target_reps,
                        "target_rest_seconds": ex.target_rest_seconds,
                        "notes": ex.notes,
                        "logged_sets": [],
                    }
                    for ex in s.exercises
                ],
            }
            for s in plan.sessions
        ],
    )
