import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> dict:
    """Verify JWT and return payload. Raises JWTError on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def generate_refresh_token() -> str:
    return secrets.token_hex(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_email_verification_token() -> str:
    return secrets.token_urlsafe(48)


def hash_email_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_email_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_email_verification_code(user_id: str, code: str) -> str:
    normalized_code = "".join(char for char in code if char.isdigit())
    return hashlib.sha256(f"{user_id}:{normalized_code}".encode()).hexdigest()
