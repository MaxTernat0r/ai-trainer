from datetime import datetime

from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    message: str


class ChatMessageRead(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: str
    title: str | None = None
    is_active: bool
    created_at: datetime
    messages: list[ChatMessageRead] = []

    model_config = {"from_attributes": True}


class ConversationListRead(BaseModel):
    id: str
    title: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
