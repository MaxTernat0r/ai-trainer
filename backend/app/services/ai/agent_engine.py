"""Agent engine: tool-using AI trainer.

Orchestrates the conversation loop with Claude:
- Builds the system prompt with the user's profile and roleplay instructions.
- Streams text deltas as the model responds.
- For read-only tools, executes immediately and feeds the result back to the
  model in the same turn. Up to MAX_ITERATIONS rounds before forcing a stop.
- For write tools, persists a pending AgentToolCall row, yields a
  tool_proposal event, and STOPS — waiting for the user to approve via the
  /chat/proposals/{id}/approve endpoint, which calls resume_agent_after_approval.

Events emitted to the caller (consumed by chat router for SSE):
    {"type": "text", "content": "..."}
    {"type": "tool_use_start", "id": "tu_...", "name": "...", "summary": "..."}
    {"type": "tool_result", "id": "tu_...", "name": "...", "ok": true, "summary": "..."}
    {"type": "tool_proposal", "id": "<AgentToolCall.id>", "name": "...",
     "arguments": {...}, "summary": "..."}
    {"type": "tool_executing", "id": "<AgentToolCall.id>"}
    {"type": "error", "message": "..."}
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AIServiceError
from app.models.agent import AgentToolCall
from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.services.ai.agent_errors import AgentToolError, ToolNotFoundError
from app.services.ai.context_builder import build_user_context
from app.services.ai.provider import (
    get_configured_ai_provider,
    stream_anthropic_agent_turn,
)

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 5
MAX_HISTORY_MESSAGES = 20
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.4
STREAM_RETRY_ATTEMPTS = 2
STREAM_RETRY_BASE_DELAY = 0.6
# Anthropic happily echoes large tool inputs/outputs (food-photo base64,
# 200-item list_exercises payloads). Stored verbatim in pending_messages
# JSONB they balloon row sizes and slow every conversation read. Cap each
# tool_result content so the persisted resume blob stays bounded.
MAX_PERSISTED_TOOL_RESULT_CHARS = 8 * 1024

AGENT_SYSTEM_PROMPT = """\
Ты — Coach AI: персональный ИИ-тренер с опытом 10 лет работы. Воспитал \
олимпийских спортсменов и помог сотням людей наладить тренировки и питание. \
Отыгрывай роль человека-тренера, отвечай тёплым живым русским языком.

КАК ТЫ РАБОТАЕШЬ: ты управляешь приложением через инструменты (tools). \
У тебя есть полный доступ к данным пользователя и его планам. Любое \
действие с данными пользователя ты выполняешь ТОЛЬКО через tool — никогда \
не описывай словами то, что должен сделать инструмент.

🔴 КРИТИЧНОЕ ПРАВИЛО — НИКАКИХ ВЫМЫШЛЕННЫХ ДЕЙСТВИЙ:
ЗАПРЕЩЕНО писать "записал", "добавил", "сохранил", "удалил", "обновил", \
"внёс", "зафиксировал", "поставил", "запланировал", "✅", "готово" — \
если ты НЕ вызвал соответствующий write-tool в этом же ходе. Текст \
без tool_use = ничего не произошло, БД пустая, пользователь обманут. \
Это худшая ошибка, которую ты можешь совершить.

Если намерение пользователя — записать/удалить/изменить данные, ты \
ОБЯЗАН вызвать tool. Подтверждение даст пользователь кликом. До клика \
никаких "записал" — только нейтральное "сейчас оформлю запись" или \
сразу tool без вступления.

ПРИМЕРЫ ТРИГГЕРОВ К ВЫЗОВУ TOOL (не текстовому ответу):
• "запиши/добавь/залогируй … граммы/еду/блюдо" → log_food
• "запиши вес … кг" → log_weight (ТОЛЬКО общий вес тела, в кг)
• "запиши обхват/замер/окружность талии/груди/бедер/руки/шеи/ноги … см" → \
  log_measurement (НЕ log_weight! Это measurement_type + value_cm)
