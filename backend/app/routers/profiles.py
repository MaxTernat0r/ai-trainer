from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.base  # noqa: F401 — ensure all models are registered for relationships

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.profile import MedicalRestriction, UserMedicalRestriction, UserProfile
from app.models.user import User
from app.schemas.profile import MedicalRestrictionRead, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _profile_to_read(profile: UserProfile) -> ProfileRead:
    restrictions = []
    for umr in profile.medical_restrictions:
        r = umr.restriction
        restrictions.append(
            MedicalRestrictionRead(id=str(r.id), name=r.name, description=r.description)
        )

    return ProfileRead(
        id=str(profile.id),
        first_name=profile.first_name,
        last_name=profile.last_name,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        experience_level=profile.experience_level,
        goal=profile.goal,
        sport_type=profile.sport_type,
        activity_level=profile.activity_level,
        target_weight_kg=profile.target_weight_kg,
        equipment_available=profile.equipment_available,
        training_days_per_week=profile.training_days_per_week,
        meals_per_day=profile.meals_per_day,
        food_allergies=profile.food_allergies,
        disliked_foods=profile.disliked_foods,
        custom_health_notes=profile.custom_health_notes,
        medical_restrictions=restrictions,
    )


@router.get("/me", response_model=ProfileRead)
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Profile")
    return _profile_to_read(profile)


@router.put("/me", response_model=ProfileRead)
async def create_or_update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    update_data = data.model_dump(exclude={"medical_restriction_ids"}, exclude_unset=True)

    if profile:
        for field, value in update_data.items():
            setattr(profile, field, value)
    else:
        profile = UserProfile(
            user_id=user.id,
            **update_data,
        )
        db.add(profile)
        await db.flush()

    # Handle medical restrictions
    if data.medical_restriction_ids is not None:
        # Remove existing
        existing = await db.execute(
            select(UserMedicalRestriction).where(
                UserMedicalRestriction.user_profile_id == profile.id
            )
        )
        for umr in existing.scalars():
            await db.delete(umr)

        # Add new
        for rid in data.medical_restriction_ids:
            umr = UserMedicalRestriction(
                user_profile_id=profile.id,
                medical_restriction_id=rid,
            )
            db.add(umr)

    await db.flush()
    await db.refresh(profile)
    return _profile_to_read(profile)


@router.get("/medical-restrictions", response_model=list[MedicalRestrictionRead])
async def list_medical_restrictions(
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(select(MedicalRestriction))
    return [
        MedicalRestrictionRead(id=str(r.id), name=r.name, description=r.description)
        for r in result.scalars()
    ]
