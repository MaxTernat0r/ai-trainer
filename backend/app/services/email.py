import asyncio
from html import escape
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BREVO_TRANSACTIONAL_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
RESEND_EMAIL_URL = "https://api.resend.com/emails"
EMAIL_HTTP_TIMEOUT_SECONDS = 20


class EmailDeliveryError(RuntimeError):
    pass


def _select_email_provider() -> str:
    provider = settings.EMAIL_PROVIDER.strip().lower()
    if provider != "auto":
        return provider
    if settings.BREVO_API_KEY:
        return "brevo"
    if settings.RESEND_API_KEY:
        return "resend"
    return "smtp"


def _smtp_is_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_FROM_EMAIL)


def _brevo_sender_email() -> str:
    return settings.BREVO_SENDER_EMAIL or settings.SMTP_FROM_EMAIL


def _brevo_sender_name() -> str:
    return settings.BREVO_SENDER_NAME or settings.SMTP_FROM_NAME


def _resend_from_email() -> str:
    return settings.RESEND_FROM_EMAIL or settings.SMTP_FROM_EMAIL


def _resend_from_name() -> str:
    return settings.RESEND_FROM_NAME or settings.SMTP_FROM_NAME


def _build_verification_email_content(verification_code: str) -> tuple[str, str, str]:
    safe_verification_code = escape(verification_code, quote=True)
    subject = "Код подтверждения AI Trainer"
    text_content = (
        "Ваш код подтверждения AI Trainer:\n\n"
        f"{verification_code}\n\n"
        "Введите этот код на странице подтверждения email. Код действует ограниченное время.\n\n"
        "Если вы не регистрировались в AI Trainer, просто проигнорируйте это письмо."
    )
    html_content = f"""
    <html>
      <body>
        <p>Ваш код подтверждения AI Trainer:</p>
        <p style="font-size: 24px; font-weight: 700; letter-spacing: 4px;">{safe_verification_code}</p>
        <p>Введите этот код на странице подтверждения email. Код действует ограниченное время.</p>
        <p>Если вы не регистрировались в AI Trainer, просто проигнорируйте это письмо.</p>
      </body>
    </html>
    """
    return subject, text_content, html_content


def _send_message(message: EmailMessage) -> None:
    if not _smtp_is_configured():
        if settings.SMTP_REQUIRED:
            raise EmailDeliveryError("SMTP is not configured")
        logger.warning("SMTP is not configured; email was not sent to %s", message["To"])
        return

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as smtp:
            if settings.SMTP_STARTTLS:
                if settings.SMTP_TLS_SERVER_HOSTNAME:
                    smtp._host = settings.SMTP_TLS_SERVER_HOSTNAME  # noqa: SLF001
                smtp.starttls(context=ssl.create_default_context())
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except smtplib.SMTPException as exc:
        raise EmailDeliveryError("Could not send email") from exc
    except OSError as exc:
        raise EmailDeliveryError("Could not connect to SMTP server") from exc


async def _send_brevo_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str,
) -> None:
    sender_email = _brevo_sender_email()
    if not settings.BREVO_API_KEY or not sender_email:
        raise EmailDeliveryError("Brevo email provider is not configured")

    payload = {
        "sender": {"email": sender_email, "name": _brevo_sender_name()},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_content,
        "htmlContent": html_content,
    }
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=EMAIL_HTTP_TIMEOUT_SECONDS) as client:
            response = await client.post(BREVO_TRANSACTIONAL_EMAIL_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Brevo email API returned %s for %s: %s",
            exc.response.status_code,
            to_email,
            exc.response.text[:500],
        )
        raise EmailDeliveryError("Could not send email with Brevo") from exc
    except httpx.HTTPError as exc:
        raise EmailDeliveryError("Could not connect to Brevo email API") from exc


async def _send_resend_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str,
) -> None:
    from_email = _resend_from_email()
    if not settings.RESEND_API_KEY or not from_email:
        raise EmailDeliveryError("Resend email provider is not configured")

    payload = {
        "from": formataddr((_resend_from_name(), from_email)),
        "to": [to_email],
        "subject": subject,
        "text": text_content,
        "html": html_content,
    }
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {settings.RESEND_API_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=EMAIL_HTTP_TIMEOUT_SECONDS) as client:
            response = await client.post(RESEND_EMAIL_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Resend email API returned %s for %s: %s",
            exc.response.status_code,
            to_email,
            exc.response.text[:500],
        )
        raise EmailDeliveryError("Could not send email with Resend") from exc
    except httpx.HTTPError as exc:
        raise EmailDeliveryError("Could not connect to Resend email API") from exc


async def send_verification_email(to_email: str, verification_code: str) -> None:
    provider = _select_email_provider()
    subject, text_content, html_content = _build_verification_email_content(verification_code)

    if provider == "brevo":
        await _send_brevo_email(to_email, subject, text_content, html_content)
        return
    if provider == "resend":
        await _send_resend_email(to_email, subject, text_content, html_content)
        return
    if provider != "smtp":
        raise EmailDeliveryError(f"Unknown email provider: {provider}")

    if not _smtp_is_configured():
        if settings.SMTP_REQUIRED:
            raise EmailDeliveryError("SMTP is not configured")
        logger.warning("SMTP is not configured; verification code for %s: %s", to_email, verification_code)
        return

    from_email = settings.SMTP_FROM_EMAIL
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.SMTP_FROM_NAME, from_email))
    message["To"] = to_email
    message.set_content(text_content)
    message.add_alternative(html_content, subtype="html")

    await asyncio.to_thread(_send_message, message)
