import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel


class FoodItem(BaseModel):
    __tablename__ = "food_items"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    protein_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fiber_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    serving_size_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class NutritionPlan(BaseModel):
    __tablename__ = "nutrition_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    daily_calories: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    daily_fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    daily_carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_prompt_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="nutrition_plans")  # type: ignore[name-defined]  # noqa: F821
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="nutrition_plan", lazy="selectin", order_by="Meal.order_index"
    )


class Meal(BaseModel):
    __tablename__ = "meals"

    nutrition_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrition_plans.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    target_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)

    nutrition_plan: Mapped["NutritionPlan"] = relationship(back_populates="meals")
    items: Mapped[list["MealItem"]] = relationship(back_populates="meal", lazy="selectin")


class MealItem(BaseModel):
    __tablename__ = "meal_items"

    meal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False
    )
    food_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("food_items.id"), nullable=False
    )
    quantity_g: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(200), nullable=True)

    meal: Mapped["Meal"] = relationship(back_populates="items")
    food_item: Mapped["FoodItem"] = relationship(lazy="selectin")


class NutritionLog(BaseModel):
    __tablename__ = "nutrition_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    food_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("food_items.id"), nullable=True
    )
    food_name: Mapped[str] = mapped_column(String(200), nullable=False)
    meal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity_g: Mapped[float] = mapped_column(Float, nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logged_at: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
