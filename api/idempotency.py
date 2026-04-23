"""
Idempotency support using Redis.
"""

import hashlib
import json
from typing import Optional, Tuple
import redis
import os

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

IDEMPOTENCY_PREFIX = "idempotency"
DEFAULT_TTL_SECONDS = 86400  # 24 hours


def _make_key(key: str) -> str:
    """Create a namespaced Redis key."""
    return f"{IDEMPOTENCY_PREFIX}:{key}"


def get_cached_response(idempotency_key: str) -> Optional[dict]:
    """
    Retrieve a cached response for the given idempotency key.
    Returns None if not found.
    """
    cached = redis_client.get(_make_key(idempotency_key))
    if cached:
        return json.loads(cached)
    return None


def store_response(idempotency_key: str, response: dict, ttl: int = DEFAULT_TTL_SECONDS):
    """
    Store a response under the idempotency key with a TTL.
    """
    redis_client.setex(
        _make_key(idempotency_key),
        ttl,
        json.dumps(response)
    )


def require_idempotency_key(request_idempotency_key: Optional[str]) -> str:
    """
    Validate that an idempotency key is present and well‑formed.
    Returns the key if valid, raises HTTPException otherwise.
    """
    from fastapi import HTTPException
    if not request_idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required.")
    if len(request_idempotency_key) < 8 or len(request_idempotency_key) > 256:
        raise HTTPException(status_code=400, detail="Idempotency-Key must be between 8 and 256 characters.")
    return request_idempotency_key
