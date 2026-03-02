from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.user import User

GENDER_LABELS = {
    "male": "Мужской",
    "female": "Женский",
}

EXPERIENCE_LABELS = {
    "beginner": "Начинающий",
    "intermediate": "Средний",
    "advanced": "Продвинутый",
}

ACTIVITY_LABELS = {
    "sedentary": "Малоподвижный",
    "light": "Лёгкая активность",
    "moderate": "Умеренная активность",
    "active": "Высокая активность",
    "very_active": "Очень высокая активность",
}

GOAL_LABELS = {
    "muscle_gain": "Набор мышечной массы",
    "fat_loss": "Снижение веса",
    "endurance": "Выносливость",
    "flexibility": "Гибкость",
    "general_fitness": "Общая физическая форма",
}

SPORT_LABELS = {
    "gym": "Тренажёрный зал",
    "calisthenics": "Калистеника",
    "running": "Бег",
    "swimming": "Плавание",
    "martial_arts": "Единоборства",
    "other": "Другое",
}

EQUIPMENT_LABELS = {
    "full_gym": "Полный тренажёрный зал",
    "home_basic": "Дом (гантели, резинки)",
    "bodyweight": "Только своё тело",
    "outdoor": "Улица (турники, брусья)",
}


async def build_user_context(user: User, db: AsyncSession) -> str:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return "Пользователь ещё не заполнил профиль."

    age = None
    if profile.date_of_birth:
        today = date.today()
        age = today.year - profile.date_of_birth.year - (
            (today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day)
        )

    restrictions = []
    for umr in profile.medical_restrictions:
        r = umr.restriction
        restrictions.append(r.description or r.name)

    first_name = profile.first_name or "Неизвестно"
    last_name = profile.last_name or ""
    gender = GENDER_LABELS.get(profile.gender, profile.gender) if profile.gender else "не указан"
    experience = EXPERIENCE_LABELS.get(profile.experience_level, profile.experience_level)
    activity = ACTIVITY_LABELS.get(profile.activity_level, profile.activity_level) if profile.activity_level else "не указан"
    goal = GOAL_LABELS.get(profile.goal, profile.goal) if profile.goal else "не указана"
    sport = SPORT_LABELS.get(profile.sport_type, profile.sport_type) if profile.sport_type else "не указан"
    equipment = EQUIPMENT_LABELS.get(profile.equipment_available, profile.equipment_available) if profile.equipment_available else "не указано"
    target_weight = f"{profile.target_weight_kg} кг" if profile.target_weight_kg else "не указан"
    training_days = profile.training_days_per_week or "не указано"

    lines = [
        f"Сейчас ты работаешь с человеком {first_name} {last_name}. Его физиологические данные:",
        f"Пол - {gender}",
        f"Возраст - {age or 'неизвестен'} лет",
        f"Рост - {profile.height_cm or 'неизвестен'} см",
        f"Вес - {profile.weight_kg or 'неизвестен'} кг",
        f"Уровень подготовки - {experience}",
        f"Уровень активности - {activity}",
    ]

    if restrictions:
        lines.append("Медицинские ограничения: " + ", ".join(restrictions))
    else:
        lines.append("Медицинские ограничения: нет")

    if profile.custom_health_notes:
        lines.append(f"Дополнительные заметки о здоровье: {profile.custom_health_notes}")

    if profile.disliked_foods:
        lines.append(f"Не любит есть: {profile.disliked_foods}")
    else:
        lines.append("Не любит есть: не указано")

    if profile.food_allergies:
        lines.append(f"Аллергии на: {profile.food_allergies}")
    else:
        lines.append("Аллергии на: нет")

    lines.append("")
    lines.append(
        f"Его цель: {goal}, целевой вес - {target_weight}. "
        f"Занимается {sport}, доступное оборудование - {equipment}, "
        f"готов заниматься {training_days} дней в неделю."
    )

    if profile.meals_per_day:
        lines.append(f"Предпочитает {profile.meals_per_day} приёмов пищи в день.")

    return "\n".join(lines)