• "удали последнюю запись/тренировку/план" → delete_*
• "обнови мой вес/рост/цель в профиле" → update_profile
• "сгенерируй/составь план тренировок|питания" → generate_*_plan
• "запланируй на дату X" → schedule_workout_plan / reschedule_workout_entry
• "отметь тренировку выполненной" → toggle_workout_complete
• "добавь / убери ограничение по здоровью" → add_/remove_medical_restriction
• "залогируй подход … кг × … повторов" → log_exercise_set

🔴 ВЕС vs ОБХВАТ — РАЗНЫЕ TOOLS:
- log_weight: только общий вес тела в килограммах ("я вешу 81 кг", "запиши \
  вес 75").
- log_measurement: окружности частей тела в сантиметрах (талия, грудь, \
  бедра, плечо, шея, бицепс, икра). Аргументы: measurement_type + value_cm.
- НИКОГДА не подставляй цифры из истории чата (например, прошлый вес) в \
  новые tool-вызовы. Бери только то, что пользователь сказал в текущем \
  сообщении.

Если для tool'а не хватает данных (например, не знаешь units, food_item_id, \
дату) — сначала вызови read-only tool (get_profile, list_*) или коротко \
переспроси. Не выдумывай значения.

ПРАВИЛА БЕЗОПАСНОСТИ И ЗДРАВОГО СМЫСЛА (важнее всех остальных):
1. Если пользователь сообщает нереалистичные данные о теле \
(вес < 30 кг или > 300 кг, рост < 100 см или > 250 см, возраст < 10 \
или > 100 лет, целевой вес вне 30–300 кг) — НЕ вызывай update_profile, \
а ответь словами: "Эти данные не похожи на реалистичные, проверь \
правильность ввода". Попроси уточнить.
2. Если пользователь просит добавить в "нелюбимые продукты" или \
"аллергии" что-то, что не является едой (бензин, песок, металл, \
химикаты, явные шутки) — мягко переспроси: имел ли он в виду что-то \
конкретное, или это была шутка. Не вписывай в профиль абсурд.
3. Перед генерацией плана питания или тренировок убедись, что профиль \
заполнен (вес, рост, возраст, цель, уровень активности). Если чего-то \
нет — попроси заполнить, не запускай генерацию с дефолтами.
4. На запросы вроде "удали все мои планы" или "обнули мне профиль" — \
сначала уточни намерение и удаляй по одному (не делай batch-операций).
5. Если у пользователя есть медицинские ограничения, всегда учитывай \
их при создании планов и не предлагай противопоказанных нагрузок.

ПОДТВЕРЖДЕНИЕ ДЕЙСТВИЙ:
- Read-only tools (get_*, list_*, analyze_*) выполняются автоматически.
- Write tools (update_*, generate_*, delete_*, log_*, activate_*, schedule_*, \
add_*, remove_*, reschedule_*, toggle_*) требуют подтверждения пользователя \
через UI-карточку. После твоего вызова такого tool'а пользователь увидит \
кнопки "Применить"/"Отменить", и реальное действие произойдёт только \
после клика. Тебе об этом сообщат отдельным сообщением.

