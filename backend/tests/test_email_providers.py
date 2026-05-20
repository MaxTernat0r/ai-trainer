from unittest import IsolatedAsyncioTestCase, TestCase
from email.message import EmailMessage

from app.core.config import settings
from app.services import email


class EmailSettingsMixin:
    email_setting_names = (
        "EMAIL_PROVIDER",
        "BREVO_API_KEY",
        "BREVO_SENDER_EMAIL",
        "BREVO_SENDER_NAME",
        "RESEND_API_KEY",
        "RESEND_FROM_EMAIL",
        "RESEND_FROM_NAME",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "SMTP_FROM_EMAIL",
        "SMTP_FROM_NAME",
        "SMTP_STARTTLS",
        "SMTP_TLS_SERVER_HOSTNAME",
    )

    def preserve_email_settings(self):
        original = {name: getattr(settings, name) for name in self.email_setting_names}
        self.addCleanup(lambda: [setattr(settings, name, value) for name, value in original.items()])


class EmailProviderSelectionTest(EmailSettingsMixin, TestCase):
    def setUp(self):
        self.preserve_email_settings()

    def test_auto_prefers_brevo_over_resend_and_smtp(self):
        settings.EMAIL_PROVIDER = "auto"
        settings.BREVO_API_KEY = "brevo-key"
        settings.RESEND_API_KEY = "resend-key"
        settings.SMTP_HOST = "smtp.example.com"
        settings.SMTP_FROM_EMAIL = "no-reply@example.com"

        self.assertEqual(email._select_email_provider(), "brevo")

    def test_auto_uses_resend_when_brevo_is_absent(self):
        settings.EMAIL_PROVIDER = "auto"
        settings.BREVO_API_KEY = ""
        settings.RESEND_API_KEY = "resend-key"

        self.assertEqual(email._select_email_provider(), "resend")

    def test_explicit_provider_wins_over_auto_detection(self):
        settings.EMAIL_PROVIDER = "smtp"
        settings.BREVO_API_KEY = "brevo-key"
        settings.RESEND_API_KEY = "resend-key"

        self.assertEqual(email._select_email_provider(), "smtp")


class FakeEmailApiResponse:
    status_code = 201
    text = '{"messageId":"test"}'

    def raise_for_status(self):
        return None


class FakeAsyncClient:
    last_request = None

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def post(self, url, headers, json):
        FakeAsyncClient.last_request = {
            "url": url,
            "headers": headers,
            "json": json,
            "timeout": self.timeout,
        }
        return FakeEmailApiResponse()


class EmailProviderDeliveryTest(EmailSettingsMixin, IsolatedAsyncioTestCase):
    def setUp(self):
        self.preserve_email_settings()
        self.original_async_client = email.httpx.AsyncClient
        email.httpx.AsyncClient = FakeAsyncClient
        self.addCleanup(lambda: setattr(email.httpx, "AsyncClient", self.original_async_client))

    async def test_send_verification_email_uses_brevo_payload(self):
        settings.EMAIL_PROVIDER = "brevo"
        settings.BREVO_API_KEY = "brevo-key"
        settings.BREVO_SENDER_EMAIL = "no-reply@example.com"
        settings.BREVO_SENDER_NAME = "AI Trainer"

        await email.send_verification_email("user@example.com", "123456")

        request = FakeAsyncClient.last_request
        self.assertEqual(request["url"], email.BREVO_TRANSACTIONAL_EMAIL_URL)
        self.assertEqual(request["headers"]["api-key"], "brevo-key")
        self.assertEqual(request["json"]["sender"]["email"], "no-reply@example.com")
        self.assertEqual(request["json"]["to"], [{"email": "user@example.com"}])
        self.assertIn("123456", request["json"]["textContent"])

    async def test_send_verification_email_uses_resend_payload(self):
        settings.EMAIL_PROVIDER = "resend"
        settings.RESEND_API_KEY = "resend-key"
        settings.RESEND_FROM_EMAIL = "no-reply@example.com"
        settings.RESEND_FROM_NAME = "AI Trainer"

        await email.send_verification_email("user@example.com", "654321")

        request = FakeAsyncClient.last_request
        self.assertEqual(request["url"], email.RESEND_EMAIL_URL)
        self.assertEqual(request["headers"]["authorization"], "Bearer resend-key")
        self.assertEqual(request["json"]["from"], "AI Trainer <no-reply@example.com>")
        self.assertEqual(request["json"]["to"], ["user@example.com"])
        self.assertIn("654321", request["json"]["text"])


class FakeSMTP:
    last_instance = None

    def __init__(self, host, port, timeout):
        self._host = host
        self.port = port
        self.timeout = timeout
        self.starttls_host = None
        FakeSMTP.last_instance = self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def starttls(self, context):
        self.starttls_host = self._host

    def login(self, user, password):
        self.user = user
        self.password = password

    def send_message(self, message):
        self.message = message


class SmtpDeliveryTest(EmailSettingsMixin, TestCase):
    def setUp(self):
        self.preserve_email_settings()
        self.original_smtp = email.smtplib.SMTP
        email.smtplib.SMTP = FakeSMTP
        self.addCleanup(lambda: setattr(email.smtplib, "SMTP", self.original_smtp))

    def test_smtp_tls_hostname_can_differ_from_connection_host(self):
        settings.SMTP_HOST = "172.18.0.1"
        settings.SMTP_PORT = 2525
        settings.SMTP_FROM_EMAIL = "sender@example.com"
        settings.SMTP_USER = "sender@example.com"
        settings.SMTP_PASSWORD = "app-password"
        settings.SMTP_STARTTLS = True
        settings.SMTP_TLS_SERVER_HOSTNAME = "smtp.gmail.com"

        message = EmailMessage()
        message["To"] = "user@example.com"
        email._send_message(message)

        smtp = FakeSMTP.last_instance
        self.assertEqual(smtp._host, "smtp.gmail.com")
        self.assertEqual(smtp.starttls_host, "smtp.gmail.com")
