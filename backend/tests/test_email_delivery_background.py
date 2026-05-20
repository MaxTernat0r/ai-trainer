from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from uuid import uuid4

import app.db.base  # noqa: F401
from app.routers import auth


class FakeSession:
    def __init__(self):
        self.added = []

    async def execute(self, statement):
        self.statement = statement

    def add(self, item):
        self.added.append(item)


class EmailDeliveryBackgroundTest(IsolatedAsyncioTestCase):
    async def test_create_verification_code_does_not_send_email_inline(self):
        original_sender = auth.send_verification_email
        auth.send_verification_email = AsyncMock()
        try:
            db = FakeSession()
            user = SimpleNamespace(id=uuid4(), email="user@example.com")

            verification_code = await auth._create_new_verification_code(user, db)

            auth.send_verification_email.assert_not_awaited()
            self.assertEqual(len(db.added), 1)
            self.assertRegex(verification_code, r"^\d{6}$")
        finally:
            auth.send_verification_email = original_sender

    async def test_background_email_delivery_logs_failure_without_raising(self):
        original_sender = auth.send_verification_email
        auth.send_verification_email = AsyncMock(side_effect=auth.EmailDeliveryError("smtp failed"))
        try:
            with self.assertLogs(auth.logger, level="ERROR") as logs:
                await auth._send_verification_email_background(
                    "user@example.com",
                    "123456",
                )

            auth.send_verification_email.assert_awaited_once()
            self.assertIn("Could not send verification email", logs.output[0])
        finally:
            auth.send_verification_email = original_sender

    async def test_required_email_delivery_raises_service_error_on_failure(self):
        original_sender = auth.send_verification_email
        auth.send_verification_email = AsyncMock(side_effect=auth.EmailDeliveryError("smtp failed"))
        try:
            with self.assertLogs(auth.logger, level="ERROR"):
                with self.assertRaises(auth.EmailServiceError):
                    await auth._send_verification_email_required("user@example.com", "123456")

            auth.send_verification_email.assert_awaited_once()
        finally:
            auth.send_verification_email = original_sender
