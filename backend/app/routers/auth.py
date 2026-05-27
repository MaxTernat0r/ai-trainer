from datetime import datetime, timedelta, timezone
import logging

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import rate_limit
from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    EmailNotVerifiedError,
    EmailServiceError,
    UnauthorizedError,
)
from app.core.security import (
    create_access_token,
    generate_email_verification_code,
    generate_email_verification_token,
    hash_email_verification_code,
    generate_refresh_token,
    hash_email_verification_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_async_session
from app.models.user import EmailVerificationToken, RefreshToken, User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    TokenResponse,
    UserBrief,
    VerifyEmailRequest,
)
from app.services.email import EmailDeliveryError, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
VERIFICATION_RESEND_COOLDOWN_SECONDS = 60

# Pre-computed dummy hash so failed-lookup login still spends bcrypt time and
# attackers can't enumerate users by response latency.
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-equalization")


def _set_refresh_cookie(response: Response, raw_refresh: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )


def _user_brief(user: User) -> UserBrief:
    return UserBrief(
        id=str(user.id),
        email=user.email,
        is_verified=user.is_verified or not settings.EMAIL_VERIFICATION_REQUIRED,
        avatar_url=user.avatar_url,
    )


async def _issue_tokens(
    user: User,
    response: Response,
    db: AsyncSession,
) -> TokenResponse:
    access_token = create_access_token(str(user.id))
    raw_refresh = generate_refresh_token()

    refresh = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh)
    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(access_token=access_token, user=_user_brief(user))


async def _send_verification_email_background(to_email: str, verification_code: str) -> None:
    try:
        await send_verification_email(to_email, verification_code)
    except EmailDeliveryError:
        logger.exception("Could not send verification email to %s", to_email)


async def _send_verification_email_required(to_email: str, verification_code: str) -> None:
    try:
        await send_verification_email(to_email, verification_code)
    except EmailDeliveryError as exc:
        logger.exception("Could not send required verification email to %s", to_email)
        raise EmailServiceError("Не удалось отправить письмо подтверждения") from exc


async def _create_new_verification_code(user: User, db: AsyncSession) -> str:
    now = datetime.now(timezone.utc)
    await db.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw_code = generate_email_verification_code()
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_email_verification_code(str(user.id), raw_code),
            expires_at=now + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS),
        )
    )

    return raw_code


def _verification_recently_sent(token: EmailVerificationToken, now: datetime) -> bool:
    return token.created_at + timedelta(seconds=VERIFICATION_RESEND_COOLDOWN_SECONDS) > now


