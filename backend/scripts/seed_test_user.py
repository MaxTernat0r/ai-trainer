"""Создать тестового пользователя для Playwright-тестов мобильной адаптивности.

Запуск из backend/:
    python -m scripts.seed_test_user

Создаёт пользователя mobile-test@example.com с паролем mobile-test-pass-123,
ставит is_verified=True, заполняет профиль для прохождения onboarding gate.

Идемпотентен.

ЗАЩИТА ОТ ЗАПУСКА НА ПРОДЕ:
    Скрипт отказывается работать если settings.DEBUG=False, кроме случая
    когда задана переменная ALLOW_TEST_SEED=1. Это нужно чтобы случайный
    `docker compose run --rm backend python -m scripts.seed_test_user` на
    production VPS не создал юзера с известным паролем.
"""
import asyncio
import os
import sys
from datetime import date

from sqlalchemy import select

import app.db.base  # noqa: F401 — register all models for relationship resolution
from app.core.config import settings
from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.profile import UserProfile
from app.models.user import User

TEST_EMAIL = "mobile-test@example.com"
TEST_PASSWORD = "mobile-test-pass-123"


async def main() -> None:
    if not settings.DEBUG and os.getenv("ALLOW_TEST_SEED") != "1":
        print(
            "Refusing to seed test user: settings.DEBUG=False and ALLOW_TEST_SEED!=1.\n"
            "This script is for local Playwright tests only. Set ALLOW_TEST_SEED=1 to override.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == TEST_EMAIL))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=TEST_EMAIL,
                hashed_password=hash_password(TEST_PASSWORD),
                is_verified=True,
                is_active=True,
            )
            session.add(user)
            await session.flush()
            print(f"Created user {TEST_EMAIL}")
        else:
            user.hashed_password = hash_password(TEST_PASSWORD)
            user.is_verified = True
            user.is_active = True
            print(f"Updated user {TEST_EMAIL}")

        prof_result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        profile = prof_result.scalar_one_or_none()

        profile_data = dict(
            first_name="Mobile",
            last_name="Tester",
            date_of_birth=date(1995, 6, 15),
            gender="male",
            height_cm=180.0,
            weight_kg=80.0,
            goal="general_fitness",
            sport_type="gym",
            experience_level="intermediate",
            activity_level="moderate",
            training_days_per_week=3,
            equipment_available="full_gym",
            target_weight_kg=78.0,
            meals_per_day=3,
        )

        if profile is None:
            profile = UserProfile(user_id=user.id, **profile_data)
            session.add(profile)
            print("Created profile")
        else:
            for key, value in profile_data.items():
                setattr(profile, key, value)
            print("Updated profile")

        await session.commit()
        print(f"Test user ready. Email: {TEST_EMAIL}, password: {TEST_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
