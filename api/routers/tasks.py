"""
Task execution endpoints with queuing and concurrency control.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from collections import deque
import asyncio
import time

from agents.governance.meta_orchestrator import MetaOrchestrator
from api.dependencies import get_current_user, require_role

router = APIRouter()

# =============================================================================
# Request Queuing and Concurrency Control
# =============================================================================

# Queue for pending pipeline tasks
task_queue = deque()
processing = False

# Limit concurrent pipeline executions (prevents resource exhaustion)
semaphore = asyncio.Semaphore(5)  # Max 5 concurrent tasks


async def process_queue():
    """Background worker that processes queued pipeline tasks."""
    global processing
    processing = True
    while task_queue:
        async with semaphore:
            task = task_queue.popleft()
            try:
                orchestrator = MetaOrchestrator()
                ctx = orchestrator.execute(
                    task["goal"],
                    mode=task["mode"],
                    auth_token=task.get("auth_token")
                )
                # Store result in a simple in‑memory cache (can be replaced with Redis)
                task_results[task["task_id"]] = {
                    "state": ctx.state.name,
                    "council_verdict": ctx.council_verdict,
                    "result": ctx.code_output or ctx.research_findings,
                }
            except Exception as e:
                task_results[task["task_id"]] = {
                    "state": "FAILED",
                    "error": str(e)
                }
            # Small delay to prevent tight loop
            await asyncio.sleep(0.1)
    processing = False


# In‑memory result storage (use Redis in production)
task_results: Dict[str, Dict] = {}


# =============================================================================
# Pydantic Models
# =============================================================================

class TaskRequest(BaseModel):
    goal: str
    mode: Optional[str] = "pipeline"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    council_verdict: Optional[Dict[str, Any]] = None
    result: Optional[str] = None


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/pipeline", response_model=TaskResponse)
async def run_pipeline(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_role("operator")),
):
    """Enqueue a pipeline task and return immediately with a task ID."""
    global processing

    task_id = f"task_{int(time.time())}"
    task_queue.append({
        "task_id": task_id,
        "goal": request.goal,
        "mode": request.mode,
        "auth_token": user.get("auth_token")  # Pass token if needed
    })

    if not processing:
        background_tasks.add_task(process_queue)

    return TaskResponse(task_id=task_id, status="queued")


@router.get("/pipeline/{task_id}", response_model=TaskResponse)
async def get_pipeline_status(task_id: str, user: dict = Depends(get_current_user)):
    """Retrieve the status and result of a previously queued pipeline task."""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    result = task_results[task_id]
    return TaskResponse(
        task_id=task_id,
        status=result.get("state", "unknown"),
        council_verdict=result.get("council_verdict"),
        result=result.get("result"),
    )


@router.post("/lab", response_model=TaskResponse)
async def run_lab(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
):
    """Run experiment mode synchronously (lab tasks are typically shorter)."""
    orchestrator = MetaOrchestrator()
    ctx = orchestrator.execute(request.goal, mode="lab")
    return TaskResponse(
        task_id=ctx.task_id,
        status=ctx.state.name,
        council_verdict=ctx.council_verdict,
        result=ctx.code_output or ctx.research_findings,
    )


@router.post("/override/{task_id}")
async def override_task(
    task_id: str,
    reason: str,
    user: dict = Depends(require_role("admin")),
):
    """Apply human override to a rejected task (admin only)."""
    orchestrator = MetaOrchestrator()
    success = orchestrator.accept_override(task_id, user.get("sub", "admin"), reason)
    if not success:
        raise HTTPException(status_code=400, detail="Override failed")
    return {"status": "success", "task_id": task_id}
