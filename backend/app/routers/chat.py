from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

import app.db.base  # noqa: F401 — ensure all models are registered for relationships

from app.core.exceptions import NotFoundError
from app.db.session import get_async_session
from app.dependencies import get_current_user
from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageRead,
    ConversationCreate,
    ConversationListRead,
    ConversationRead,
    ToolProposalApprove,
)

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


@router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    data: ConversationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new conversation. Frontend sends {title: string|null} and expects
    a full Conversation response (with empty messages list)."""
    conversation = ChatConversation(user_id=user.id, title=data.title)
    db.add(conversation)
    await db.flush()
    return ConversationRead(
        id=str(conversation.id),
        title=conversation.title,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        messages=[],
    )


@router.get("/conversations", response_model=list[ConversationListRead])
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(ChatConversation)
        .where(ChatConversation.user_id == user.id)
        .order_by(ChatConversation.created_at.desc())
    )
    return [
        ConversationListRead(
            id=str(c.id),
            title=c.title,
            is_active=c.is_active,
            created_at=c.created_at,
        )
        for c in result.scalars()
    ]


@router.get("/conversations/{conv_id}", response_model=ConversationRead)
async def get_conversation(
    conv_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conv_id, ChatConversation.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise NotFoundError("Conversation")

    return ConversationRead(
        id=str(conv.id),
        title=conv.title,
        is_active=conv.is_active,
        created_at=conv.created_at,
        messages=[
            ChatMessageRead(
                id=str(m.id),
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in conv.messages
        ],
    )


@router.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conv_id, ChatConversation.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise NotFoundError("Conversation")
    await db.delete(conv)
    return {"detail": "Conversation deleted"}


@router.post("/conversations/{conv_id}/messages")
async def send_message(
    conv_id: str,
    data: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conv_id, ChatConversation.user_id == user.id
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise NotFoundError("Conversation")

    should_generate_title = conv.title is None or conv.title.strip() == ""
    if should_generate_title:
        fallback_title = data.content.strip().split("\n", 1)[0][:60].strip() or "Новый диалог"
        await db.execute(
            update(ChatConversation)
            .where(ChatConversation.id == conv.id)
            .values(title=fallback_title)
        )
        await db.flush()

    user_message_for_title = data.content
    from app.services.ai.agent_engine import run_agent_turn
    from app.services.ai.chat_engine import generate_conversation_title

    async def event_stream():
        try:
            async for event in run_agent_turn(
                user=user,
                conversation=conv,
                user_message=data.content,
                db=db,
            ):
                yield _sse(event)
        except Exception:
            logger.exception("Agent turn streaming failed")
            yield _sse({"type": "error", "message": "AI agent failed"})

        if should_generate_title:
            try:
                new_title = await generate_conversation_title(user_message_for_title)
                if new_title:
                    await db.execute(
                        update(ChatConversation)
                        .where(ChatConversation.id == conv.id)
                        .values(title=new_title)
                    )
                    await db.commit()
            except Exception:
                logger.warning("Failed to set conversation title", exc_info=True)

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(
    proposal_id: str,
    data: ToolProposalApprove,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Approve or reject a pending agent tool proposal. Streams the
    continuation of the agent turn (tool execution + Claude's followup)."""
    from app.services.ai.agent_engine import resume_agent_after_approval

    async def event_stream():
        try:
            async for event in resume_agent_after_approval(
                user=user,
                proposal_id=proposal_id,
                approved=data.approved,
                db=db,
            ):
                yield _sse(event)
        except Exception:
            logger.exception("Approval streaming failed")
            yield _sse({"type": "error", "message": "AI agent failed"})
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
