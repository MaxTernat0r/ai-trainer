from datetime import date

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.nutrition import FoodItem, NutritionLog, NutritionPlan
from app.models.user import User
from app.schemas.nutrition import (
    DailySummary,
    FoodItemRead,
    FoodRecognitionResult,
    GenerateNutritionRequest,
    NutritionLogCreate,
    NutritionLogRead,
    NutritionPlanListRead,
    NutritionPlanRead,
    MealRead,
    MealItemRead,
)

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.post("/generate", response_model=NutritionPlanRead)
async def generate_nutrition(
    data: GenerateNutritionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    from app.services.ai.nutrition_generator import generate_nutrition_plan

    plan = await generate_nutrition_plan(user, data, db)
    return plan


@router.get("/plans", response_model=list[NutritionPlanListRead])
async def list_plans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(NutritionPlan).where(NutritionPlan.user_id == user.id).order_by(NutritionPlan.created_at.desc())
    )
    return [
        NutritionPlanListRead(
            id=str(p.id),
            title=p.title,
            daily_calories=p.daily_calories,
            daily_protein_g=p.daily_protein_g,
            daily_fat_g=p.daily_fat_g,
            daily_carbs_g=p.daily_carbs_g,
            is_active=p.is_active,
        )
        for p in result.scalars()
    ]


@router.get("/plans/{plan_id}", response_model=NutritionPlanRead)
async def get_plan(
    plan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(NutritionPlan).where(NutritionPlan.id == plan_id, NutritionPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Nutrition plan")

    meals = []
    for m in plan.meals:
        items = []
        for mi in m.items:
            items.append(
                MealItemRead(
                    id=str(mi.id),
                    food_item=FoodItemRead(
                        id=str(mi.food_item.id),
                        name=mi.food_item.name,
                        name_ru=mi.food_item.name_ru,
                        brand=mi.food_item.brand,
                        calories_per_100g=mi.food_item.calories_per_100g,
                        protein_per_100g=mi.food_item.protein_per_100g,
                        fat_per_100g=mi.food_item.fat_per_100g,
                        carbs_per_100g=mi.food_item.carbs_per_100g,
                        fiber_per_100g=mi.food_item.fiber_per_100g,
                        serving_size_g=mi.food_item.serving_size_g,
                        category=mi.food_item.category,
                    ),
                    quantity_g=mi.quantity_g,
                    notes=mi.notes,
                )
            )
        meals.append(
            MealRead(
                id=str(m.id),
                name=m.name,
                order_index=m.order_index,
                target_calories=m.target_calories,
                items=items,
            )
        )

    return NutritionPlanRead(
        id=str(plan.id),
        title=plan.title,
        daily_calories=plan.daily_calories,
        daily_protein_g=plan.daily_protein_g,
        daily_fat_g=plan.daily_fat_g,
        daily_carbs_g=plan.daily_carbs_g,
        is_ai_generated=plan.is_ai_generated,
        is_active=plan.is_active,
        meals=meals,
    )


@router.post("/plans/{plan_id}/activate")
async def activate_plan(
    plan_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await db.execute(
        update(NutritionPlan).where(NutritionPlan.user_id == user.id).values(is_active=False)
    )
    result = await db.execute(
        select(NutritionPlan).where(NutritionPlan.id == plan_id, NutritionPlan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundError("Nutrition plan")
    plan.is_active = True
    return {"detail": "Plan activated"}


@router.get("/foods", response_model=list[FoodItemRead])
async def search_foods(
    search: str = Query(""),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    query = select(FoodItem)
    if search:
        query = query.where(
            FoodItem.name_ru.ilike(f"%{search}%") | FoodItem.name.ilike(f"%{search}%")
        )
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return [
        FoodItemRead(
            id=str(f.id),
            name=f.name,
            name_ru=f.name_ru,
            brand=f.brand,
            calories_per_100g=f.calories_per_100g,
            protein_per_100g=f.protein_per_100g,
            fat_per_100g=f.fat_per_100g,
            carbs_per_100g=f.carbs_per_100g,
            fiber_per_100g=f.fiber_per_100g,
            serving_size_g=f.serving_size_g,
            category=f.category,
        )
        for f in result.scalars()
    ]


@router.post("/log", response_model=NutritionLogRead)
async def log_food(
    data: NutritionLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    log = NutritionLog(
        user_id=user.id,
        food_item_id=data.food_item_id,
        food_name=data.food_name,
        meal_type=data.meal_type,
        quantity_g=data.quantity_g,
        calories=data.calories,
        protein_g=data.protein_g,
        fat_g=data.fat_g,
        carbs_g=data.carbs_g,
        logged_at=data.logged_at,
        notes=data.notes,
    )
    db.add(log)
    await db.flush()
    return NutritionLogRead(
        id=str(log.id),
        food_name=log.food_name,
        meal_type=log.meal_type,
        quantity_g=log.quantity_g,
        calories=log.calories,
        protein_g=log.protein_g,
        fat_g=log.fat_g,
        carbs_g=log.carbs_g,
        logged_at=log.logged_at,
        notes=log.notes,
    )


@router.get("/log", response_model=list[NutritionLogRead])
async def get_food_log(
    date_from: date = Query(...),
    date_to: date = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(NutritionLog)
        .where(
            NutritionLog.user_id == user.id,
            NutritionLog.logged_at >= date_from,
            NutritionLog.logged_at <= date_to,
        )
        .order_by(NutritionLog.logged_at.desc())
    )
    return [
        NutritionLogRead(
            id=str(l.id),
            food_name=l.food_name,
            meal_type=l.meal_type,
            quantity_g=l.quantity_g,
            calories=l.calories,
            protein_g=l.protein_g,
            fat_g=l.fat_g,
            carbs_g=l.carbs_g,
            photo_url=l.photo_url,
            logged_at=l.logged_at,
            notes=l.notes,
        )
        for l in result.scalars()
    ]


@router.get("/daily-summary", response_model=DailySummary)
async def daily_summary(
    target_date: date = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(
            func.coalesce(func.sum(NutritionLog.calories), 0).label("total_cal"),
            func.coalesce(func.sum(NutritionLog.protein_g), 0).label("total_p"),
            func.coalesce(func.sum(NutritionLog.fat_g), 0).label("total_f"),
            func.coalesce(func.sum(NutritionLog.carbs_g), 0).label("total_c"),
            func.count(NutritionLog.id).label("count"),
        ).where(
            NutritionLog.user_id == user.id,
            NutritionLog.logged_at == target_date,
        )
    )
    row = result.one()
    return DailySummary(
        date=target_date,
        total_calories=float(row.total_cal),
        total_protein_g=float(row.total_p),
        total_fat_g=float(row.total_f),
        total_carbs_g=float(row.total_c),
        meals_logged=int(row.count),
    )


@router.post("/recognize", response_model=FoodRecognitionResult)
async def recognize_food(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    from app.services.ai.food_recognizer import recognize_food_from_photo

    image_data = await file.read()
    return await recognize_food_from_photo(image_data)
