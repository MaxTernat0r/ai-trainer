"""Chat engine using OpenAI API with streaming.

Provides an async generator that yields response chunks from the OpenAI
streaming API. Maintains conversation context by loading recent messages
and the user's profile information.
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.services.ai.context_builder import build_user_context
from app.services.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """\
Ты являешься профессиональным фитнес-тренером со стажем работы в 10 лет. \
Воспитал много и олимпийских спортсменов, и просто помог людям влюбиться в спорт и похудеть. \
Отыгрывай его роль, отвечай как человек.
"""

MAX_HISTORY_MESSAGES = 20


async def _load_conversation_history(
    conversation: ChatConversation,
    db: AsyncSession,
) -> list[dict[str, str]]:
    """Load the last N messages from the conversation for context.

    Returns a list of message dicts in OpenAI format: {"role": ..., "content": ...}.
    """
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    )
    messages = result.scalars().all()

    # Reverse to chronological order
    messages = list(reversed(messages))

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]


async def generate_chat_response(
    user: User,
    conversation: ChatConversation,
    message: str,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """Generate a streaming chat response from the AI trainer.

    Builds the full message context including system prompt, user profile,
    conversation history, and the new user message. Streams the response
    back as an async generator yielding string chunks.

    The caller is responsible for saving the user message and the
    accumulated assistant response to the database.
    """
    try:
        # Build user context from profile
        user_context = await build_user_context(user, db)

        # Build the system message with user context
        system_message = (
            f"{CHAT_SYSTEM_PROMPT}\n"
            f"{user_context}\n\n"
            f"Ответь на вопрос пользователя как человек (фитнес-тренер), "
            f"учитывая данные о нём, максимально подробно."
        )

        # Load conversation history
        history = await _load_conversation_history(conversation, db)

        # Assemble the messages array
        messages = [{"role": "system", "content": system_message}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # Call OpenAI API with streaming
        client = get_openai_client()
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except AIServiceError:
        raise
    except Exception as e:
        logger.exception("Error during chat response generation")
        raise AIServiceError(f"Failed to generate chat response: {e}") from e
