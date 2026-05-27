"""Shared validation constants and Literal types.

Single source of truth for ranges and enums used across:
- Pydantic schemas in app/schemas/*
- Agent tool input validation in app/services/ai/agent_tools.py
"""

from typing import Literal

# --- Numeric ranges ---

WEIGHT_KG_MIN = 30.0
WEIGHT_KG_MAX = 300.0

HEIGHT_CM_MIN = 100.0
HEIGHT_CM_MAX = 250.0

AGE_MIN = 10
AGE_MAX = 100

TRAINING_DAYS_MIN = 1
TRAINING_DAYS_MAX = 7

MEALS_PER_DAY_MIN = 2
MEALS_PER_DAY_MAX = 7

MEASUREMENT_CM_MIN = 10.0
MEASUREMENT_CM_MAX = 250.0

WORKOUT_WEEKS_MIN = 1
WORKOUT_WEEKS_MAX = 52

PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 128

# --- Enum literals ---

Gender = Literal["male", "female"]
Goal = Literal[
    "muscle_gain",
    "fat_loss",
    "endurance",
    "flexibility",
    "general_fitness",
]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
ActivityLevel = Literal[
    "sedentary",
    "light",
    "moderate",
    "active",
    "very_active",
]
SportType = Literal[
    "gym",
    "calisthenics",
    "running",
    "swimming",
    "martial_arts",
    "other",
]
EquipmentAvailable = Literal[
    "full_gym",
    "home_basic",
    "bodyweight",
    "outdoor",
]
MeasurementType = Literal[
    "chest",
    "waist",
    "hips",
    "thigh",
    "biceps",
    "neck",
    "forearm",
    "calf",
    "shoulders",
]
MealType = Literal["breakfast", "lunch", "dinner", "snack"]
Periodization = Literal["linear", "undulating", "block"]
