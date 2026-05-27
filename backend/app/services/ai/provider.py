import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.services.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


def get_anthropic_api_keys() -> list[str]:
    raw_keys = [
        *(key.strip() for key in settings.ANTHROPIC_API_KEYS.split(",") if key.strip()),
        settings.ANTHROPIC_API_KEY.strip(),
        settings.ANTHROPIC_API_KEY_2.strip(),
    ]
    keys: list[str] = []
    for key in raw_keys:
        if key and key not in keys:
            keys.append(key)
    return keys


def get_configured_ai_provider() -> str | None:
    provider = settings.AI_PROVIDER.strip().lower()
    has_openai = bool(settings.OPENAI_API_KEY.strip())
    has_anthropic = bool(get_anthropic_api_keys())

    if provider in {"anthropic", "claude"}:
        return "anthropic" if has_anthropic else None
    if provider == "openai":
        return "openai" if has_openai else None
    if provider == "auto":
        if has_anthropic:
            return "anthropic"
        if has_openai:
            return "openai"
        return None

    logger.warning("Unknown AI_PROVIDER=%s; falling back to auto provider selection", settings.AI_PROVIDER)
    if has_anthropic:
        return "anthropic"
    if has_openai:
        return "openai"
    return None


async def generate_json_completion(
    system_prompt: str,
    user_message: str,
    *,
    max_tokens: int,
    temperature: float,
) -> str:
    provider = get_configured_ai_provider()
    if provider == "anthropic":
        return await _create_anthropic_message(
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if provider == "openai":
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        if not content:
            raise AIServiceError("AI returned an empty response")
        return _extract_json_candidate(content)

    raise AIServiceError("AI provider is not configured")


async def generate_vision_json(
    prompt: str,
    image_base64: str,
    mime_type: str,
    *,
    max_tokens: int,
    temperature: float,
) -> str:
    provider = get_configured_ai_provider()
    if provider == "anthropic":
        return await _create_anthropic_message(
            system=None,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if provider == "openai":
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        if not content:
            raise AIServiceError("AI returned an empty response")
        return _extract_json_candidate(content)

    raise AIServiceError("AI provider is not configured")


async def stream_chat_completion(
    messages: list[dict[str, str]],
    *,
    max_tokens: int,
    temperature: float,
) -> AsyncGenerator[str, None]:
    provider = get_configured_ai_provider()
    if provider == "anthropic":
        system, anthropic_messages = _to_anthropic_messages(messages)
        async for text in _stream_anthropic_message(
            system=system,
            messages=anthropic_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        ):
            yield text
        return

    if provider == "openai":
        client = get_openai_client()
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
        return

    raise AIServiceError("AI provider is not configured")


async def _create_anthropic_message(
    *,
    system: str | None,
    messages: list[dict[str, Any]],
    max_tokens: int,
    temperature: float,
    tools: list[dict[str, Any]] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    if system:
        payload["system"] = system
    if tools:
        payload["tools"] = tools

    data = await _post_anthropic(payload)
    text = _extract_anthropic_text(data)
    if not text:
        raise AIServiceError("Anthropic returned an empty response")
    return _extract_json_candidate(text)


async def create_anthropic_agent_turn(
    *,
    system: str | None,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    """Send a turn with tool definitions and return the raw Anthropic response.

    The agent engine inspects content blocks (text vs. tool_use) to decide
    whether to execute a tool, surface a proposal, or yield text. Streaming
    is handled separately by stream_anthropic_agent_turn.
    """
    payload: dict[str, Any] = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
        "tools": tools,
    }
    if system:
        payload["system"] = system
    return await _post_anthropic(payload)


async def stream_anthropic_agent_turn(
    *,
    system: str | None,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    max_tokens: int,
    temperature: float,
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream an agent turn. Yields raw Anthropic SSE events as decoded dicts.

    Caller is expected to assemble text deltas, watch for tool_use blocks,
    and emit higher-level protocol events.

    Retries each available API key once on transient failure (HTTP 5xx,
    timeout, connection error). Logs the underlying status/exception on
    every attempt — silent failure was observed in production where the
    last-key error fell through without any context.
    """
    payload: dict[str, Any] = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
        "tools": tools,
        "stream": True,
    }
    if system:
        payload["system"] = system

    keys = get_anthropic_api_keys()
    if not keys:
        raise AIServiceError("Anthropic API key is not configured")

    last_error: Exception | None = None
    last_status: int | None = None
    last_body: str | None = None

    for index, api_key in enumerate(keys):
        try:
            async with httpx.AsyncClient(timeout=settings.ANTHROPIC_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    ANTHROPIC_MESSAGES_URL,
                    headers=_anthropic_headers(api_key),
                    json=payload,
                ) as response:
                    if response.status_code >= 400:
                        body_bytes = await response.aread()
                        last_status = response.status_code
                        last_body = body_bytes.decode("utf-8", errors="replace")[:1000]
                        logger.warning(
                            "Anthropic agent stream key #%s returned %s: %s",
                            index + 1,
                            last_status,
                            last_body,
                        )
                        last_error = AIServiceError(
                            f"Anthropic returned {last_status}"
                        )
                        continue
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        event_text = line.removeprefix("data: ").strip()
                        if not event_text or event_text == "[DONE]":
                            continue
                        try:
                            event = json.loads(event_text)
                        except json.JSONDecodeError:
                            continue
                        yield event
                        if event.get("type") == "error":
                            err_payload = event.get("error", {})
                            logger.warning(
                                "Anthropic agent stream key #%s emitted error: %s",
                                index + 1,
                                err_payload,
                            )
                            raise AIServiceError(
                                f"Anthropic stream error: {err_payload.get('type', 'unknown')}"
                            )
            return
        except AIServiceError as exc:
            last_error = exc
            logger.warning(
                "Anthropic agent stream key #%s aborted: %s",
                index + 1,
                exc,
            )
            continue
        except httpx.HTTPError as exc:
            last_error = exc
            logger.warning(
                "Anthropic agent stream key #%s transport error: %s: %s",
                index + 1,
                type(exc).__name__,
                exc,
            )
            continue
        except ValueError as exc:
            last_error = exc
            logger.warning(
                "Anthropic agent stream key #%s parse error: %s",
                index + 1,
                exc,
            )
            continue

    detail = (
        f"Anthropic agent stream failed: {last_status} {last_body}"
        if last_status is not None
        else f"Anthropic agent stream failed: {type(last_error).__name__ if last_error else 'unknown'}"
    )
    logger.error(detail)
    raise AIServiceError(detail) from last_error


async def _post_anthropic(payload: dict[str, Any]) -> dict[str, Any]:
    keys = get_anthropic_api_keys()
    if not keys:
        raise AIServiceError("Anthropic API key is not configured")

    last_error: Exception | None = None
    for index, api_key in enumerate(keys):
        try:
            async with httpx.AsyncClient(timeout=settings.ANTHROPIC_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    ANTHROPIC_MESSAGES_URL,
                    headers=_anthropic_headers(api_key),
                    json=payload,
                )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            last_error = exc
            logger.warning(
                "Anthropic request failed with status %s: %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            if index < len(keys) - 1:
                logger.warning("Anthropic request failed with key #%s; trying next key", index + 1)
                continue
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            if index < len(keys) - 1:
                logger.warning("Anthropic request failed with key #%s; trying next key", index + 1)
                continue

    raise AIServiceError("Anthropic request failed") from last_error


async def _stream_anthropic_message(
    *,
    system: str | None,
    messages: list[dict[str, Any]],
    max_tokens: int,
    temperature: float,
) -> AsyncGenerator[str, None]:
    payload: dict[str, Any] = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
        "stream": True,
    }
    if system:
        payload["system"] = system

    keys = get_anthropic_api_keys()
    if not keys:
        raise AIServiceError("Anthropic API key is not configured")

    last_error: Exception | None = None
    for index, api_key in enumerate(keys):
        try:
            async with httpx.AsyncClient(timeout=settings.ANTHROPIC_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    ANTHROPIC_MESSAGES_URL,
                    headers=_anthropic_headers(api_key),
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        event_text = line.removeprefix("data: ").strip()
                        if not event_text or event_text == "[DONE]":
                            continue
                        event = json.loads(event_text)
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {})
                            if delta.get("type") == "text_delta" and delta.get("text"):
                                yield delta["text"]
                        elif event.get("type") == "error":
                            raise AIServiceError("Anthropic stream returned an error")
            return
        except (httpx.HTTPError, ValueError, AIServiceError) as exc:
            last_error = exc
            if index < len(keys) - 1:
                logger.warning("Anthropic stream failed with key #%s; trying next key", index + 1)
                continue

    raise AIServiceError("Anthropic stream failed") from last_error


def _anthropic_headers(api_key: str) -> dict[str, str]:
    return {
        "anthropic-version": ANTHROPIC_VERSION,
        "x-api-key": api_key,
        "content-type": "application/json",
    }


def _extract_anthropic_text(data: dict[str, Any]) -> str:
    blocks = data.get("content", [])
    text_parts = [
        block.get("text", "")
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    return "".join(text_parts).strip()


def _extract_json_candidate(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    object_start = stripped.find("{")
    object_end = stripped.rfind("}")
    if object_start != -1 and object_end > object_start:
        return stripped[object_start : object_end + 1]

    array_start = stripped.find("[")
    array_end = stripped.rfind("]")
    if array_start != -1 and array_end > array_start:
        return stripped[array_start : array_end + 1]

    return stripped


def _to_anthropic_messages(
    messages: list[dict[str, str]],
) -> tuple[str | None, list[dict[str, str]]]:
    system_parts: list[str] = []
    converted: list[dict[str, str]] = []

    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        if role == "system":
            system_parts.append(content)
            continue
        if role not in {"user", "assistant"}:
            continue
        if converted and converted[-1]["role"] == role:
            converted[-1]["content"] = f"{converted[-1]['content']}\n\n{content}"
        else:
            converted.append({"role": role, "content": content})

    return "\n\n".join(system_parts) or None, converted
