"""
Celery application for distributed task execution.
"""

from celery import Celery
import os

celery_app = Celery(
    "aetherion",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,       # Hard timeout (10 minutes)
    task_soft_time_limit=540,  # Soft timeout (9 minutes)
    worker_prefetch_multiplier=1,  # Fair distribution
    task_acks_late=True,       # Retry on worker failure
)
