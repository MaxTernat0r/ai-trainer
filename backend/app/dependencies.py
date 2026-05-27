import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmailNotVerifiedError
from app.core.config import settings
from app.core.security import verify_access_token
from app.db.session import get_async_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        try:
            user_uuid = uuid.UUID(str(user_id))
        except (ValueError, TypeError):
            # Tokens with malformed `sub` (non-UUID, e.g. truncated or from
            # a different schema) used to bubble up as a 500. Surface a
            # plain 401 instead so we don't leak stack traces to clients.
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    if settings.EMAIL_VERIFICATION_REQUIRED and not user.is_verified:
        raise EmailNotVerifiedError()

    return user
