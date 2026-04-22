from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from agents.governance.meta_orchestrator import MetaOrchestrator
from api.dependencies import get_current_user, require_role

router = APIRouter()

class TaskRequest(BaseModel):
    goal: str
    mode: Optional[str] = "pipeline"

class TaskResponse(BaseModel):
    task_id: str
    state: str
    council_verdict: Optional[Dict[str, Any]] = None
    result: Optional[str] = None

@router.post("/pipeline", response_model=TaskResponse)
async def run_pipeline(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
):
    orch = MetaOrchestrator()
    ctx = orch.execute(request.goal, mode=request.mode)
    return TaskResponse(
        task_id=ctx.task_id,
        state=ctx.state.name,
        council_verdict=ctx.council_verdict,
        result=ctx.code_output or ctx.research_findings,
    )

@router.post("/lab", response_model=TaskResponse)
async def run_lab(
    request: TaskRequest,
    user: dict = Depends(require_role("operator")),
):
    from main import lab_mode as lab_mode_func
    # Note: lab_mode currently prints to console; we'll adapt it to return context
    orch = MetaOrchestrator()
    # For now, reuse pipeline; full lab integration pending
    ctx = orch.execute(request.goal, mode="pipeline")
    return TaskResponse(
        task_id=ctx.task_id,
        state=ctx.state.name,
        council_verdict=ctx.council_verdict,
        result=ctx.code_output or ctx.research_findings,
    )

@router.post("/override/{task_id}")
async def override_task(
    task_id: str,
    reason: str,
    user: dict = Depends(require_role("admin")),
):
    orch = MetaOrchestrator()
    success = orch.accept_override(task_id, user.get("sub", "admin"), reason)
    if not success:
        raise HTTPException(status_code=400, detail="Override failed")
    return {"status": "success", "task_id": task_id}
