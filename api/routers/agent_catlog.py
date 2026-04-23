"""
Agent Catalog – browse, search, and enable/disable domain experts per workspace.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from core.workspace import WorkspaceManager
from agents.colleges.all_colleges import AGENT_REGISTRY
from api.dependencies import get_current_user, require_role

router = APIRouter(prefix="/agent-catalog", tags=["Agent Catalog"])
workspace_manager = WorkspaceManager()


class AgentCatalogUpdate(BaseModel):
    agents: Dict[str, bool]


@router.get("/{workspace_id}")
async def get_agent_catalog(
    workspace_id: str,
    user: dict = Depends(require_role("admin")),
):
    """Retrieve the agent catalog for a workspace with enable/disable states."""
    try:
        enabled = workspace_manager.get_enabled_agents(workspace_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Workspace not found")

    catalog = []
    for name, is_enabled in enabled.items():
        agent_cls = AGENT_REGISTRY.get(name)
        catalog.append({
            "name": name,
            "college": agent_cls.college if agent_cls else "Unknown",
            "expertise": agent_cls.expertise if agent_cls else "",
            "enabled": is_enabled
        })

    # Sort by college then name
    catalog.sort(key=lambda x: (x["college"], x["name"]))
    return {"workspace_id": workspace_id, "agents": catalog}


@router.put("/{workspace_id}")
async def update_agent_catalog(
    workspace_id: str,
    update: AgentCatalogUpdate,
    user: dict = Depends(require_role("admin")),
):
    """Update the enabled/disabled state of agents for a workspace."""
    success = workspace_manager.update_enabled_agents(workspace_id, update.agents)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"status": "updated", "workspace_id": workspace_id}
