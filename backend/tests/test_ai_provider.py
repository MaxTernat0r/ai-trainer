import unittest

from app.core.config import settings
from app.services.ai.provider import get_anthropic_api_keys, get_configured_ai_provider


class AiProviderSelectionTest(unittest.TestCase):
    def setUp(self):
        self._old_values = {
            "AI_PROVIDER": settings.AI_PROVIDER,
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
            "ANTHROPIC_API_KEY_2": settings.ANTHROPIC_API_KEY_2,
            "ANTHROPIC_API_KEYS": settings.ANTHROPIC_API_KEYS,
        }

    def tearDown(self):
        for key, value in self._old_values.items():
            setattr(settings, key, value)

    def test_auto_provider_prefers_anthropic_when_key_is_present(self):
        settings.AI_PROVIDER = "auto"
        settings.OPENAI_API_KEY = "openai-key"
        settings.ANTHROPIC_API_KEY = "anthropic-key"
        settings.ANTHROPIC_API_KEY_2 = ""
        settings.ANTHROPIC_API_KEYS = ""

        self.assertEqual(get_configured_ai_provider(), "anthropic")

    def test_openai_remains_available_when_selected_explicitly(self):
        settings.AI_PROVIDER = "openai"
        settings.OPENAI_API_KEY = "openai-key"
        settings.ANTHROPIC_API_KEY = "anthropic-key"
        settings.ANTHROPIC_API_KEYS = ""

        self.assertEqual(get_configured_ai_provider(), "openai")

    def test_anthropic_keys_are_deduplicated(self):
        settings.ANTHROPIC_API_KEY = "anthropic-key"
        settings.ANTHROPIC_API_KEY_2 = "anthropic-key"
        settings.ANTHROPIC_API_KEYS = ""

        self.assertEqual(get_anthropic_api_keys(), ["anthropic-key"])


if __name__ == "__main__":
    unittest.main()
