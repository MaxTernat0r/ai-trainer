from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ConversationCreate(BaseModel):
    title: str | None = Field(None, max_length=200)


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)

    @field_validator("content")
    @classmethod
    def _strip_and_require(cls, v: str) -> str:
        stripped = (v or "").strip()
        if not stripped:
            raise ValueError("content must not be empty")
        return stripped


class ToolProposalApprove(BaseModel):
    approved: bool


class ChatMessageRead(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ToolCallRead(BaseModel):
    """Persisted record of a write-tool proposal so the chat history shows
    which actions were proposed, applied, cancelled, or failed even after a
    page reload."""

    id: str
    tool_name: str
    arguments: dict[str, Any]
    summary: str
    status: str  # "pending" | "approved" | "rejected" | "error"
    result_summary: str | None = None
    error: str | None = None
    created_at: datetime


class ConversationRead(BaseModel):
    id: str
    title: str | None = None
    is_active: bool
    created_at: datetime
    messages: list[ChatMessageRead] = []
    tool_calls: list[ToolCallRead] = []

    model_config = {"from_attributes": True}


class ConversationListRead(BaseModel):
    id: str
    title: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
