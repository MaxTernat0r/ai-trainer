"""Nutrition plan generation using OpenAI API.

Generates structured meal plans based on user profile, caloric needs,
macro targets, and dietary preferences. Uses calorie_calculator for
TDEE/macro computation and OpenAI for meal plan generation.
"""

import json
import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.models.nutrition import FoodItem, Meal, MealItem, NutritionPlan
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.nutrition import GenerateNutritionRequest, NutritionPlanRead
from app.services.ai.calorie_calculator import (
    calculate_bmr,
    calculate_macro_targets,
    calculate_tdee,
)
from app.services.ai.context_builder import build_user_context
from app.services.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)

NUTRITION_SYSTEM_PROMPT = """\
Ты являешься профессиональным нутрициологом и диетологом со стажем работы в 10 лет. \
Помог сотням людей нормализовать питание, похудеть и набрать мышечную массу.

Твоя задача — составить детальный план питания для клиента на основе его данных и рассчитанных потребностей.

ПРАВИЛА:
1. Строго соблюдай указанную калорийность и распределение макронутриентов.
2. НИКОГДА не используй продукты, на которые у клиента аллергия или непереносимость.
3. По возможности исключай нелюбимые продукты клиента.
4. Учитывай медицинские ограничения.
5. Предлагай разнообразные, простые и доступные продукты.
6. Указывай количество каждого продукта в граммах.
7. Для каждого продукта указывай точное содержание калорий и БЖУ на 100г.
8. Распределяй калории между приёмами пищи равномерно.

Ответь СТРОГО валидным JSON без какого-либо дополнительного текста. Структура:
{
  "title": "Название плана питания",
  "meals": [
    {
      "name": "Завтрак",
      "target_calories": 500,
      "items": [
        {
          "food_name": "Название продукта (на русском)",
          "food_name_en": "Food name (in English)",
          "quantity_g": 150,
          "calories_per_100g": 130,
          "protein_per_100g": 11,
          "fat_per_100g": 3.5,
          "carbs_per_100g": 18,
          "category": "dairy",
          "notes": "опциональные заметки"
        }
      ]
    }
  ]
}

НЕ ПИШИ НИЧЕГО КРОМЕ JSON. Никаких пояснений, комментариев или markdown — только чистый JSON.
"""


async def _get_user_profile(user: User, db: AsyncSession) -> UserProfile | None:
    """Load the user profile from the database."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    return result.scalar_one_or_none()


def _compute_macro_targets(profile: UserProfile) -> dict:
    """Calculate TDEE and macro targets from the user profile."""
    weight = profile.weight_kg or 70.0
    height = profile.height_cm or 170.0
    gender = profile.gender or "male"
    activity_level = profile.activity_level or "moderately_active"
    goal = profile.goal or "general_fitness"

    # Calculate age
    age = 30  # default
    if profile.date_of_birth:
        today = date.today()
        age = today.year - profile.date_of_birth.year - (
            (today.month, today.day)
            < (profile.date_of_birth.month, profile.date_of_birth.day)
        )

    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    macros = calculate_macro_targets(tdee, goal)

    return macros


async def _find_or_create_food_item(
    food_data: dict,
    db: AsyncSession,
) -> FoodItem:
    """Find existing food item by name or create a new one.

    AI-generated food items are marked as unverified.
    """
    food_name_ru = food_data.get("food_name", "Unknown food")
    food_name_en = food_data.get("food_name_en", food_name_ru)

    # Try to find an existing food item by Russian name (case-insensitive)
    result = await db.execute(
        select(FoodItem).where(FoodItem.name_ru.ilike(food_name_ru))
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new food item from AI data
    food_item = FoodItem(
        name=food_name_en,
        name_ru=food_name_ru,
        calories_per_100g=food_data.get("calories_per_100g", 0),
        protein_per_100g=food_data.get("protein_per_100g", 0),
        fat_per_100g=food_data.get("fat_per_100g", 0),
        carbs_per_100g=food_data.get("carbs_per_100g", 0),
        serving_size_g=food_data.get("quantity_g"),
        category=food_data.get("category"),
        is_verified=False,
    )
    db.add(food_item)
    await db.flush()

    return food_item


async def generate_nutrition_plan(
    user: User,
    request: GenerateNutritionRequest,
    db: AsyncSession,
) -> NutritionPlanRead:
    """Generate a complete nutrition plan using OpenAI API.

    Calculates the user's TDEE and macro targets, builds context,
    calls the AI model, parses the response, saves to database,
    and returns a NutritionPlanRead schema.
    """
    try:
        # Load user profile for calorie calculations
        profile = await _get_user_profile(user, db)
        if not profile:
            raise AIServiceError(
                "User profile is required to generate a nutrition plan. "
                "Please complete your profile first."
            )

        # Calculate TDEE and macro targets
        macros = _compute_macro_targets(profile)

        # Use profile defaults when not provided
        meals_per_day = request.meals_per_day or profile.meals_per_day or 3

        # Build user context
        user_context = await build_user_context(user, db)

        # Build dietary restrictions note
        dietary_notes = ""
        if profile.food_allergies:
            dietary_notes += f"\n\nВАЖНО — АЛЛЕРГИИ И НЕПЕРЕНОСИМОСТИ (ИСКЛЮЧИТЬ ИЗ ПЛАНА):\n{profile.food_allergies}"
        if profile.disliked_foods:
            dietary_notes += f"\n\nНЕЛЮБИМЫЕ ПРОДУКТЫ (по возможности исключить):\n{profile.disliked_foods}"

        # Build the user message
        user_message = f"""\
{user_context}

