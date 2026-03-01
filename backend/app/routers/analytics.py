from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.analytics import MeasurementLog, WeightLog
from app.models.nutrition import NutritionLog
from app.models.user import User
from app.schemas.analytics import (
    DashboardData,
    MeasurementCreate,
    MeasurementRead,
    WeightLogCreate,
    WeightLogRead,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/weight", response_model=WeightLogRead)
async def log_weight(
    data: WeightLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    log = WeightLog(
        user_id=user.id,
        weight_kg=data.weight_kg,
        logged_at=data.logged_at,
    )
    db.add(log)
    await db.flush()
    return WeightLogRead(id=str(log.id), weight_kg=log.weight_kg, logged_at=log.logged_at)


@router.get("/weight", response_model=list[WeightLogRead])
async def get_weight_history(
    date_from: date = Query(...),
    date_to: date = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(WeightLog)
        .where(
            WeightLog.user_id == user.id,
            WeightLog.logged_at >= date_from,
            WeightLog.logged_at <= date_to,
        )
        .order_by(WeightLog.logged_at)
    )
    return [
        WeightLogRead(id=str(w.id), weight_kg=w.weight_kg, logged_at=w.logged_at)
        for w in result.scalars()
    ]


@router.post("/measurements", response_model=MeasurementRead)
async def log_measurement(
    data: MeasurementCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    log = MeasurementLog(
        user_id=user.id,
        measurement_type=data.measurement_type,
        value_cm=data.value_cm,
        logged_at=data.logged_at,
    )
    db.add(log)
    await db.flush()
    return MeasurementRead(
        id=str(log.id),
        measurement_type=log.measurement_type,
        value_cm=log.value_cm,
        logged_at=log.logged_at,
    )


@router.get("/measurements", response_model=list[MeasurementRead])
async def get_measurements(
    measurement_type: str | None = Query(None),
    date_from: date = Query(...),
    date_to: date = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    query = select(MeasurementLog).where(
        MeasurementLog.user_id == user.id,
        MeasurementLog.logged_at >= date_from,
        MeasurementLog.logged_at <= date_to,
    )
    if measurement_type:
        query = query.where(MeasurementLog.measurement_type == measurement_type)
    query = query.order_by(MeasurementLog.logged_at)

    result = await db.execute(query)
    return [
        MeasurementRead(
            id=str(m.id),
            measurement_type=m.measurement_type,
            value_cm=m.value_cm,
            logged_at=m.logged_at,
        )
        for m in result.scalars()
    ]


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    from datetime import timedelta

    today = date.today()

    # Latest weight
    weight_result = await db.execute(
        select(WeightLog)
        .where(WeightLog.user_id == user.id)
        .order_by(WeightLog.logged_at.desc())
        .limit(1)
    )
    latest_weight = weight_result.scalar_one_or_none()

    # Today's nutrition
    nutrition_result = await db.execute(
        select(
            func.coalesce(func.sum(NutritionLog.calories), 0),
            func.coalesce(func.sum(NutritionLog.protein_g), 0),
        ).where(NutritionLog.user_id == user.id, NutritionLog.logged_at == today)
    )
    cal_today, protein_today = nutrition_result.one()

    return DashboardData(
        current_weight=latest_weight.weight_kg if latest_weight else None,
        calories_today=float(cal_today),
        protein_today=float(protein_today),
    )
