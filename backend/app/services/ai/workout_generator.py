"""Workout plan generation using OpenAI API.

Generates structured workout programs based on user profile, goals,
available exercises, and medical restrictions. Uses OpenAI structured
output (JSON mode) to produce parseable workout plans.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.models.exercise import Exercise
from app.models.user import User
from app.models.workout import WorkoutExercise, WorkoutPlan, WorkoutSession
from app.schemas.workout import GenerateWorkoutRequest, WorkoutPlanRead
from app.services.ai.context_builder import build_user_context
from app.services.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)

WORKOUT_SYSTEM_PROMPT = """\
Ты — профессиональный спортивный тренер с опытом составления тренировочных программ.

Твоя задача — составить структурированную тренировочную программу для пользователя.

ПРАВИЛА:
1. Подбирай упражнения строго из предоставленного списка доступных упражнений (используй их exercise_id).
2. Учитывай уровень подготовки пользователя при выборе количества подходов и повторений.
3. НИКОГДА не включай упражнения, которые противоречат медицинским ограничениям пользователя.
4. Учитывай доступное оборудование.
5. Обеспечь прогрессивную нагрузку на протяжении программы.
6. Каждая тренировка должна включать разминочные и основные упражнения.
7. Сбалансируй нагрузку на разные мышечные группы в течение недели.

Отвечай ТОЛЬКО валидным JSON следующей структуры:
{
  "title": "Название программы",
  "description": "Описание программы",
  "goal": "цель (fat_loss | muscle_gain | strength | endurance | general_fitness)",
  "difficulty": "сложность (beginner | intermediate | advanced)",
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

Не добавляй никакого текста вне JSON. Только чистый JSON.
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


async def generate_workout_plan(
    user: User,
    request: GenerateWorkoutRequest,
    db: AsyncSession,
) -> WorkoutPlanRead:
    """Generate a complete workout plan using OpenAI API.

    Builds user context, queries available exercises, calls the AI model
    with structured output, parses the response, saves to database, and
    returns a WorkoutPlanRead schema.
    """
    try:
        # Build user context
        user_context = await build_user_context(user, db)

        # Load available exercises
        available_exercises = await _load_available_exercises(db)
        if not available_exercises:
            raise AIServiceError(
                "No exercises found in the database. Please seed the exercise catalog first."
            )
        exercise_list_text = _build_exercise_list_text(available_exercises)
        valid_exercise_ids = _build_valid_exercise_ids(available_exercises)

        # Build the user message with all context
        user_message = f"""\
Составь тренировочную программу со следующими параметрами:
- Длительность: {request.weeks} недель
- Дней тренировок в неделю: {request.days_per_week}
- Тип периодизации: {request.periodization}

ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
{user_context}

{exercise_list_text}
"""

        # Call OpenAI API
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": WORKOUT_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=4096,
        )

        raw_content = response.choices[0].message.content
        if not raw_content:
            raise AIServiceError("AI returned an empty response")

        # Parse the JSON response
        try:
            plan_data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI workout response: %s", e)
            raise AIServiceError("Failed to parse AI response into a valid workout plan")

        # Validate required fields
        if "sessions" not in plan_data or not plan_data["sessions"]:
            raise AIServiceError("AI generated an empty workout plan with no sessions")

        # Save WorkoutPlan to database
        workout_plan = WorkoutPlan(
            user_id=user.id,
            title=plan_data.get("title", "AI Workout Plan"),
            description=plan_data.get("description"),
            goal=plan_data.get("goal", "general_fitness"),
            difficulty=plan_data.get("difficulty", "intermediate"),
            duration_weeks=request.weeks,
            days_per_week=request.days_per_week,
            is_ai_generated=True,
            is_active=False,
            ai_prompt_snapshot=user_message[:2000],
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
                    exercise_id=exercise_id,
                    order_index=ex_idx,
                    target_sets=ex_data.get("target_sets", 3),
                    target_reps=str(ex_data.get("target_reps", "8-12")),
                    target_rest_seconds=ex_data.get("target_rest_seconds"),
                    notes=ex_data.get("notes"),
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