Составь ему план питания со следующими рассчитанными параметрами:
- Приёмов пищи в день: {meals_per_day}
- Целевая калорийность: {macros['target_kcal']} ккал/день
- Белки: {macros['protein_g']} г/день
- Жиры: {macros['fat_g']} г/день
- Углеводы: {macros['carbs_g']} г/день
- TDEE (поддержание): {macros['tdee']} ккал/день{dietary_notes}
"""

        # Call OpenAI API
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": NUTRITION_SYSTEM_PROMPT},
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
            logger.error("Failed to parse AI nutrition response: %s", e)
            raise AIServiceError("Failed to parse AI response into a valid nutrition plan")

        # Validate required fields
        if "meals" not in plan_data or not plan_data["meals"]:
            raise AIServiceError("AI generated an empty nutrition plan with no meals")

        # Save NutritionPlan to database
        nutrition_plan = NutritionPlan(
            user_id=user.id,
            title=plan_data.get("title", "AI Nutrition Plan"),
            daily_calories=macros["target_kcal"],
            daily_protein_g=macros["protein_g"],
            daily_fat_g=macros["fat_g"],
            daily_carbs_g=macros["carbs_g"],
            is_ai_generated=True,
            is_active=False,
            ai_prompt_snapshot=user_message[:2000],
        )
        db.add(nutrition_plan)
        await db.flush()

        # Save Meals and MealItems
        for meal_idx, meal_data in enumerate(plan_data["meals"]):
            meal = Meal(
                nutrition_plan_id=nutrition_plan.id,
                name=meal_data.get("name", f"Meal {meal_idx + 1}"),
                order_index=meal_idx,
                target_calories=meal_data.get("target_calories"),
            )
            db.add(meal)
            await db.flush()

            items_data = meal_data.get("items", [])
            for item_data in items_data:
                # Find or create the food item
                food_item = await _find_or_create_food_item(item_data, db)

                meal_item = MealItem(
                    meal_id=meal.id,
                    food_item_id=food_item.id,
                    quantity_g=item_data.get("quantity_g", 100),
                    notes=item_data.get("notes"),
                )
                db.add(meal_item)

        await db.commit()

        # Refresh to load all relationships for the response
        await db.refresh(nutrition_plan, attribute_names=["meals"])
        for meal in nutrition_plan.meals:
            await db.refresh(meal, attribute_names=["items"])
            for item in meal.items:
                await db.refresh(item, attribute_names=["food_item"])

        return _build_plan_read(nutrition_plan)

    except AIServiceError:
        raise
    except Exception as e:
        logger.exception("Unexpected error during nutrition plan generation")
        await db.rollback()
        raise AIServiceError(f"Failed to generate nutrition plan: {e}") from e


def _build_plan_read(plan: NutritionPlan) -> NutritionPlanRead:
    """Convert a NutritionPlan ORM model to a NutritionPlanRead schema."""
    return NutritionPlanRead(
        id=str(plan.id),
        title=plan.title,
        daily_calories=plan.daily_calories,
        daily_protein_g=plan.daily_protein_g,
        daily_fat_g=plan.daily_fat_g,
        daily_carbs_g=plan.daily_carbs_g,
        is_ai_generated=plan.is_ai_generated,
        is_active=plan.is_active,
        meals=[
            {
                "id": str(m.id),
                "name": m.name,
                "order_index": m.order_index,
                "target_calories": m.target_calories,
                "items": [
                    {
                        "id": str(item.id),
                        "food_item": {
                            "id": str(item.food_item.id),
                            "name": item.food_item.name,
                            "name_ru": item.food_item.name_ru,
                            "brand": item.food_item.brand,
                            "calories_per_100g": item.food_item.calories_per_100g,
                            "protein_per_100g": item.food_item.protein_per_100g,
                            "fat_per_100g": item.food_item.fat_per_100g,
                            "carbs_per_100g": item.food_item.carbs_per_100g,
                            "fiber_per_100g": item.food_item.fiber_per_100g,
                            "serving_size_g": item.food_item.serving_size_g,
                            "category": item.food_item.category,
                        },
                        "quantity_g": item.quantity_g,
                        "notes": item.notes,
                    }
                    for item in m.items
                ],
            }
            for m in plan.meals
        ],
    )