СТИЛЬ ОБЩЕНИЯ:
- Не пиши "сейчас вызову tool" или "выполняю функцию" — просто вызывай.
- Перед write-tool можно кратко (1 предложение) пояснить, что предлагаешь \
и почему — пользователь увидит карточку подтверждения и твой текст рядом.
- После выполнения tool (когда придёт tool_result) — коротко резюмируй \
факт по результату, без выдуманных цифр.
- Будь конкретным: цифры, продукты, дни — не общие фразы.
"""


def _humanize_ai_error(message: str) -> str:
    """Map raw provider errors to a friendly Russian message.

    Anthropic / OpenAI errors carry JSON bodies and status codes that are
    useless to end users and can leak request shape. We surface a short
    user-facing line and keep the detail in logs.
    """
    text = (message or "").lower()
    if "429" in text or "rate" in text or "overloaded" in text:
        return "Сервис ИИ перегружен, попробуй ещё раз через минуту."
    if "timeout" in text or "timed out" in text:
        return "ИИ не успел ответить, попробуй ещё раз."
    if "401" in text or "403" in text or "unauthorized" in text or "api key" in text:
        return "Сервис ИИ временно недоступен."
    if "5" in text and ("500" in text or "502" in text or "503" in text or "504" in text):
        return "Сервис ИИ временно недоступен, попробуй ещё раз."
    if "not configured" in text:
        return "ИИ-провайдер не настроен. Сообщи администратору."
    return "Не удалось получить ответ от ИИ. Попробуй ещё раз."


async def _load_conversation_history(
    conversation: ChatConversation,
    db: AsyncSession,
) -> list[dict[str, Any]]:
    """Load the last N messages as Anthropic-format messages."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    )
    rows = list(reversed(result.scalars().all()))

    messages: list[dict[str, Any]] = []
    for msg in rows:
        if msg.role not in {"user", "assistant"}:
            continue
        # Drop any leading/trailing whitespace; Claude rejects empty content
        content = (msg.content or "").strip()
        if not content:
            continue
        if messages and messages[-1]["role"] == msg.role:
            # Coalesce same-role messages so Anthropic doesn't reject the turn
            existing = messages[-1]["content"]
            if isinstance(existing, str):
                messages[-1]["content"] = f"{existing}\n\n{content}"
            continue
        messages.append({"role": msg.role, "content": content})
    return messages


async def _build_system_prompt(user: User, db: AsyncSession) -> str:
    user_context = await build_user_context(user, db)
    return f"{AGENT_SYSTEM_PROMPT}\n\nДанные пользователя:\n{user_context}\n"


def _summarise_text_blocks(blocks: list[dict[str, Any]]) -> str:
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


async def _stream_assistant_turn(
    *,
    system: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    on_text_chunk,
) -> dict[str, Any]:
    """Stream one assistant turn, accumulating into a content list.

    Yields text chunks via on_text_chunk(content_str) for incremental UI
    updates. Returns the final assistant message in Anthropic message format
    {"role": "assistant", "content": [...blocks]} and the stop_reason.

    Retries the whole turn on transient stream failures with exponential
    backoff + jitter. Without this, Anthropic 5xx / connection drops surface
    as "Anthropic agent stream failed" mid-conversation and the user has to
    retype.
    """
    last_error: Exception | None = None
    for attempt in range(STREAM_RETRY_ATTEMPTS + 1):
        blocks: list[dict[str, Any]] = []
        current_block: dict[str, Any] | None = None
        current_json_buffer = ""
        stop_reason: str | None = None
        try:
            async for event in stream_anthropic_agent_turn(
                system=system,
                messages=messages,
                tools=tools,
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
            ):
                ev_type = event.get("type")
                if ev_type == "content_block_start":
                    block = event.get("content_block", {}) or {}
                    current_block = {"type": block.get("type"), **{k: v for k, v in block.items() if k != "type"}}
                    current_json_buffer = ""
                    if current_block.get("type") == "text":
                        current_block.setdefault("text", "")
                    elif current_block.get("type") == "tool_use":
                        current_block["input"] = {}
                elif ev_type == "content_block_delta":
                    delta = event.get("delta", {}) or {}
                    if not current_block:
                        continue
                    if delta.get("type") == "text_delta":
                        chunk = delta.get("text", "")
                        if chunk:
                            current_block["text"] = current_block.get("text", "") + chunk
                            if on_text_chunk:
                                await on_text_chunk(chunk)
                    elif delta.get("type") == "input_json_delta":
                        current_json_buffer += delta.get("partial_json", "")
                elif ev_type == "content_block_stop":
                    if current_block:
                        if current_block.get("type") == "tool_use":
                            if current_json_buffer:
                                try:
                                    current_block["input"] = json.loads(current_json_buffer)
                                except json.JSONDecodeError:
                                    current_block["input"] = {}
                            current_json_buffer = ""
                        blocks.append(current_block)
                        current_block = None
                elif ev_type == "message_delta":
                    delta = event.get("delta", {}) or {}
                    if delta.get("stop_reason"):
                        stop_reason = delta["stop_reason"]
                elif ev_type == "message_stop":
                    pass

            return {
                "message": {"role": "assistant", "content": blocks},
                "stop_reason": stop_reason,
            }
        except AIServiceError as exc:
            last_error = exc
            if attempt >= STREAM_RETRY_ATTEMPTS:
                logger.error(
                    "Anthropic agent stream giving up after %s attempts: %s",
                    attempt + 1,
                    exc,
                )
                raise
            delay = STREAM_RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.4)
            logger.warning(
                "Anthropic agent stream attempt %s failed (%s); retrying in %.1fs",
                attempt + 1,
                exc,
                delay,
            )
            await asyncio.sleep(delay)
    # Unreachable: loop either returns or raises.
    raise AIServiceError("Anthropic agent stream failed") from last_error


