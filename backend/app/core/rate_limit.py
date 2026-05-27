"""Lightweight Redis-backed rate limiter for auth endpoints.

Falls back to a no-op if Redis is unavailable so a flaky cache cannot brick
login. Counters use a fixed window (per-IP, per-key) keyed by epoch seconds.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from fastapi import Request

from app.core.config import settings
from app.core.exceptions import RateLimitError

logger = logging.getLogger(__name__)

_redis_client = None
_redis_disabled = False


async def _get_redis():
    global _redis_client, _redis_disabled
    if _redis_disabled:
        return None
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as redis_async  # type: ignore

        client = redis_async.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        await client.ping()
        _redis_client = client
        return client
    except Exception as exc:  # pragma: no cover — best-effort
        logger.warning("Rate limiter disabled — Redis unavailable: %s", exc)
        _redis_disabled = True
        return None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def enforce(
    request: Request,
    *,
    bucket: str,
    limit: int,
    window_seconds: int,
    extra: Optional[str] = None,
) -> None:
    """Increment counter and raise RateLimitError if over the limit."""
    client = await _get_redis()
    if client is None:
        return  # fail-open if Redis is down

    ip = _client_ip(request)
    window = int(time.time()) // window_seconds
    key_parts = ["rl", bucket, ip, str(window)]
    if extra:
        key_parts.append(extra)
    key = ":".join(key_parts)

    try:
        async with client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            count, _ = await pipe.execute()
    except Exception as exc:  # pragma: no cover
        logger.warning("Rate limiter error, failing open: %s", exc)
        return

    if count > limit:
        raise RateLimitError()
