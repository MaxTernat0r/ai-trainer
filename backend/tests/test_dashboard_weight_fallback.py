from types import SimpleNamespace
from unittest import TestCase

from app.routers import analytics


class DashboardWeightFallbackTest(TestCase):
    def test_profile_weight_is_current_weight_until_first_logged_measurement(self):
        profile = SimpleNamespace(weight_kg=78.5)

        self.assertEqual(analytics._resolve_current_weight(None, profile), 78.5)

    def test_logged_weight_overrides_profile_weight(self):
        latest_weight = SimpleNamespace(weight_kg=76.2)
        profile = SimpleNamespace(weight_kg=78.5)

        self.assertEqual(analytics._resolve_current_weight(latest_weight, profile), 76.2)
