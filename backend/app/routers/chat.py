from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
)

router = APIRouter(prefix="/chat", tags=["chat"])


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

    # Save user message
    user_msg = ChatMessage(
        conversation_id=conv.id,
        role="user",
        content=data.content,
    )
    db.add(user_msg)
    await db.flush()

    # Generate AI response (streaming)
    from app.services.ai.chat_engine import generate_chat_response

    async def event_stream():
        full_response = ""
        async for chunk in generate_chat_response(user, conv, data.content, db):
            full_response += chunk
            yield f"data: {chunk}\n\n"

        # Save assistant message
        assistant_msg = ChatMessage(
            conversation_id=conv.id,
            role="assistant",
            content=full_response,
        )
        db.add(assistant_msg)
        await db.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
