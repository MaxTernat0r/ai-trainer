from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: str
    email: str
    is_active: bool
    is_verified: bool
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    email: EmailStr | None = None