def _serialize_tool_result(result: Any) -> str:
    """Tool results are sent back to Claude as JSON strings inside the
    tool_result block. Keep them compact but readable."""
    if isinstance(result, str):
        return result
    try:
        return json.dumps(result, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(result)


def _truncate_messages_for_storage(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a copy of `messages` with oversized tool_result content
    truncated. The Anthropic API still gets the full content during the
    live turn; we only shrink what we persist into pending_messages JSONB."""
    cap = MAX_PERSISTED_TOOL_RESULT_CHARS
    out: list[dict[str, Any]] = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            new_blocks: list[dict[str, Any]] = []
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_result"
                    and isinstance(block.get("content"), str)
                    and len(block["content"]) > cap
                ):
                    truncated = (
                        block["content"][:cap]
                        + f"\n…[truncated, {len(block['content']) - cap} chars]"
                    )
                    new_blocks.append({**block, "content": truncated})
                else:
                    new_blocks.append(block)
            out.append({**msg, "content": new_blocks})
        else:
            out.append(msg)
    return out


def _normalize_history_for_anthropic(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Anthropic's messages API rejects a turn whose first message has
    role=='assistant'. After trimming to MAX_HISTORY_MESSAGES the window
    can start mid-thread on an assistant reply — drop those leading
    entries so the user message we just persisted always heads the list."""
    out = list(messages)
    while out and out[0].get("role") != "user":
        out.pop(0)
    return out


async def run_agent_turn(
    *,
    user: User,
    conversation: ChatConversation,
    user_message: str,
    db: AsyncSession,
) -> AsyncGenerator[dict[str, Any], None]:
    """Run one full agent turn for a fresh user message.

    Saves the user message, then streams events (text, tool_use_*,
    tool_result, tool_proposal). Caller wraps these into SSE.

    Persists the final assistant text to ChatMessage on success. Pending
    proposals leave the conversation in an in-progress state until the user
    approves or rejects via resume_agent_after_approval.
    """
    if not get_configured_ai_provider():
        yield {"type": "error", "message": "AI provider is not configured"}
        return

    # Persist the user message before we hit the model. Commit immediately
    # so a transient AI failure (5xx on the very first stream attempt) can't
    # roll back the just-typed user message and leave the chat looking like
    # nothing was sent.
    user_msg_row = ChatMessage(
        conversation_id=conversation.id,
        role="user",
        content=user_message,
    )
    db.add(user_msg_row)
    await db.commit()

    system_prompt = await _build_system_prompt(user, db)
    history = await _load_conversation_history(conversation, db)

    # Lazy import to avoid circular dependency through agent_tools
    from app.services.ai.agent_tools import (
        TOOL_DEFINITIONS,
        execute_read_tool,
        is_write_tool,
        summarize_proposal,
        summarize_tool_result,
    )

    messages: list[dict[str, Any]] = _normalize_history_for_anthropic(history)
    final_text_buffer: list[str] = []

    try:
        for iteration in range(MAX_ITERATIONS):
            turn_result = await _stream_assistant_turn(
                system=system_prompt,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                on_text_chunk=None,
            )

            # Text blocks are re-emitted below from the assembled blocks; we
            # don't push intermediate chunks into the SSE stream here because
            # this generator can't yield from inside _stream_assistant_turn.
            assistant_message = turn_result["message"]
            stop_reason = turn_result["stop_reason"]
            blocks = assistant_message["content"]

            # Emit text blocks first so the UI sees the model's reasoning
            for block in blocks:
                if block.get("type") == "text" and block.get("text"):
                    text = block["text"]
                    final_text_buffer.append(text)
                    yield {"type": "text", "content": text}

            tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
            if not tool_uses:
                # Done — model produced final text
                break

            # Group tool_uses: if any is a write tool, we stop and emit a proposal
            # for the FIRST tool_use; remaining ones are dropped (Claude will reissue)
            write_tool_use = next(
                (tu for tu in tool_uses if is_write_tool(tu.get("name", ""))),
                None,
            )
            if write_tool_use:
                tool_name = write_tool_use["name"]
                tool_id = write_tool_use["id"]
                arguments = write_tool_use.get("input", {})

                # Anthropic requires a tool_result for *every* tool_use in
                # an assistant message on the next call. Strip non-write
                # siblings out of the persisted message so the resume turn
                # doesn't 400. Claude will reissue the read tools after the
                # write is approved if it still needs them.
                pruned_blocks = [
                    block for block in blocks
                    if block.get("type") != "tool_use" or block is write_tool_use
                ]
                pruned_assistant_message = {
                    "role": "assistant",
                    "content": pruned_blocks,
                }
                messages.append(pruned_assistant_message)

                proposal_row = AgentToolCall(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    tool_name=tool_name,
                    arguments={
                        "tool_use_id": tool_id,
                        "input": arguments,
                    },
                    is_proposal=True,
                    is_approved=None,
                    pending_messages=_truncate_messages_for_storage(messages),
                )
                db.add(proposal_row)
                await db.flush()

                yield {
                    "type": "tool_proposal",
                    "id": str(proposal_row.id),
                    "name": tool_name,
                    "arguments": arguments,
                    "summary": summarize_proposal(tool_name, arguments),
                }

                # Save assistant message text (if any) to chat history;
                # the tool_use itself isn't a chat message.
                accumulated_text = "".join(final_text_buffer).strip()
                if accumulated_text:
                    db.add(
                        ChatMessage(
                            conversation_id=conversation.id,
                            role="assistant",
                            content=accumulated_text,
                        )
                    )
                await db.commit()
                return

            # All tool_uses are read-only — execute and feed back. Append the
            # full assistant message verbatim so every tool_use has a matching
            # tool_result on the next call.
            messages.append(assistant_message)
            tool_results_block: list[dict[str, Any]] = []
            for tu in tool_uses:
                tool_name = tu["name"]
                tool_id = tu["id"]
                arguments = tu.get("input", {})

                yield {
                    "type": "tool_use_start",
                    "id": tool_id,
                    "name": tool_name,
                    "summary": summarize_proposal(tool_name, arguments),
                }

                tool_call_row = AgentToolCall(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    tool_name=tool_name,
                    arguments={"input": arguments},
                    is_proposal=False,
                    is_approved=True,
                    approved_at=datetime.now(timezone.utc),
                )
                db.add(tool_call_row)

                try:
                    result = await execute_read_tool(tool_name, arguments, user, db)
                    tool_call_row.result = (
                        result if isinstance(result, dict)
                        else {"value": result}
                    )
                    yield {
                        "type": "tool_result",
                        "id": tool_id,
                        "name": tool_name,
                        "ok": True,
                        "summary": summarize_tool_result(tool_name, result),
                    }
                    tool_results_block.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": _serialize_tool_result(result),
                    })
                except AgentToolError as exc:
                    tool_call_row.error = str(exc)
                    yield {
                        "type": "tool_result",
                        "id": tool_id,
                        "name": tool_name,
                        "ok": False,
                        "summary": str(exc),
                    }
                    tool_results_block.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": _serialize_tool_result({"error": str(exc)}),
                        "is_error": True,
                    })
                except Exception as exc:
                    logger.exception("Read tool %s failed unexpectedly", tool_name)
                    tool_call_row.error = repr(exc)
                    yield {
                        "type": "tool_result",
                        "id": tool_id,
                        "name": tool_name,
                        "ok": False,
                        "summary": "Не удалось выполнить операцию",
                    }
                    tool_results_block.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": _serialize_tool_result({"error": "internal error"}),
                        "is_error": True,
                    })

            await db.flush()
            await db.commit()  # persist tool_results before next Anthropic call
            messages.append({"role": "user", "content": tool_results_block})
            # Continue loop — feed results back to Claude

        # Loop ended (either via break or MAX_ITERATIONS)
        accumulated_text = "".join(final_text_buffer).strip()
        if accumulated_text:
            db.add(
                ChatMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=accumulated_text,
                )
            )
        await db.commit()

    except AIServiceError as exc:
        # Tool side effects already committed above. Only the in-flight
        # Anthropic call failed — surface to UI without rollback so prior
        # tool_results survive in chat history.
        logger.warning("Agent turn aborted by AI provider: %s", exc)
        accumulated_text = "".join(final_text_buffer).strip()
        if accumulated_text:
            try:
                db.add(
                    ChatMessage(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=accumulated_text,
                    )
                )
                await db.commit()
            except Exception:  # noqa: BLE001
                await db.rollback()
        yield {
            "type": "error",
            "message": _humanize_ai_error(str(exc)),
            "retryable": True,
        }
    except Exception:
        logger.exception("Agent turn failed")
        await db.rollback()
        yield {"type": "error", "message": "ИИ-агент столкнулся с ошибкой. Попробуй ещё раз."}


