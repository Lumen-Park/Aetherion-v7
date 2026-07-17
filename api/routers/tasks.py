"""
Task execution endpoints with progress tracking.
"""

import json
import os
import redis
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.tasks.celery_tasks import run_pipeline_task, run_lab_task
from api.dependencies import get_current_user, require_role

router = APIRouter()
redis_client = redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))


class TaskRequest(BaseModel):
    goal: str
    mode: Optional[str] = "pipeline"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    council_verdict: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    cached: bool = False


class ProgressResponse(BaseModel):
    state: str
    elapsed: float
    updated_at: float
    estimated_remaining: int
    progress_percent: int


@router.post("/pipeline", response_model=TaskResponse)
async def run_pipeline(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
):
    """Enqueue a pipeline task and return the Celery task ID."""
    task = run_pipeline_task.delay(request.goal, request.mode, user.get("auth_token"))
    return TaskResponse(task_id=task.id, status="queued")


@router.get("/pipeline/{task_id}", response_model=TaskResponse)
async def get_pipeline_status(
    task_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve the status and result of a Celery task."""
    task = run_pipeline_task.AsyncResult(task_id)
    if task.state == "PENDING":
        return TaskResponse(task_id=task_id, status="pending")
    elif task.state == "STARTED":
        return TaskResponse(task_id=task_id, status="running")
    elif task.state == "SUCCESS":
        result = task.result
        return TaskResponse(
            task_id=task_id,
            status="completed",
            council_verdict=result.get("council_verdict"),
            result=result.get("result"),
        )
    elif task.state == "FAILURE":
        return TaskResponse(
            task_id=task_id,
            status="failed",
            result=str(task.info) if task.info else "Unknown error",
        )
    elif task.state == "RETRY":
        return TaskResponse(task_id=task_id, status="retrying")
    else:
        return TaskResponse(task_id=task_id, status=task.state)


@router.get("/pipeline/{task_id}/progress", response_model=ProgressResponse)
async def get_task_progress(
    task_id: str,
    user: dict = Depends(get_current_user),
):
    """Return fine‑grained progress of a pipeline task."""
    progress_key = f"task_progress:{task_id}"
    data = redis_client.get(progress_key)
    if not data:
        raise HTTPException(status_code=404, detail="Progress not available")
    progress = json.loads(data)

    # Estimated total time based on historical averages (can be tuned)
    state_durations = {
        "QUEUED": 0,
        "REFINING": 10,
        "CURATING": 15,
        "RESEARCHING": 60,
        "DEVELOPING": 90,
        "REVIEWING": 20,
        "TESTING": 30,
        "SANITIZING": 5,
        "FORENSICS": 10,
        "EDGE_CASES": 10,
        "EVALUATING": 20,
        "COUNCIL": 45,
        "HUMAN_REVIEW": 0,
        "APPROVED": 0,
        "REJECTED": 0,
        "REVISION": 0,
        "FAILED": 0,
        "DONE": 0,
    }

    total_estimate = sum(state_durations.values())
    elapsed = progress.get("elapsed", 0)
    current_state = progress["state"]
    state_names = list(state_durations.keys())
    if current_state in state_names:
        current_state_idx = state_names.index(current_state)
    else:
        current_state_idx = 0

    completed_estimate = sum(list(state_durations.values())[:current_state_idx])
    remaining = max(0, total_estimate - elapsed)
    percent = min(100, int((completed_estimate / total_estimate) * 100)) if total_estimate > 0 else 0

    return ProgressResponse(
        state=current_state,
        elapsed=elapsed,
        updated_at=progress["updated_at"],
        estimated_remaining=remaining,
        progress_percent=percent,
    )


@router.post("/lab", response_model=TaskResponse)
async def run_lab(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
):
    """Enqueue an experiment (lab) task."""
    task = run_lab_task.delay(request.goal, user.get("auth_token"))
    return TaskResponse(task_id=task.id, status="queued")


@router.get("/lab/{task_id}", response_model=TaskResponse)
async def get_lab_status(
    task_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve the status and result of a lab task."""
    task = run_lab_task.AsyncResult(task_id)
    if task.state == "SUCCESS":
        result = task.result
        return TaskResponse(
            task_id=task_id,
            status="completed",
            council_verdict=result.get("council_verdict"),
            result=result.get("result"),
        )
    elif task.state == "FAILURE":
        return TaskResponse(task_id=task_id, status="failed")
    else:
        return TaskResponse(task_id=task_id, status=task.state)


@router.post("/override/{task_id}")
async def override_task(
    task_id: str,
    reason: str,
    user: dict = Depends(require_role("admin")),
):
    """Apply human override to a rejected task (admin only)."""
    from agents.governance.meta_orchestrator import MetaOrchestrator
    from api.tasks.redis_state import RedisStateManager
    
    orchestrator = MetaOrchestrator()
    # Load task context from Redis
    ctx = RedisStateManager.load(task_id)
    if not ctx:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Restore context to orchestrator
    orchestrator.current_context = ctx
    orchestrator.state_manager.current_context = ctx
    
    success = orchestrator.accept_override(task_id, user.get("sub", "admin"), reason, auth_token=user.get("auth_token"))
    if not success:
        raise HTTPException(status_code=400, detail="Override failed")
    return {"status": "success", "task_id": task_id}
