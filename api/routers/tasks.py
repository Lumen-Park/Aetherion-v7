from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.tasks.celery_tasks import run_pipeline_task, run_lab_task
from api.dependencies import get_current_user, require_role
from api.idempotency import (
    require_idempotency_key,
    get_cached_response,
    store_response,
)

router = APIRouter()


class TaskRequest(BaseModel):
    goal: str
    mode: Optional[str] = "pipeline"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    council_verdict: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    cached: bool = False  # Indicates if the response came from cache


@router.post("/pipeline", response_model=TaskResponse)
async def run_pipeline(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """Enqueue a pipeline task with idempotency protection."""
    key = require_idempotency_key(idempotency_key)

    # Check cache
    cached = get_cached_response(key)
    if cached:
        return TaskResponse(**cached, cached=True)

    # Not cached – submit new task
    task = run_pipeline_task.delay(request.goal, request.mode, user.get("auth_token"))
    response = TaskResponse(task_id=task.id, status="queued", cached=False)

    # Store in cache
    store_response(key, response.dict())

    return response


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


@router.post("/lab", response_model=TaskResponse)
async def run_lab(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    """Enqueue an experiment (lab) task with idempotency protection."""
    key = require_idempotency_key(idempotency_key)

    cached = get_cached_response(key)
    if cached:
        return TaskResponse(**cached, cached=True)

    task = run_lab_task.delay(request.goal, user.get("auth_token"))
    response = TaskResponse(task_id=task.id, status="queued", cached=False)
    store_response(key, response.dict())
    return response


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
    orchestrator = MetaOrchestrator()
    success = orchestrator.accept_override(task_id, user.get("sub", "admin"), reason)
    if not success:
        raise HTTPException(status_code=400, detail="Override failed")
    return {"status": "success", "task_id": task_id}
