from datetime import date, datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.validators import MealType


class GenerateNutritionRequest(BaseModel):
    goal: str | None = Field(None, max_length=64)
    daily_calories: int | None = Field(None, ge=500, le=10000)
    meals_per_day: int = Field(4, ge=1, le=10)


class FoodItemRead(BaseModel):
    id: str
    name: str
    name_ru: str
    brand: str | None = None
    calories_per_100g: float
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    fiber_per_100g: float | None = None
    serving_size_g: float | None = None
    category: str | None = None

    model_config = {"from_attributes": True}


class MealItemRead(BaseModel):
    id: str
    food_item: FoodItemRead
    quantity_g: float
    notes: str | None = None

    model_config = {"from_attributes": True}


class MealRead(BaseModel):
    id: str
    name: str
    order_index: int
    target_calories: int | None = None
    items: list[MealItemRead] = []

    model_config = {"from_attributes": True}


class NutritionPlanRead(BaseModel):
    id: str
    title: str
    daily_calories: int
    daily_protein_g: float
    daily_fat_g: float
    daily_carbs_g: float
    is_ai_generated: bool
    is_active: bool
    meals: list[MealRead] = []

    model_config = {"from_attributes": True}


class NutritionPlanListRead(BaseModel):
    id: str
    title: str
    daily_calories: int
    daily_protein_g: float
    daily_fat_g: float
    daily_carbs_g: float
    is_active: bool

    model_config = {"from_attributes": True}


def _validate_safe_url(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if value.startswith("/"):
        return value
    lowered = value.lower()
    if lowered.startswith(("http://", "https://")):
        return value
    raise ValueError("photo_url must be http(s) or a relative path starting with /")


def _validate_logged_at(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError) as exc:
        raise ValueError("invalid date format (expected ISO-8601)") from exc
    today = date.today()
    if parsed > today + timedelta(days=1):
        raise ValueError("logged_at cannot be in the future")
    if parsed < today - timedelta(days=365 * 5):
        raise ValueError("logged_at is too far in the past")
    return parsed.isoformat()


class NutritionLogCreate(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=200)
    meal_type: MealType
    quantity_g: float = Field(..., gt=0, le=10000)
    calories: float = Field(..., ge=0, le=20000)
    protein_g: float = Field(..., ge=0, le=2000)
    fat_g: float = Field(..., ge=0, le=2000)
    carbs_g: float = Field(..., ge=0, le=2000)
    photo_url: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)
    logged_at: str | None = None
    food_item_id: UUID | None = None

    @field_validator("photo_url")
    @classmethod
    def _validate_photo_url(cls, v: str | None) -> str | None:
        return _validate_safe_url(v)

    @field_validator("logged_at")
    @classmethod
    def _validate_logged_at_field(cls, v: str | None) -> str | None:
        return _validate_logged_at(v)


class NutritionLogRead(BaseModel):
    id: str
    food_name: str
    meal_type: str
    quantity_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    photo_url: str | None = None
    logged_at: date
    notes: str | None = None

    model_config = {"from_attributes": True}


class DailySummary(BaseModel):
    date: date
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    meals_logged: int


class FoodRecognitionResult(BaseModel):
    is_food: bool
    items: list["RecognizedFoodItem"]
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float


class RecognizedFoodItem(BaseModel):
    food_name: str
    confidence_score: float
    portion_grams: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
