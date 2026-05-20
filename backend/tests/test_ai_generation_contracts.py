import unittest

from app.services.ai.nutrition_generator import NUTRITION_SYSTEM_PROMPT
from app.services.ai.workout_generator import WORKOUT_SYSTEM_PROMPT


class AiGenerationContractsTest(unittest.TestCase):
    def test_workout_prompt_limits_weekly_template_size(self):
        self.assertIn("sessions — это шаблоны тренировочных дней недели", WORKOUT_SYSTEM_PROMPT)
        self.assertIn("НЕ создавай отдельные sessions для каждой недели", WORKOUT_SYSTEM_PROMPT)
        self.assertIn("не больше 5 упражнений", WORKOUT_SYSTEM_PROMPT)

    def test_nutrition_prompt_limits_meal_size(self):
        self.assertIn("Ровно столько meals", NUTRITION_SYSTEM_PROMPT)
        self.assertIn("не больше 4 продуктов", NUTRITION_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
