"""Nutrition plan generation using the configured AI provider.

Generates structured meal plans based on user profile, caloric needs,
macro targets, and dietary preferences. Uses calorie_calculator for
TDEE/macro computation.
"""

import json
import logging
from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.services.ai.provider import generate_json_completion, get_configured_ai_provider

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
9. Ровно столько meals, сколько запрошено приёмов пищи в день.
10. В каждом приёме пищи должно быть не больше 4 продуктов.
11. Пиши короткие заметки: одна короткая фраза на продукт или null.
12. Возвращай компактный JSON без лишних пробелов и переносов, если это возможно.

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


async def _load_food_catalog(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(FoodItem).order_by(FoodItem.name_ru))
    return [
        {
            "food_name": food.name_ru,
            "food_name_en": food.name,
            "calories_per_100g": food.calories_per_100g,
            "protein_per_100g": food.protein_per_100g,
            "fat_per_100g": food.fat_per_100g,
            "carbs_per_100g": food.carbs_per_100g,
            "category": food.category,
        }
        for food in result.scalars()
    ]


def _is_allowed_food(food: dict, profile: UserProfile) -> bool:
    haystack = " ".join(
        [
            food.get("food_name", ""),
            food.get("food_name_en", ""),
            food.get("category", "") or "",
        ]
    ).lower()
    allergies = (profile.food_allergies or "").lower()
    disliked = (profile.disliked_foods or "").lower()

    if "лактоз" in allergies and food.get("category") in {"dairy", "supplements"}:
        return False
    if "орех" in allergies and food.get("category") == "nuts":
        return False

    blocked_terms = [term.strip() for term in [*allergies.split(","), *disliked.split(",")]]
    return not any(term and term in haystack for term in blocked_terms)


def _pick_food(catalog: list[dict], keywords: list[str], profile: UserProfile) -> dict:
    allowed = [food for food in catalog if _is_allowed_food(food, profile)]
    for keyword in keywords:
        keyword_lower = keyword.lower()
        match = next(
            (
                food
                for food in allowed
                if keyword_lower in food.get("food_name", "").lower()
                or keyword_lower in food.get("food_name_en", "").lower()
            ),
            None,
        )
        if match:
            return match

    if allowed:
        return allowed[0]
    return catalog[0]


def _meal_item(food: dict, quantity_g: int, notes: str | None = None) -> dict:
    return {
        **food,
        "quantity_g": quantity_g,
        "notes": notes,
    }


def _build_fallback_nutrition_plan_data(
    profile: UserProfile,
    meals_per_day: int,
    macros: dict,
    catalog: list[dict],
) -> dict:
    """Build a deterministic meal plan when OpenAI is not configured."""
    templates = [
        {
            "name": "Завтрак",
            "items": [
                (["овсяная каша", "овсянка"], 250),
                (["яичный белок", "яйцо"], 120),
                (["банан", "яблоко"], 120),
            ],
        },
        {
            "name": "Обед",
            "items": [
                (["куриная грудка", "грудка индейки", "тофу"], 180),
                (["гречка", "бурый рис", "киноа"], 220),
                (["брокколи", "шпинат", "салат"], 150),
            ],
        },
        {
            "name": "Перекус",
            "items": [
                (["яблоко", "груша", "киви"], 180),
                (["хумус", "рисовые хлебцы", "миндаль"], 80),
            ],
        },
        {
            "name": "Ужин",
            "items": [
                (["треска", "тунец", "лосось", "темпе"], 180),
                (["картофель", "батат", "рис"], 220),
                (["огурец", "помидор", "перец"], 180),
            ],
        },
        {
            "name": "Полдник",
            "items": [
                (["тофу", "чечевица", "нут"], 140),
                (["цельнозерновой хлеб", "рисовые хлебцы"], 70),
            ],
        },
        {
            "name": "Второй ужин",
            "items": [
                (["соевое молоко", "кефир", "творог"], 250),
                (["клубника", "голубика", "малина"], 120),
            ],
        },
    ]

    meal_count = max(2, min(meals_per_day, len(templates)))
    calories_per_meal = round(macros["target_kcal"] / meal_count)
    meals = []
    for meal_idx, template in enumerate(templates[:meal_count]):
        meals.append(
            {
                "name": template["name"],
                "target_calories": calories_per_meal,
                "items": [
                    _meal_item(
                        _pick_food(catalog, keywords, profile),
                        quantity_g,
                        "Резервный план без обращения к OpenAI.",
                    )
                    for keywords, quantity_g in template["items"]
                ],
            }
        )

    return {
        "title": "Базовый план питания",
        "is_ai_generated": False,
        "meals": meals,
    }


async def generate_nutrition_plan(
    user: User,
    request: GenerateNutritionRequest,
    db: AsyncSession,
) -> NutritionPlanRead:
    """Generate a complete nutrition plan using the configured AI provider.

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

Сгенерируй ровно {meals_per_day} meals. В каждом meal используй 2-4 продукта максимум.
"""

        if get_configured_ai_provider():
            raw_content = await generate_json_completion(
                NUTRITION_SYSTEM_PROMPT,
                user_message,
                temperature=0.3,
                max_tokens=8192,
            )

            # Parse the JSON response
            try:
                plan_data = json.loads(raw_content)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse AI nutrition response: %s", e)
                raise AIServiceError("Failed to parse AI response into a valid nutrition plan")
        else:
            logger.warning("AI provider is not configured; using fallback nutrition plan")
            catalog = await _load_food_catalog(db)
            if not catalog:
                raise AIServiceError(
                    "No foods found in the database. Please seed the food catalog first."
                )
            plan_data = _build_fallback_nutrition_plan_data(
                profile, meals_per_day, macros, catalog
            )

        # Validate required fields
        if "meals" not in plan_data or not plan_data["meals"]:
            raise AIServiceError("AI generated an empty nutrition plan with no meals")

        # Deactivate existing plans
        await db.execute(
            update(NutritionPlan)
            .where(NutritionPlan.user_id == user.id)
            .values(is_active=False)
        )

        # Save NutritionPlan to database
        nutrition_plan = NutritionPlan(
            user_id=user.id,
            title=plan_data.get("title", "AI Nutrition Plan"),
            daily_calories=macros["target_kcal"],
            daily_protein_g=macros["protein_g"],
            daily_fat_g=macros["fat_g"],
            daily_carbs_g=macros["carbs_g"],
            is_ai_generated=plan_data.get("is_ai_generated", True),
            is_active=True,
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
