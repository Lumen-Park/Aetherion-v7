"""
Celery task definitions with live task migration and graceful shutdown.
"""

import json
import time
import os
import redis
from celery import current_task
from celery.exceptions import SoftTimeLimitExceeded
from api.celery_app import celery_app
from agents.governance.meta_orchestrator import MetaOrchestrator, TaskState
from api.tasks.redis_state import RedisStateManager

REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)


class MigrationEnabledOrchestrator(MetaOrchestrator):
    """
    Orchestrator that persists its TaskContext after every state transition,
    and handles graceful shutdown by saving state on SoftTimeLimitExceeded.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._migration_task_id = None

    def set_migration_task_id(self, task_id: str):
        self._migration_task_id = task_id

    def _transition(self, new_state, context_update):
        ctx = super()._transition(new_state, context_update)
        if self._migration_task_id:
            RedisStateManager.save(self._migration_task_id, ctx)
            # Update lightweight progress
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

    def execute(self, goal, mode=None, auth_token=None):
        """Execute with graceful shutdown handling."""
        try:
            return super().execute(goal, mode=mode, auth_token=auth_token)
        except SoftTimeLimitExceeded:
            # Celery sent us a warning – save state immediately
            if self._migration_task_id and self.current_context:
                RedisStateManager.save(self._migration_task_id, self.current_context)
                self.logger.warning(
                    f"Soft time limit exceeded for task {self._migration_task_id}. State saved."
                )
            raise  # Celery will handle the retry


@celery_app.task(bind=True, max_retries=3)
def run_pipeline_task(self, goal: str, mode: str = "pipeline", auth_token: str = None):
    """
    Execute a pipeline task with migration support and graceful shutdown.
    If the worker is restarted, the task resumes from the last saved state.
    """
    task_id = self.request.id
    orchestrator = MigrationEnabledOrchestrator()
    orchestrator.set_migration_task_id(task_id)

    # Try to resume from saved state if this is a retry
    saved_ctx = RedisStateManager.load(task_id)
    if saved_ctx and saved_ctx.state not in (TaskState.QUEUED, TaskState.DONE):
        orchestrator.current_context = saved_ctx
        orchestrator.state_manager.current_context = saved_ctx
        orchestrator.start_time = saved_ctx.updated_at  # approximate
        orchestrator.call_count = saved_ctx.retry_count  # rough
        ctx = orchestrator._execute_standard_pipeline(mode)
    else:
        ctx = orchestrator.execute(goal, mode=mode, auth_token=auth_token)

    # Clean up saved state on success
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
    if saved_ctx and saved_ctx.state not in (TaskState.QUEUED, TaskState.DONE):
        orchestrator.current_context = saved_ctx
        orchestrator.state_manager.current_context = saved_ctx
        orchestrator.start_time = saved_ctx.updated_at
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
