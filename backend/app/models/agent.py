import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_model import BaseModel


class AgentToolCall(BaseModel):
    """Audit log of every agent tool invocation, plus pending state for write
    proposals that need user approval before execution."""

    __tablename__ = "agent_tool_calls"
    __table_args__ = (
        Index("ix_agent_tool_calls_user_created", "user_id", "created_at"),
        Index("ix_agent_tool_calls_conversation", "conversation_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String(60), nullable=False)
    arguments: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_proposal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pending_messages: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
