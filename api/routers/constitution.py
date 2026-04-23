"""
Constitution management endpoints for enterprise customization.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from core.workspace import WorkspaceManager
from api.dependencies import get_current_user, require_role

router = APIRouter(prefix="/constitution", tags=["Constitution"])

# Global workspace manager instance (should be injected in production)
workspace_manager = WorkspaceManager()


class ConstitutionUpdate(BaseModel):
    judges: Dict[str, Dict[str, Any]]
    thresholds: Dict[str, float]


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
    success = workspace_manager.update_constitution(workspace_id, constitution)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"status": "updated", "workspace_id": workspace_id}
