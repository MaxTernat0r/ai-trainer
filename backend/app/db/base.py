# Import all models here so Alembic can detect them
from app.db.base_model import Base  # noqa: F401
from app.models.user import User, OAuthAccount, RefreshToken  # noqa: F401
from app.models.profile import UserProfile, MedicalRestriction, UserMedicalRestriction  # noqa: F401
from app.models.exercise import Exercise, MuscleGroup, Equipment, ExerciseMuscleGroup  # noqa: F401
from app.models.workout import WorkoutPlan, WorkoutSession, WorkoutExercise, ExerciseSet  # noqa: F401
from app.models.nutrition import NutritionPlan, Meal, MealItem, FoodItem, NutritionLog  # noqa: F401
from app.models.chat import ChatConversation, ChatMessage  # noqa: F401
from app.models.analytics import WeightLog, MeasurementLog  # noqa: F401
