"""
GDPR / CCPA compliance endpoints – data export, deletion, and consent.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from api.dependencies import require_role
from core.workspace import WorkspaceManager
import json
import io
import tarfile
import os

router = APIRouter(prefix="/compliance", tags=["Compliance"])
workspace_manager = WorkspaceManager()


@router.get("/export/{workspace_id}")
async def export_user_data(
    workspace_id: str,
    user: dict = Depends(require_role("admin")),
):
    """
    Download all data belonging to a workspace in a single archive.
    Satisfies GDPR Article 20 (right to data portability) and
    CCPA right to access.
    """
    try:
        # Collect workspace data
        constitution = workspace_manager.get_constitution(workspace_id)
        agents = workspace_manager.get_enabled_agents(workspace_id)
        audit = workspace_manager.get_constitution_audit_log(workspace_id, limit=9999)
        kg = workspace_manager.get_knowledge_graph(workspace_id)
        kg_entries = kg.query("*", n_results=9999)

        export_data = {
            "workspace_id": workspace_id,
            "constitution": constitution,
            "agents": agents,
            "audit_log": audit,
            "knowledge_graph": kg_entries,
        }

        # Build tar.gz in memory
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            info = tarfile.TarInfo(name="data.json")
            raw = json.dumps(export_data, indent=2, default=str).encode("utf-8")
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))

        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/x-gzip",
            headers={
                "Content-Disposition": f"attachment; filename=aetherion_export_{workspace_id}.tar.gz"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{workspace_id}")
async def delete_user_data(
    workspace_id: str,
    user: dict = Depends(require_role("admin")),
):
    """
    Permanently delete a workspace and all its data.
    Satisfies GDPR Article 17 (right to erasure) and CCPA deletion rights.
    """
    success = workspace_manager.delete_workspace(workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"status": "deleted", "workspace_id": workspace_id}


@router.post("/consent/{workspace_id}")
async def set_consent(
    workspace_id: str,
    consented: bool,
    user: dict = Depends(require_role("admin")),
):
    """
    Record whether the workspace owner has consented to data processing.
    """
    workspace_manager.set_consent(workspace_id, consented)
    return {"workspace_id": workspace_id, "consented": consented}


@router.get("/consent/{workspace_id}")
async def get_consent(
    workspace_id: str,
    user: dict = Depends(require_role("admin")),
):
    """
    Check the current consent status for a workspace.
    """
    consented = workspace_manager.has_consent(workspace_id)
    return {"workspace_id": workspace_id, "consented": consented}
