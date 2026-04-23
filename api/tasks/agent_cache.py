"""
Agent response cache backed by Redis.
"""

import hashlib
import json
import os
import redis
from typing import Optional, Dict, Any

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

CACHE_PREFIX = "agent_cache"
DEFAULT_TTL = int(os.getenv("AGENT_CACHE_TTL", "3600"))  # 1 hour


def _make_key(agent_name: str, goal: str) -> str:
    """Create a deterministic cache key from agent name and goal."""
    goal_hash = hashlib.sha256(goal.encode()).hexdigest()[:16]
    return f"{CACHE_PREFIX}:{agent_name}:{goal_hash}"


def get_cached_response(agent_name: str, goal: str) -> Optional[Dict[str, Any]]:
    """Retrieve a cached agent response, or None if not found."""
    key = _make_key(agent_name, goal)
    raw = redis_client.get(key)
    if raw:
        return json.loads(raw)
    return None


def cache_response(agent_name: str, goal: str, response: Dict[str, Any], ttl: int = None):
    """Store an agent response in the cache."""
    key = _make_key(agent_name, goal)
    redis_client.setex(key, ttl or DEFAULT_TTL, json.dumps(response))
