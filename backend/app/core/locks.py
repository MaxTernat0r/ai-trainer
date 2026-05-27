"""Deterministic Postgres advisory-lock key helpers.

CPython randomises `hash()` of strings via PYTHONHASHSEED for security,
which means each uvicorn worker computes a different key for the same
input — making any pg_advisory_xact_lock built on top of `hash()` a
no-op across the worker pool. We use blake2b for a stable signed-int8
key instead.
"""

from __future__ import annotations

import hashlib


def advisory_key(*parts: str) -> int:
    """Return a deterministic signed 64-bit int suitable for pg_advisory_xact_lock.

    Stable across processes / Python invocations (unlike `hash()`).
    """
    digest = hashlib.blake2b(":".join(parts).encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big", signed=True)
