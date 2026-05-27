"""Chat engine using configured AI provider with streaming.

Provides an async generator that yields response chunks from the configured
AI provider. Maintains conversation context by loading recent messages and
the user's profile information.
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AIServiceError
from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.services.ai.context_builder import build_user_context
from app.services.ai.provider import get_configured_ai_provider, stream_chat_completion

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """\
Ты являешься профессиональным фитнес-тренером со стажем работы в 10 лет. \
Воспитал много и олимпийских спортсменов, и просто помог людям влюбиться в спорт и похудеть. \
Отыгрывай его роль, отвечай как человек.
"""

TITLE_SYSTEM_PROMPT = (
    "Ты помогаешь именовать чат с фитнес-тренером. "
    "На основе первого сообщения пользователя придумай очень короткий заголовок "
    "на русском языке: 3-6 слов, без кавычек, без точки в конце, в именительном падеже. "
    "Только сам заголовок, никакого вступления."
)

MAX_HISTORY_MESSAGES = 20


async def generate_conversation_title(first_message: str) -> str:
    """Generate a short title (3-6 words, Russian) for a conversation based on
    the first user message. Falls back to a truncation of the message if AI is
    not configured or generation fails."""
    fallback = first_message.strip().split("\n", 1)[0][:60].strip() or "Новый диалог"
    if not get_configured_ai_provider():
        return fallback
    try:
        accumulated = ""
        async for chunk in stream_chat_completion(
            messages=[
                {"role": "system", "content": TITLE_SYSTEM_PROMPT},
                {"role": "user", "content": first_message[:1000]},
            ],
            temperature=0.3,
            max_tokens=40,
        ):
            accumulated += chunk
        title = accumulated.strip().strip('"').strip("'").rstrip(".")
        # collapse whitespace, hard cap
        title = " ".join(title.split())[:80]
        return title or fallback
    except Exception:
        logger.warning("Failed to generate conversation title", exc_info=True)
        return fallback


def _build_fallback_chat_response(message: str) -> str:
    message_lower = message.lower()
    if any(word in message_lower for word in ["пит", "еда", "калор", "бжу"]):
        return (
            "Давай держать питание простым: в каждом основном приёме пищи "
            "собери источник белка, сложные углеводы и овощи. Для твоей цели "
            "лучше заранее планировать 3-4 приёма пищи, добирать белок в течение "
            "дня и не менять рацион резко. Если есть аллергии или продукты, которые "
            "ты не любишь, исключай их сразу и выбирай близкие аналоги."
        )
    if any(word in message_lower for word in ["техник", "упраж", "жим", "присед", "тяга"]):
        return (
            "По технике ориентируйся на три правила: стабильный корпус, контролируемая "
            "амплитуда и отсутствие боли. Начинай с разминочных подходов, снимай первое "
            "рабочее движение на видео сбоку и не увеличивай вес, пока движение не выглядит "
            "одинаково от первого до последнего повтора."
        )
    return (
        "Составь тренировку вокруг базовой схемы: разминка 7-10 минут, затем 4-6 упражнений "
        "по 3 подхода. Для набора мышц держи диапазон 8-12 повторений, отдых 60-120 секунд "
        "и добавляй нагрузку постепенно. Если есть ограничения по здоровью, выбирай варианты "
        "без боли и оставляй 1-2 повтора в запасе."
    )


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
        # Defence-in-depth: refuse anything that isn't a chat-shaped role.
        # The writer constrains role today, but a future buggy migration or
        # a row written by a tool path with role="system"/"tool" must not
        # be replayed as upstream system instructions.
        {"role": (msg.role if msg.role in {"user", "assistant"} else "user"),
         "content": msg.content}
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

        if not get_configured_ai_provider():
            logger.warning("AI provider is not configured; using fallback chat response")
            yield _build_fallback_chat_response(message)
            return

        stream = stream_chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        try:
            async for content in stream:
                yield content
        finally:
            # Make cancellation deterministic — if the SSE client disconnects
            # mid-response, close the upstream HTTP stream right away instead
            # of relying on GC to eventually release the socket.
            aclose = getattr(stream, "aclose", None)
            if aclose is not None:
                try:
                    await aclose()
                except Exception:  # noqa: BLE001
                    pass

    except AIServiceError:
        raise
    except Exception as e:
        logger.exception("Error during chat response generation")
        raise AIServiceError(f"Failed to generate chat response: {e}") from e
