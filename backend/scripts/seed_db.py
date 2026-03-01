"""Database seeding script.

Usage: python -m scripts.seed_db
Run from the backend/ directory.
"""
import asyncio

from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.exercise import Equipment, Exercise, ExerciseMuscleGroup, MuscleGroup
from app.models.nutrition import FoodItem
from app.models.profile import MedicalRestriction
from app.seeds.seed_equipment import EQUIPMENT
from app.seeds.seed_exercises import EXERCISES
from app.seeds.seed_foods import FOODS
from app.seeds.seed_muscle_groups import MUSCLE_GROUPS

MEDICAL_RESTRICTIONS = [
    {"name": "lower_back_injury", "description": "Травма поясницы"},
    {"name": "shoulder_impingement", "description": "Импинджмент плеча"},
    {"name": "knee_injury", "description": "Травма колена"},
    {"name": "herniated_disc", "description": "Грыжа межпозвоночного диска"},
    {"name": "carpal_tunnel", "description": "Синдром запястного канала"},
    {"name": "high_blood_pressure", "description": "Повышенное артериальное давление"},
    {"name": "heart_condition", "description": "Заболевание сердца"},
    {"name": "asthma", "description": "Бронхиальная астма"},
    {"name": "diabetes", "description": "Сахарный диабет"},
    {"name": "pregnancy", "description": "Беременность"},
    {"name": "ankle_injury", "description": "Травма голеностопа"},
    {"name": "wrist_injury", "description": "Травма запястья"},
    {"name": "neck_injury", "description": "Травма шеи"},
    {"name": "hip_injury", "description": "Травма тазобедренного сустава"},
    {"name": "elbow_injury", "description": "Травма локтя"},
]


async def seed_all():
    async with async_session_factory() as session:
        # Seed muscle groups
        for mg_data in MUSCLE_GROUPS:
            existing = await session.execute(
                select(MuscleGroup).where(MuscleGroup.name == mg_data["name"])
            )
            if not existing.scalar_one_or_none():
                session.add(MuscleGroup(**mg_data))
        await session.commit()
        print(f"Seeded {len(MUSCLE_GROUPS)} muscle groups")

        # Seed equipment
        for eq_data in EQUIPMENT:
            existing = await session.execute(
                select(Equipment).where(Equipment.name == eq_data["name"])
            )
            if not existing.scalar_one_or_none():
                session.add(Equipment(**eq_data))
        await session.commit()
        print(f"Seeded {len(EQUIPMENT)} equipment items")

        # Seed medical restrictions
        for mr_data in MEDICAL_RESTRICTIONS:
            existing = await session.execute(
                select(MedicalRestriction).where(
                    MedicalRestriction.name == mr_data["name"]
                )
            )
            if not existing.scalar_one_or_none():
                session.add(MedicalRestriction(**mr_data))
        await session.commit()
        print(f"Seeded {len(MEDICAL_RESTRICTIONS)} medical restrictions")

        # Build lookup maps
        mg_result = await session.execute(select(MuscleGroup))
        mg_map = {mg.name: mg.id for mg in mg_result.scalars()}

        eq_result = await session.execute(select(Equipment))
        eq_map = {eq.name: eq.id for eq in eq_result.scalars()}

        # Seed exercises
        for ex_data in EXERCISES:
            existing = await session.execute(
                select(Exercise).where(Exercise.name == ex_data["name"])
            )
            if existing.scalar_one_or_none():
                continue

            equipment_id = (
                eq_map.get(ex_data.get("equipment_name"))
                if ex_data.get("equipment_name")
                else None
            )
            exercise = Exercise(
                name=ex_data["name"],
                name_ru=ex_data["name_ru"],
                description_ru=ex_data.get("description_ru"),
                instructions_ru=ex_data.get("instructions_ru"),
                difficulty=ex_data["difficulty"],
                exercise_type=ex_data["exercise_type"],
                equipment_id=equipment_id,
            )
            session.add(exercise)
            await session.flush()

            for muscle_name in ex_data.get("primary_muscles", []):
                if muscle_name in mg_map:
                    session.add(
                        ExerciseMuscleGroup(
                            exercise_id=exercise.id,
                            muscle_group_id=mg_map[muscle_name],
                            is_primary=True,
                        )
                    )

            for muscle_name in ex_data.get("secondary_muscles", []):
                if muscle_name in mg_map:
                    session.add(
                        ExerciseMuscleGroup(
                            exercise_id=exercise.id,
                            muscle_group_id=mg_map[muscle_name],
                            is_primary=False,
                        )
                    )

        await session.commit()
        print(f"Seeded {len(EXERCISES)} exercises")

        # Seed foods
        for food_data in FOODS:
            existing = await session.execute(
                select(FoodItem).where(FoodItem.name == food_data["name"])
            )
            if not existing.scalar_one_or_none():
                session.add(FoodItem(**food_data))
        await session.commit()
        print(f"Seeded {len(FOODS)} food items")

        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_all())
