"""
Celery task definitions with fine‑grained progress tracking.
"""

import json
import time
import os
import redis
from celery import current_task
from api.celery_app import celery_app
from agents.governance.meta_orchestrator import MetaOrchestrator, TaskState
from core.task_state import TaskContext

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)


class ProgressTrackingOrchestrator(MetaOrchestrator):
    """Orchestrator that reports task state changes to Redis."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_id_for_progress = None

    def set_task_id(self, task_id: str):
        self.task_id_for_progress = task_id

    def _transition(self, new_state, context_update):
        # Call original transition
        ctx = super()._transition(new_state, context_update)

        # Report progress to Redis
        if self.task_id_for_progress:
            progress_key = f"task_progress:{self.task_id_for_progress}"
            elapsed = time.time() - self.start_time if self.start_time else 0
            redis_client.setex(
                progress_key,
                3600,  # expire after 1 hour
                json.dumps({
                    "state": new_state.name,
                    "elapsed": elapsed,
                    "updated_at": time.time()
                })
            )
        return ctx


@celery_app.task(bind=True, max_retries=3)
def run_pipeline_task(self, goal: str, mode: str = "pipeline", auth_token: str = None):
    """Execute a pipeline task with progress tracking."""
    orchestrator = ProgressTrackingOrchestrator()
    orchestrator.set_task_id(self.request.id)
    ctx = orchestrator.execute(goal, mode=mode, auth_token=auth_token)
    return {
        "task_id": ctx.task_id,
        "state": ctx.state.name,
        "council_verdict": ctx.council_verdict,
        "result": ctx.code_output or ctx.research_findings,
    }


@celery_app.task(bind=True, max_retries=2)
def run_lab_task(self, research_question: str, auth_token: str = None):
    """Execute a lab task with progress tracking."""
    orchestrator = ProgressTrackingOrchestrator()
    orchestrator.set_task_id(self.request.id)
    ctx = orchestrator.execute(research_question, mode="lab", auth_token=auth_token)
    return {
        "task_id": ctx.task_id,
        "state": ctx.state.name,
        "council_verdict": ctx.council_verdict,
        "result": ctx.code_output or ctx.research_findings,
    }
