from datetime import date

from pydantic import BaseModel


class GenerateNutritionRequest(BaseModel):
    goal: str | None = None
    daily_calories: int | None = None
    meals_per_day: int = 4


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


class NutritionLogCreate(BaseModel):
    food_name: str
    meal_type: str
    quantity_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    photo_url: str | None = None
    notes: str | None = None
    logged_at: str | None = None
    food_item_id: str | None = None


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
