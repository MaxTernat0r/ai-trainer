from unittest import IsolatedAsyncioTestCase

from app.core.exceptions import AIServiceError
from app.services.ai import food_recognizer


class FoodRecognizerFallbackTest(IsolatedAsyncioTestCase):
    async def test_ai_failure_returns_fallback_result(self):
        original_provider = food_recognizer.get_configured_ai_provider
        original_generate = food_recognizer.generate_vision_json
        food_recognizer.get_configured_ai_provider = lambda: "anthropic"

        async def fail_generation(*args, **kwargs):
            raise AIServiceError("vision failed")

        food_recognizer.generate_vision_json = fail_generation
        try:
            result = await food_recognizer.recognize_food_from_photo(b"not a real image")
        finally:
            food_recognizer.get_configured_ai_provider = original_provider
            food_recognizer.generate_vision_json = original_generate

        self.assertTrue(result.is_food)
        self.assertEqual(result.items[0].food_name, "Продукт с фото (уточните вручную)")
        self.assertGreater(result.total_calories, 0)
