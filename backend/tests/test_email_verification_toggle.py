from types import SimpleNamespace
from unittest import TestCase
from uuid import uuid4

from app.core.config import settings
from app.routers import auth


class EmailVerificationToggleTest(TestCase):
    def setUp(self):
        self.original_required = settings.EMAIL_VERIFICATION_REQUIRED
        self.addCleanup(lambda: setattr(settings, "EMAIL_VERIFICATION_REQUIRED", self.original_required))

    def test_user_brief_reports_verified_when_email_verification_is_disabled(self):
        settings.EMAIL_VERIFICATION_REQUIRED = False
        user = SimpleNamespace(
            id=uuid4(),
            email="demo@example.com",
            is_verified=False,
            avatar_url=None,
        )

        brief = auth._user_brief(user)

        self.assertTrue(brief.is_verified)

    def test_user_brief_preserves_verification_status_when_required(self):
        settings.EMAIL_VERIFICATION_REQUIRED = True
        user = SimpleNamespace(
            id=uuid4(),
            email="demo@example.com",
            is_verified=False,
            avatar_url=None,
        )

        brief = auth._user_brief(user)

        self.assertFalse(brief.is_verified)
