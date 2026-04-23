"""
Celery task definitions with live task migration support.
"""

import json
import time
import os
import redis
from celery import current_task
from api.celery_app import celery_app
from agents.governance.meta_orchestrator import MetaOrchestrator, TaskState
from api.tasks.redis_state import RedisStateManager

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)


class MigrationEnabledOrchestrator(MetaOrchestrator):
    """
    Orchestrator that persists its TaskContext after every state transition,
    enabling another worker to resume the task if this one crashes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._migration_task_id = None

    def set_migration_task_id(self, task_id: str):
        self._migration_task_id = task_id

    def _transition(self, new_state, context_update):
        ctx = super()._transition(new_state, context_update)
        if self._migration_task_id:
            # Persist the full context to Redis
            RedisStateManager.save(self._migration_task_id, ctx)
            # Also update the lightweight progress
            progress_key = f"task_progress:{self._migration_task_id}"
            elapsed = time.time() - self.start_time if self.start_time else 0
            redis_client.setex(
                progress_key,
                3600,
                json.dumps({
                    "state": new_state.name,
                    "elapsed": elapsed,
                    "updated_at": time.time()
                })
            )
        return ctx


@celery_app.task(bind=True, max_retries=3)
def run_pipeline_task(self, goal: str, mode: str = "pipeline", auth_token: str = None):
    task_id = self.request.id
    orchestrator = MigrationEnabledOrchestrator()
    orchestrator.set_migration_task_id(task_id)

    saved_ctx = RedisStateManager.load(task_id)
    if saved_ctx and saved_ctx.state not in (TaskState.QUEUED, TaskState.DONE):
        orchestrator.current_context = saved_ctx
        orchestrator.state_manager.current_context = saved_ctx

    try:
        ctx = orchestrator.execute(goal, mode=mode, auth_token=auth_token)
    finally:
        # On success or graceful failure, clean up
        RedisStateManager.delete(task_id)

    return {
        "task_id": ctx.task_id,
        "state": ctx.state.name,
        "council_verdict": ctx.council_verdict,
        "result": ctx.code_output or ctx.research_findings,
    }


@celery_app.task(bind=True, max_retries=2)
def run_lab_task(self, research_question: str, auth_token: str = None):
    """Lab task with migration support."""
    task_id = self.request.id
    orchestrator = MigrationEnabledOrchestrator()
    orchestrator.set_migration_task_id(task_id)

    saved_ctx = RedisStateManager.load(task_id)
    if saved_ctx and saved_ctx.state != TaskState.QUEUED:
        orchestrator.current_context = saved_ctx
        orchestrator.state_manager.current_context = saved_ctx
        ctx = orchestrator._execute_standard_pipeline("lab")
    else:
        ctx = orchestrator.execute(research_question, mode="lab", auth_token=auth_token)

    RedisStateManager.delete(task_id)
    return {
        "task_id": ctx.task_id,
        "state": ctx.state.name,
        "council_verdict": ctx.council_verdict,
        "result": ctx.code_output or ctx.research_findings,
    }
