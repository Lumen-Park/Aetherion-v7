"""
Celery task definitions for Aetherion pipelines.
"""

from api.celery_app import celery_app
from agents.governance.meta_orchestrator import MetaOrchestrator
import time


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_pipeline_task(self, goal: str, mode: str = "pipeline", auth_token: str = None):
    """
    Execute a pipeline task asynchronously.
    Automatically retries on failure up to 3 times.
    """
    try:
        orchestrator = MetaOrchestrator()
        ctx = orchestrator.execute(goal, mode=mode, auth_token=auth_token)
        return {
            "task_id": ctx.task_id,
            "state": ctx.state.name,
            "council_verdict": ctx.council_verdict,
            "result": ctx.code_output or ctx.research_findings,
        }
    except Exception as e:
        # Retry with exponential backoff (60s, 120s, 240s)
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_lab_task(self, research_question: str, auth_token: str = None):
    """
    Execute an experiment (lab) task asynchronously.
    """
    try:
        orchestrator = MetaOrchestrator()
        ctx = orchestrator.execute(research_question, mode="lab", auth_token=auth_token)
        return {
            "task_id": ctx.task_id,
            "state": ctx.state.name,
            "council_verdict": ctx.council_verdict,
            "result": ctx.code_output or ctx.research_findings,
        }
    except Exception as e:
        self.retry(exc=e)
