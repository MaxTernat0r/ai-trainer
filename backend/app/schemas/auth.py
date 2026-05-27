from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.validators import PASSWORD_MAX_LEN, PASSWORD_MIN_LEN


def _lowercase_email(value):
    if isinstance(value, str):
        return value.strip().lower()
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)

    _norm_email = field_validator("email", mode="before")(_lowercase_email)

    @field_validator("password")
    @classmethod
    def _strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v) or not any(c.isalpha() for c in v):
            raise ValueError("password must contain both letters and digits")
        return v


class RegisterResponse(BaseModel):
    detail: str
    email: EmailStr
    requires_verification: bool = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    _norm_email = field_validator("email", mode="before")(_lowercase_email)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserBrief"


class UserBrief(BaseModel):
    id: str
    email: str
    is_verified: bool
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str | None = None
    email: EmailStr | None = None
    code: str | None = None

    _norm_email = field_validator("email", mode="before")(_lowercase_email)


class ResendVerificationRequest(BaseModel):
    email: EmailStr

    _norm_email = field_validator("email", mode="before")(_lowercase_email)


class MessageResponse(BaseModel):
    detail: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str | None = None