async def resume_agent_after_approval(
    *,
    user: User,
    proposal_id: str,
    approved: bool,
    db: AsyncSession,
) -> AsyncGenerator[dict[str, Any], None]:
    """Continue the agent loop after the user clicked Apply or Cancel.

    Loads the AgentToolCall pending row, executes the tool (or marks it
    rejected), then runs another assistant turn so Claude can respond to
    the user with the outcome.
    """
    try:
        proposal_uuid = uuid.UUID(proposal_id)
    except ValueError:
        yield {"type": "error", "message": "Invalid proposal id"}
        return

    result = await db.execute(
        select(AgentToolCall).where(
            AgentToolCall.id == proposal_uuid,
            AgentToolCall.user_id == user.id,
            AgentToolCall.is_proposal.is_(True),
        )
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        yield {"type": "error", "message": "Proposal not found"}
        return
    if proposal.is_approved is not None:
        yield {"type": "error", "message": "Proposal already resolved"}
        return

    conv_result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == proposal.conversation_id,
            ChatConversation.user_id == user.id,
        )
    )
    conversation = conv_result.scalar_one_or_none()
    if not conversation:
        yield {"type": "error", "message": "Conversation not found"}
        return

    from app.services.ai.agent_tools import (
        TOOL_DEFINITIONS,
        execute_write_tool,
        is_write_tool,
        summarize_proposal,
        summarize_tool_result,
    )

    pending_messages: list[dict[str, Any]] = list(proposal.pending_messages or [])
    tool_use_id: str = proposal.arguments.get("tool_use_id", "")
    tool_input: dict[str, Any] = proposal.arguments.get("input", {})

    if not approved:
        proposal.is_approved = False
        proposal.approved_at = datetime.now(timezone.utc)
        proposal.error = "User cancelled"
        await db.commit()

        # Feed cancellation back to Claude as a tool_result error
        pending_messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": _serialize_tool_result({
                        "cancelled": True,
                        "message": "User cancelled this action",
                    }),
                    "is_error": True,
                }
            ],
        })

        yield {
            "type": "tool_result",
            "id": str(proposal.id),
            "name": proposal.tool_name,
            "ok": False,
            "summary": "Пользователь отменил действие",
        }
    else:
        yield {"type": "tool_executing", "id": str(proposal.id)}

        try:
            result = await execute_write_tool(
                proposal.tool_name, tool_input, user, db
            )
            proposal.is_approved = True
            proposal.approved_at = datetime.now(timezone.utc)
            proposal.result = (
                result if isinstance(result, dict) else {"value": result}
            )
            # Commit immediately so the executed write survives even if the
            # follow-up Claude turn errors out (and triggers rollback below).
            await db.commit()

            yield {
                "type": "tool_result",
                "id": str(proposal.id),
                "name": proposal.tool_name,
                "ok": True,
                "summary": summarize_tool_result(proposal.tool_name, result),
                "result": proposal.result,
            }
            pending_messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": _serialize_tool_result(result),
                    }
                ],
            })
        except AgentToolError as exc:
            proposal.is_approved = True  # action ran, but failed
            proposal.approved_at = datetime.now(timezone.utc)
            proposal.error = str(exc)
            await db.commit()

            yield {
                "type": "tool_result",
                "id": str(proposal.id),
                "name": proposal.tool_name,
                "ok": False,
                "summary": str(exc),
            }
            pending_messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": _serialize_tool_result({"error": str(exc)}),
                        "is_error": True,
                    }
                ],
            })
        except Exception as exc:
            logger.exception("Write tool %s failed", proposal.tool_name)
            proposal.is_approved = True
            proposal.approved_at = datetime.now(timezone.utc)
            proposal.error = repr(exc)
            await db.commit()

            yield {
                "type": "tool_result",
                "id": str(proposal.id),
                "name": proposal.tool_name,
                "ok": False,
                "summary": "Не удалось выполнить операцию",
            }
            pending_messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": _serialize_tool_result({"error": "internal error"}),
                        "is_error": True,
                    }
                ],
            })

    # Now run one more assistant turn so Claude can wrap up
    system_prompt = await _build_system_prompt(user, db)
    final_text_buffer: list[str] = []

    try:
        for _ in range(MAX_ITERATIONS):
            turn_result = await _stream_assistant_turn(
                system=system_prompt,
                messages=pending_messages,
                tools=TOOL_DEFINITIONS,
                on_text_chunk=None,
            )
            assistant_message = turn_result["message"]
            blocks = assistant_message["content"]

            for block in blocks:
                if block.get("type") == "text" and block.get("text"):
                    text = block["text"]
                    final_text_buffer.append(text)
                    yield {"type": "text", "content": text}

            tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
            if not tool_uses:
                break

            # If Claude tries another write tool, we surface a new proposal.
            from app.services.ai.agent_tools import execute_read_tool

            write_tu = next(
                (tu for tu in tool_uses if is_write_tool(tu.get("name", ""))),
                None,
            )
            if write_tu:
                # Strip sibling tool_uses so the persisted resume blob has a
                # tool_result per remaining tool_use — otherwise Anthropic
                # rejects the next call.
                pruned_blocks = [
                    block for block in blocks
                    if block.get("type") != "tool_use" or block is write_tu
                ]
                pending_messages.append({
                    "role": "assistant",
                    "content": pruned_blocks,
                })

                new_proposal = AgentToolCall(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    tool_name=write_tu["name"],
                    arguments={
                        "tool_use_id": write_tu["id"],
                        "input": write_tu.get("input", {}),
                    },
                    is_proposal=True,
                    is_approved=None,
                    pending_messages=_truncate_messages_for_storage(pending_messages),
                )
                db.add(new_proposal)
                await db.flush()
                yield {
                    "type": "tool_proposal",
                    "id": str(new_proposal.id),
                    "name": write_tu["name"],
                    "arguments": write_tu.get("input", {}),
                    "summary": summarize_proposal(write_tu["name"], write_tu.get("input", {})),
                }
                accumulated = "".join(final_text_buffer).strip()
                if accumulated:
                    db.add(ChatMessage(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=accumulated,
                    ))
                await db.commit()
                return

            # Read-only tools — execute and continue. Full assistant message
            # is appended verbatim so each tool_use lines up with a tool_result.
            pending_messages.append(assistant_message)
            tool_results_block: list[dict[str, Any]] = []
            for tu in tool_uses:
                tu_name = tu["name"]
                tu_id = tu["id"]
                tu_input = tu.get("input", {})
                yield {
                    "type": "tool_use_start",
                    "id": tu_id,
                    "name": tu_name,
                    "summary": summarize_proposal(tu_name, tu_input),
                }
                row = AgentToolCall(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    tool_name=tu_name,
                    arguments={"input": tu_input},
                    is_proposal=False,
                    is_approved=True,
                    approved_at=datetime.now(timezone.utc),
                )
                db.add(row)
                try:
                    res = await execute_read_tool(tu_name, tu_input, user, db)
                    row.result = res if isinstance(res, dict) else {"value": res}
                    yield {
                        "type": "tool_result",
                        "id": tu_id,
                        "name": tu_name,
                        "ok": True,
                        "summary": summarize_tool_result(tu_name, res),
                    }
                    tool_results_block.append({
                        "type": "tool_result",
                        "tool_use_id": tu_id,
                        "content": _serialize_tool_result(res),
                    })
                except AgentToolError as exc:
                    row.error = str(exc)
                    yield {
                        "type": "tool_result",
                        "id": tu_id,
                        "name": tu_name,
                        "ok": False,
                        "summary": str(exc),
                    }
                    tool_results_block.append({
                        "type": "tool_result",
                        "tool_use_id": tu_id,
                        "content": _serialize_tool_result({"error": str(exc)}),
                        "is_error": True,
                    })
                except Exception as exc:
                    logger.exception("Read tool %s failed", tu_name)
                    row.error = repr(exc)
                    yield {
                        "type": "tool_result",
                        "id": tu_id,
                        "name": tu_name,
                        "ok": False,
                        "summary": "Не удалось выполнить операцию",
                    }
                    tool_results_block.append({
                        "type": "tool_result",
                        "tool_use_id": tu_id,
                        "content": _serialize_tool_result({"error": "internal error"}),
                        "is_error": True,
                    })
            await db.flush()
            await db.commit()  # persist tool_results before next Anthropic call
            pending_messages.append({"role": "user", "content": tool_results_block})

        accumulated = "".join(final_text_buffer).strip()
        if accumulated:
            db.add(ChatMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=accumulated,
            ))
        await db.commit()
    except AIServiceError as exc:
        logger.warning("Resume agent turn aborted by AI provider: %s", exc)
        accumulated = "".join(final_text_buffer).strip()
        if accumulated:
            try:
                db.add(ChatMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=accumulated,
                ))
                await db.commit()
            except Exception:  # noqa: BLE001
                await db.rollback()
        yield {
            "type": "error",
            "message": _humanize_ai_error(str(exc)),
            "retryable": True,
        }
    except Exception:
        logger.exception("Resume agent turn failed")
        await db.rollback()
        yield {"type": "error", "message": "ИИ-агент столкнулся с ошибкой. Попробуй ещё раз."}