async def _latest_active_verification_token(user: User, db: AsyncSession) -> EmailVerificationToken | None:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at > now,
        )
        .order_by(EmailVerificationToken.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.post("/register", response_model=RegisterResponse)
async def register(
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    await rate_limit.enforce(
        request, bucket="register", limit=5, window_seconds=600
    )

    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        is_verified=not settings.EMAIL_VERIFICATION_REQUIRED,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ConflictError("Email already registered")

    if not settings.EMAIL_VERIFICATION_REQUIRED:
        await db.commit()
        return RegisterResponse(
            detail="Account created",
            email=user.email,
            requires_verification=False,
        )

    verification_code = await _create_new_verification_code(user, db)
    await _send_verification_email_required(user.email, verification_code)
    await db.commit()

    return RegisterResponse(
        detail="Verification email sent",
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_session),
):
    await rate_limit.enforce(
        request,
        bucket="login",
        limit=10,
        window_seconds=600,
        extra=data.email,
    )

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Equalize bcrypt time even when the account doesn't exist so the response
    # time can't be used to enumerate registered emails.
    candidate_hash = user.hashed_password if user and user.hashed_password else _DUMMY_PASSWORD_HASH
    password_ok = verify_password(data.password, candidate_hash)

    if not user or not user.hashed_password or not password_ok:
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    if settings.EMAIL_VERIFICATION_REQUIRED and not user.is_verified:
        raise EmailNotVerifiedError()

    return await _issue_tokens(user, response, db)


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(
    data: VerifyEmailRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_async_session),
):
    await rate_limit.enforce(
        request, bucket="verify-email", limit=20, window_seconds=600
    )

    now = datetime.now(timezone.utc)

    if data.token:
        token_hash = hash_email_verification_token(data.token)
        result = await db.execute(
            select(EmailVerificationToken)
            .where(
                EmailVerificationToken.token_hash == token_hash,
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > now,
            )
            .with_for_update()
            .limit(1)
        )
        verification_token = result.scalar_one_or_none()
    else:
        normalized_code = "".join(char for char in (data.code or "") if char.isdigit())
        if not data.email or len(normalized_code) != 6:
            raise BadRequestError("Invalid or expired verification code")

        user_lookup = await db.execute(select(User).where(User.email == data.email))
        user = user_lookup.scalar_one_or_none()
        if not user or not user.is_active:
            raise BadRequestError("Invalid or expired verification code")

        token_hash = hash_email_verification_code(str(user.id), normalized_code)
        result = await db.execute(
            select(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.token_hash == token_hash,
                EmailVerificationToken.used_at.is_(None),
                EmailVerificationToken.expires_at > now,
            )
            .with_for_update()
            .limit(1)
        )
        verification_token = result.scalar_one_or_none()

    if not verification_token:
        raise BadRequestError("Invalid or expired verification code")

    user_result = await db.execute(select(User).where(User.id == verification_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    user.is_verified = True
    verification_token.used_at = now
    await db.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.id != verification_token.id,
        )
        .values(used_at=now)
    )

    return await _issue_tokens(user, response, db)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    data: ResendVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    await rate_limit.enforce(
        request,
        bucket="resend-verification",
        limit=5,
        window_seconds=600,
        extra=data.email,
    )

    if not settings.EMAIL_VERIFICATION_REQUIRED:
        return MessageResponse(detail="Email verification is disabled")

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user and user.is_active and not user.is_verified:
        latest_token = await _latest_active_verification_token(user, db)
        if latest_token and _verification_recently_sent(latest_token, datetime.now(timezone.utc)):
            return MessageResponse(detail="If the account exists, a verification email has been sent")

        verification_code = await _create_new_verification_code(user, db)
        await _send_verification_email_required(user.email, verification_code)
        await db.commit()

    return MessageResponse(detail="If the account exists, a verification email has been sent")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    response: Response,
    db: AsyncSession = Depends(get_async_session),
):
    token_hash = hash_refresh_token(data.refresh_token)

    # Lock the row for the duration of the rotation so two concurrent
    # /refresh calls (e.g. two browser tabs) can't both observe is_revoked=False
    # and both succeed. The loser blocks until the leader commits, then sees
    # is_revoked=True and falls through to UnauthorizedError.
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )
    existing = result.scalar_one_or_none()

    if not existing:
        raise UnauthorizedError("Invalid or expired refresh token")

    # Reuse-detection: a second hit on an already-rotated token usually means
    # the cookie was stolen and replayed. Burn down all of the user's refresh
    # tokens so the attacker (and the legitimate user) have to log in again.
    if existing.is_revoked:
        logger.warning(
            "Refresh token reuse detected for user %s — revoking all tokens",
            existing.user_id,
        )
        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == existing.user_id,
                RefreshToken.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        await db.commit()
        raise UnauthorizedError("Invalid or expired refresh token")

    if existing.expires_at <= datetime.now(timezone.utc):
        raise UnauthorizedError("Invalid or expired refresh token")

    # Revoke old token (rotation)
    existing.is_revoked = True

    user_result = await db.execute(select(User).where(User.id == existing.user_id))
    user = user_result.scalar_one()

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    if settings.EMAIL_VERIFICATION_REQUIRED and not user.is_verified:
        raise EmailNotVerifiedError()

    return await _issue_tokens(user, response, db)


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_async_session),
):
    if refresh_token:
        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == hash_refresh_token(refresh_token),
                RefreshToken.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        await db.commit()

    response.delete_cookie(
        "refresh_token",
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return {"detail": "Logged out"}
