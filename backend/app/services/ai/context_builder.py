from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.user import User


async def build_user_context(user: User, db: AsyncSession) -> str:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return "User has not completed their profile yet."

    age = None
    if profile.date_of_birth:
        today = date.today()
        age = today.year - profile.date_of_birth.year - (
            (today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day)
        )

    restrictions = []
    for umr in profile.medical_restrictions:
        restrictions.append(umr.restriction.name)

    sections = []

    sections.append(f"""BASIC INFO:
- Name: {profile.first_name or 'Unknown'}
- Age: {age or 'unknown'} years
- Gender: {profile.gender or 'unknown'}
- Height: {profile.height_cm or 'unknown'} cm
- Weight: {profile.weight_kg or 'unknown'} kg""")

    sections.append(f"""TRAINING BACKGROUND:
- Experience level: {profile.experience_level}
- Primary sport: {profile.sport_type or 'general fitness'}
- Training days per week: {profile.training_days_per_week or 'not set'}
- Available equipment: {profile.equipment_available or 'not specified'}""")

    sections.append(f"""GOALS:
- Primary goal: {profile.goal or 'not set'}
- Target weight: {profile.target_weight_kg or 'not set'} kg
- Activity level: {profile.activity_level or 'not set'}""")

    if restrictions:
        restrictions_str = "\n".join(f"- {r}" for r in restrictions)
        sections.append(f"""MEDICAL RESTRICTIONS (CRITICAL - NEVER IGNORE):
{restrictions_str}""")

    return "\n\n".join(sections)
