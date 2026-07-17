"""
Constitution management endpoints with live preview and audit history.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.workspace import WorkspaceManager, DEFAULT_CONSTITUTION
from api.dependencies import get_current_user, require_role
from agents.council.council import AetherionCouncil
from core.protocol import LLMWrapper

router = APIRouter(tags=["Council"])

workspace_manager = WorkspaceManager()


class ConstitutionUpdate(BaseModel):
    judges: Dict[str, Dict[str, Any]]
    thresholds: Dict[str, float]


class PreviewRequest(BaseModel):
    output: str
    goal: str
    constitution: Optional[Dict[str, Any]] = None


class AuditEntry(BaseModel):
    timestamp: float
    operator: str
    previous: Dict[str, Any]
    new: Dict[str, Any]


@router.get("/{workspace_id}")
async def get_constitution(
    workspace_id: str,
    user: dict = Depends(require_role("admin")),
):
    """Retrieve the current constitution for a workspace."""
    try:
        constitution = workspace_manager.get_constitution(workspace_id)
        return {"workspace_id": workspace_id, "constitution": constitution}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{workspace_id}")
async def update_constitution(
    workspace_id: str,
    update: ConstitutionUpdate,
    user: dict = Depends(require_role("admin")),
):
    """Update the constitution for a workspace."""
    constitution = {
        "judges": update.judges,
        "thresholds": update.thresholds,
    }
    operator = user.get("sub", user.get("email", "unknown"))
    success = workspace_manager.update_constitution(workspace_id, constitution, operator=operator)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"status": "updated", "workspace_id": workspace_id}


@router.get("/{workspace_id}/audit")
async def get_audit_log(
    workspace_id: str,
    limit: int = 50,
    user: dict = Depends(require_role("admin")),
):
    """Retrieve the audit history of constitution changes."""
    entries = workspace_manager.get_constitution_audit_log(workspace_id, limit)
    return {"workspace_id": workspace_id, "audit": entries}


@router.post("/preview")
async def preview_constitution(
    request: PreviewRequest,
    user: dict = Depends(require_role("admin")),
):
    """
    Test a constitution against sample output and goal.
    Returns the Council's verdict using the provided (or default) constitution.
    """
    constitution = request.constitution or DEFAULT_CONSTITUTION
    llm = LLMWrapper()
    council = AetherionCouncil(llm=llm)

    # Build weights from constitution
    weights = {
        name: config.get("weight", 1.0)
        for name, config in constitution["judges"].items()
        if config.get("enabled", True)
    }

    verdict = council.deliberate(
        request.output,
        request.goal,
        weights=weights,
        constitution=constitution,
    )

    return {
        "verdict": verdict["verdict"],
        "score": verdict["score"],
        "votes": verdict["votes"],
        "thresholds_used": constitution["thresholds"],
        "judges_enabled": [
            name for name, cfg in constitution["judges"].items()
            if cfg.get("enabled", True)
        ],
    }
