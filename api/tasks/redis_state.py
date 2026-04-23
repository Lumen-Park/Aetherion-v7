"""
Redis-backed persistence for TaskContext, enabling live task migration.
"""

import json
import time
import redis
import os
from typing import Optional
from core.task_state import TaskContext, TaskState

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)


class RedisStateManager:
    """Saves and loads TaskContext to/from Redis."""

    PREFIX = "task_state"
    TTL = 3600  # 1 hour

    @classmethod
    def _key(cls, task_id: str) -> str:
        return f"{cls.PREFIX}:{task_id}"

    @classmethod
    def save(cls, task_id: str, context: TaskContext):
        """Store the entire TaskContext as JSON."""
        data = context.__dict__.copy()
        # Convert enum to string
        data["state"] = data["state"].name
        # Convert non‑serializable fields if any (e.g., expert_panel is list)
        redis_client.setex(
            cls._key(task_id),
            cls.TTL,
            json.dumps(data, default=str)
        )

    @classmethod
    def load(cls, task_id: str) -> Optional[TaskContext]:
        """Load a previously saved TaskContext, or None."""
        raw = redis_client.get(cls._key(task_id))
        if not raw:
            return None
        data = json.loads(raw)
        # Rebuild TaskContext from dict
        data["state"] = TaskState[data["state"]]
        return TaskContext(**data)

    @classmethod
    def delete(cls, task_id: str):
        """Remove the saved state after task completion."""
        redis_client.delete(cls._key(task_id))
